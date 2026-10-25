"""Render the game's 1bpp font as a labelled sheet: each cell shows the ROM glyph, its 16-bit code and the
table's reading drawn in MS Gothic beside it, so a reader can spot table errors.

    python -X utf8 tools/fontsheet.py --out work/font/k --from 0x100 --to 0x400 [--tbl tbl/jp.tbl] [--fmt 16x16]

Glyph layout (docs/re/font.md): 16x16 = 32 bytes per code, rows of 2 bytes, MSB = left pixel.
"""
import argparse
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).parent))
from tbl import Table

ROM = Path(__file__).parent.parent / "rom" / "Farland Story 2 (Japan).sfc"
FONTS = {"16x16": (0x41000, 16, 16), "8x16": (0x40000, 8, 16)}
ORDERS = {"tl-tr-bl-br": [(0, 0), (1, 0), (0, 1), (1, 1)], "tl-bl-tr-br": [(0, 0), (0, 1), (1, 0), (1, 1)]}


def glyph(rom, base, w, h, code, order):
    """Glyph = 8x8 1bpp tiles (8 bytes each) in `order` (tile index -> (tx, ty))."""
    off = base + code * w * h // 8
    img = Image.new("L", (w, h), 255)
    for i, (tx, ty) in enumerate(order):
        for y in range(8):
            row = rom[off + i * 8 + y]
            for x in range(8):
                if row & (0x80 >> x):
                    img.putpixel((tx * 8 + x, ty * 8 + y), 0)
    return img


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True, help="output prefix; writes <out>_<n>.png")
    ap.add_argument("--from", dest="lo", type=lambda s: int(s, 0), default=0)
    ap.add_argument("--to", dest="hi", type=lambda s: int(s, 0), default=0x100)
    ap.add_argument("--tbl", default=str(Path(__file__).parent.parent / "tbl" / "jp.tbl"))
    ap.add_argument("--fmt", choices=FONTS, default="16x16")
    ap.add_argument("--per-page", type=int, default=256)
    ap.add_argument("--order", choices=ORDERS, default="tl-bl-tr-br")
    a = ap.parse_args()
    rom = ROM.read_bytes()
    base, w, h = FONTS[a.fmt]
    order = ORDERS[a.order] if a.fmt == "16x16" else [(0, 0), (0, 1)]
    t = Table.load(a.tbl) if Path(a.tbl).exists() else None
    jp = ImageFont.truetype("C:/Windows/Fonts/msgothic.ttc", 16)
    lab = ImageFont.load_default()
    z, cols, cw, ch = 3, 16, 3 * w + 40, 3 * h + 14
    codes = list(range(a.lo, a.hi))
    for page in range(0, len(codes), a.per_page):
        chunk = codes[page:page + a.per_page]
        sheet = Image.new("L", (cols * cw, (len(chunk) + cols - 1) // cols * ch), 255)
        d = ImageDraw.Draw(sheet)
        for i, c in enumerate(chunk):
            x, y = i % cols * cw, i // cols * ch
            sheet.paste(glyph(rom, base, w, h, c, order).resize((w * z, h * z), Image.NEAREST), (x, y))
            d.text((x, y + h * z), f"{c:04X}", font=lab, fill=0)
            reading = t.dec.get(c.to_bytes(2, "little")) if t else None
            if reading:
                d.text((x + w * z + 4, y + 8), reading[:1], font=jp, fill=0)
        out = Path(f"{a.out}_{page // a.per_page:02d}.png")
        out.parent.mkdir(parents=True, exist_ok=True)
        sheet.save(out)
        print(out)


if __name__ == "__main__":
    main()
