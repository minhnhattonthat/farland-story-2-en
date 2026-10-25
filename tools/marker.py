"""marker.py: marker text for the phase-5 marker build (`build.py --marker`).

Every text run (text and {nl} between control codes) of every string becomes `[ADDR] The quick brown fox...`:
script boxes get full lines (px and lines from data/windows.json, else the box default), other strings one
marker line per Japanese line at the Japanese line's pixel width (16 px per full-width glyph, 8 per half-width),
so menus keep their layout. A second run in one string is `[ADDR.2]`. Control codes stay as they are; entries
flagged `notext` or `unused` keep their Japanese.

    python -X utf8 tools/marker.py [ID ..]     # print the marker text
    python -X utf8 tools/marker.py --check build/farland2_marker.sfc work/qa/marker   # Japanese left on screen
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import font

ROOT = Path(__file__).resolve().parents[1]
WINDOWS = ROOT / "data" / "windows.json"
CTRL = re.compile(r"(\{\w+(?::[0-9A-Fa-f]*)?\})")
BREAK = {"{nl}"}
FILLER = ("The quick brown fox jumps over the lazy dog. Pack my box with five dozen liquor jugs! "
          "How vexingly quick daft zebras jump? Sphinx of black quartz, judge my vow.").split()
BOX_DEFAULT = {"px": 143, "lines": 3, "last": 136}  # dialogue box (data/windows.json `box`)


def windows():
    return json.loads(WINDOWS.read_text(encoding="utf-8")) if WINDOWS.exists() else {}


def lines(head, px, n, w, last=None):
    """n lines of at most px pixels (the last one `last` px: the page-wait arrow): head, then filler words."""
    limit = lambda i: last if last and i == n - 1 else px  # noqa: E731
    out, cur, words = [], head, iter(FILLER * 4)
    for word in words:
        cand = f"{cur} {word}" if cur else word
        if font.text_width(cand, w) <= limit(len(out)):
            cur = cand
            continue
        out.append(cur)
        if len(out) == n:
            break
        cur = word if font.text_width(word, w) <= limit(len(out)) else ""
    else:
        out.append(cur)
    return out[:n]


def marker(e, win, w):
    tokens = [t for t in CTRL.split(e["jp"]) if t]
    box = win.get("box", {}).get(e["box"].split("/")[0], BOX_DEFAULT) if e.get("box") else None
    out, run, full, k = [], [], False, 0

    def flush():
        nonlocal k
        if not any(not CTRL.fullmatch(t) and t.strip("　") for t in run):
            out.extend(run)
            return
        k += 1
        head = f"[{e['addr']}{'' if k == 1 else f'.{k}'}]"
        if box:
            ls = lines(head, box["px"], box["lines"], w, box.get("last"))
        else:
            jp_lines = "".join(run).split("{nl}")
            ls = []
            for i, jl in enumerate(jp_lines):
                px = len(jl) * (16 if full else 8)
                ls.append(lines(head if i == 0 else "", max(px, font.text_width(head, w)), 1, w)[0] if jl else "")
        out.append("{nl}".join(ls))
        run.clear()

    for t in tokens:
        if CTRL.fullmatch(t) and t not in BREAK:
            flush()
            run.clear()
            out.append(t)
            full = {"{full}": True, "{half}": False}.get(t, full)
        else:
            run.append(t)
    flush()
    return "".join(out)


def fill(entries):
    win, w = windows(), font.widths()
    return [dict(e, en=e["en"] if e.get("notext") or e.get("unused") else marker(e, win, w)) for e in entries]


def check(tours, rom_path):
    """Strings a marker-build tour drew (tools/lua/textlog.lua) that still hold Japanese: text the extraction
    missed (or kept on purpose: notext/unused). Exit 1 if any."""
    import build
    from tbl import Table
    en = font.english_table()  # VWF words ($04xx) never collide with jp.tbl keys (kanji end at $0329)
    jp = Table([f"{k.hex().upper()}={'\\s' if v == ' ' else v}" for k, v in en.dec.items()]
               + (ROOT / "tbl" / "jp.tbl").read_text(encoding="utf-8").splitlines())
    rom = Path(rom_path).read_bytes()
    kana = re.compile(r"[぀-ヿ一-鿿]")
    pat = re.compile(r"str f(\d+) ([0-9A-F]{6}) .*?(?: buf=([0-9A-F]+))?$")
    bad = {}
    for log in sorted(p for t in tours for p in Path(t).glob("*/log.txt")):
        for line in log.read_text(encoding="utf-8", errors="replace").splitlines():
            if m := pat.match(line):
                p = int(m[2], 16)
                if m[3]:
                    b = bytes.fromhex(m[3])
                    text = jp.decode(b, 0, len(b))[0]
                else:
                    text = jp.decode(rom, p & 0x3FFFFF)[0]
                if kana.search(text):
                    bad.setdefault(f"{p:06X} {text[:60]}", log.parent.name)
    for k, scene in sorted(bad.items()):
        print(f"{scene:14} {k}")
    print(f"{len(bad)} drawn strings still Japanese")
    return 1 if bad else 0


def main():
    sys.path.insert(0, str(Path(__file__).parent))
    import build
    if sys.argv[1:2] == ["--check"]:
        sys.exit(check(sys.argv[3:], sys.argv[2]))
    ids = set(sys.argv[1:])
    for e in fill(build.load_script()):
        if not ids or e["id"] in ids:
            print(e["id"], e["en"])


if __name__ == "__main__":
    main()
