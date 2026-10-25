"""coverage.py: which script strings a tour on the English build showed (tools/lua/textlog.lua logs).

A string drawn from ROM is matched by its address in the build (relocated strings: build/<rom>.reloc.txt); one
drawn from a RAM buffer by the English text the buffer holds. Prints counts per file; `--missing F` writes the
ids of the box strings (upper/lower/centre) never shown, with their build address, for tools/lua/viewer.lua.

    python -X utf8 tools/coverage.py work/qa/p8/tour [more tour dirs] [--rom build/farland2_en.sfc] [--missing F]
"""
import argparse
import collections
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import build
import font

STR = re.compile(r"str f(\d+) ([0-9A-F]{6}) win=([0-9A-F]{2}) w=(\d+) h=(\d+) mode=([0-9A-F]{2})(?: buf=([0-9A-F]+))?")
CTRL = re.compile(r"\{[^}]*\}")


def strip(s):
    return CTRL.sub("", s).replace("　", "").replace(font.ZWSP, "")


def addresses(entries, rom):
    """{entry id: CPU address of its string in the build}."""
    reloc = {}
    path = Path(rom).with_suffix(".reloc.txt")
    if path.exists():
        for line in path.read_text().splitlines():
            o, n = line.split()
            reloc[int(o, 16)] = int(n, 16)
    out = {}
    for e in entries:
        a = build.cpu(int(e["addr"], 16))
        out[e["id"]] = reloc.get(a, a)
    return out


def shown(tours, rom):
    entries = build.load_script()
    by_addr = {a: i for i, a in addresses(entries, rom).items()}
    texts = [(e["id"], strip(e["en"])) for e in entries if e["en"] and len(strip(e["en"])) >= 3]
    en = font.english_table()
    seen = set()
    for log in sorted(p for t in tours for p in Path(t).rglob("log.txt")):
        for line in log.read_text(encoding="utf-8", errors="replace").splitlines():
            if m := STR.match(line):
                p = int(m[2], 16)
                if m[7]:
                    buf = strip(en.decode(bytes.fromhex(m[7]))[0])
                    seen.update(i for i, t in texts if t in buf)
                elif p in by_addr:
                    seen.add(by_addr[p])
    return seen


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("tours", nargs="+")
    ap.add_argument("--rom", default=str(build.OUT))
    ap.add_argument("--missing", help="write the unseen box strings: '<id> <build address>' per line")
    a = ap.parse_args()
    entries = [e for e in build.load_script() if not e.get("unused") and not e.get("notext")]
    seen = shown(a.tours, a.rom)
    per = collections.defaultdict(lambda: [0, 0])
    for e in entries:
        f = e["id"].split(".")[0]
        per[f][1] += 1
        per[f][0] += e["id"] in seen
    for f, (s, n) in sorted(per.items()):
        print(f"{f:12} {s:4}/{n:4}")
    box = [e for e in entries if e.get("box")]
    print(f"all {sum(e['id'] in seen for e in entries)}/{len(entries)}, "
          f"box strings {sum(e['id'] in seen for e in box)}/{len(box)}")
    if a.missing:
        addr = addresses(entries, a.rom)
        Path(a.missing).write_text("".join(f"{e['id']} {addr[e['id']]:06X}\n" for e in box if e["id"] not in seen))


if __name__ == "__main__":
    main()
