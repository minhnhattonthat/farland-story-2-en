"""font.py: the English VWF font (fonts/vwf.txt) -> binaries for asm/vwf.asm, the English table, text widths.

VWF code of the i-th glyph in the file = word $0400 + i (docs/re/vwf.md). The English table is jp.tbl's control
codes plus one entry per glyph, so `{clr}{pos:00000000}Hello` encodes like the Japanese script.

    python -X utf8 tools/font.py [--sheet work/font/vwf.png] [--text "Hello, world"]
"""
import argparse
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from tbl import Table

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "fonts" / "vwf.txt"
JP_TBL = ROOT / "tbl" / "jp.tbl"
TOP = 3            # cell row of the first glyph row (cap top)
BASE = 0x0400      # VWF code of glyph 0
MAX_ADV = 8        # the renderer spills into one next cell only: px (0-7) + advance <= 16
ZWSP = "​"    # zero-width blank (name templates)
JP_REMAP = 0x4C   # JP codes $00-$4B (symbols, digits, A-Z) are drawn with the VWF glyph of the same character


def load(path=SRC):
    """[(char, [16 row bytes], advance)] in file order."""
    glyphs, cur = [], None
    for n, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        if line.startswith("== "):
            parts = line[3:].split(" ")
            ch = {r"\s": " ", r"\z": ZWSP}.get(parts[0], parts[0])
            cur = [ch, [], int(parts[1]) if len(parts) > 1 else None, n]
            glyphs.append(cur)
        elif cur is None or not line.strip():
            continue  # header comments, blank lines
        else:
            if set(line) - {"#", "."}:
                raise ValueError(f"{path}:{n}: bad row {line!r}")
            cur[1].append(line)
    out = []
    for ch, rows, adv, n in glyphs:
        if len(rows) > 16 - TOP:
            raise ValueError(f"{path}:{n}: {ch!r} has {len(rows)} rows, max {16 - TOP}")
        width = max((len(r) for r in rows), default=0)
        adv = width + 1 if adv is None else adv
        if width > 8 or adv > MAX_ADV:
            raise ValueError(f"{path}:{n}: {ch!r} width {width} advance {adv}, max 8")
        data = [0] * 16
        for y, r in enumerate(rows):
            data[TOP + y] = sum(0x80 >> x for x, c in enumerate(r) if c == "#")
        out.append((ch, data, adv))
    if len(out) > 128 or len({g[0] for g in out}) != len(out):
        raise ValueError("at most 128 glyphs, each character once")
    return out


def english_table(glyphs=None):
    glyphs = glyphs or load()
    ctrl = [l for l in JP_TBL.read_text(encoding="utf-8").splitlines() if "={" in l and not l.startswith("#")]
    chars = [f"{i:02X}{BASE >> 8:02X}=" + ("\\s" if ch == " " else ch) for i, (ch, _, _) in enumerate(glyphs)]
    return Table(ctrl + chars)


def widths(glyphs=None):
    return {ch: adv for ch, _, adv in (glyphs or load())}


def text_width(text, w=None):
    """Pixel width of plain text (no control codes)."""
    w = w or widths()
    return sum(w[c] for c in text)


def remap(glyphs=None):
    """bytes[JP_REMAP]: JP code -> VWF index ($FF = keep the original glyph). Full-width forms map to ASCII;
    the ideographic space maps to the VWF '　' (figure-width space), so code-padded numbers stay aligned."""
    glyphs = glyphs or load()
    index = {ch: i for i, (ch, _, _) in enumerate(glyphs)}
    jp = Table.load(JP_TBL)
    out = bytearray(b"\xff" * JP_REMAP)
    for code in range(JP_REMAP):
        ch = jp.dec.get(bytes([code, 0]), "")
        ch = ch if ch == "　" else unicodedata.normalize("NFKC", ch)
        if ch in index and ch != "▶":  # the menu cursor keeps its own glyph; VWF ▶ is for English yes/no lines
            out[code] = index[ch]
    return bytes(out)


def binaries(glyphs=None):
    """{name: bytes} for asm/vwf.asm's incbins."""
    glyphs = glyphs or load()
    shift = b"".join(((b << 8) >> px).to_bytes(2, "little") for px in range(8) for b in range(256))
    return {"vwf_font.bin": b"".join(bytes(d) for _, d, _ in glyphs),
            "vwf_width.bin": bytes(a for _, _, a in glyphs),
            "vwf_shift.bin": shift,
            "vwf_remap.bin": remap(glyphs),
            "vwf_consts.asm": f"!vwf_space = ${[c for c, _, _ in glyphs].index(' '):04X}\n".encode()}


def sheet(path, glyphs, zoom=4):
    from PIL import Image
    cols = 16
    img = Image.new("RGB", (cols * 10 * zoom, ((len(glyphs) + cols - 1) // cols) * 18 * zoom), (40, 40, 120))
    for i, (ch, data, adv) in enumerate(glyphs):
        ox, oy = (i % cols) * 10, (i // cols) * 18
        for y in range(16):
            for x in range(8):
                c = (255, 255, 255) if data[y] & (0x80 >> x) else ((70, 70, 160) if x < adv else (40, 40, 120))
                for zy in range(zoom):
                    for zx in range(zoom):
                        img.putpixel(((ox + x) * zoom + zx, (oy + y) * zoom + zy), c)
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    img.save(path)


def selftest():
    g = load()
    t = english_table(g)
    s = "{clr}{pos:00000000}{full}Hi, Ark! 25%"
    assert t.decode(t.encode(s) + b"\x00\x80")[0] == s + "{end}"
    assert t.encode("A") == bytes([[c for c, _, _ in g].index("A"), BASE >> 8])
    r = remap(g)
    assert r[0x32] == [c for c, _, _ in g].index("A") and r[0x28] == [c for c, _, _ in g].index("0")
    assert r[0x22] == 0xFF  # menu cursor keeps its own glyph
    b = binaries(g)
    assert len(b["vwf_shift.bin"]) == 4096 and b["vwf_shift.bin"][2 * (256 * 3 + 0xFF):][:2] == (0xFF00 >> 3).to_bytes(2, "little")
    assert text_width("AA", widths(g)) == 12


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheet", help="write a zoomed PNG of every glyph (advance shaded)")
    ap.add_argument("--text", help="print the pixel width of this text")
    a = ap.parse_args()
    selftest()
    g = load()
    print(f"{len(g)} glyphs, selftest ok")
    if a.sheet:
        sheet(a.sheet, g)
    if a.text:
        print(text_width(a.text, widths(g)), "px")


if __name__ == "__main__":
    main()
