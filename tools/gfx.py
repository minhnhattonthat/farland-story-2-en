"""gfx.py: graphics text (docs/re/graphics.md), drawn with the VWF font (fonts/vwf.txt).

- G2 title menu: LZ block 0x6321 unpacks to the BG2 tiles at VRAM byte 0x4000; the menu text is tiles $B4-$E5,
  48 cells (8 wide x 6 tall, 3 lines of 16 px) over a stone texture. Each cell is redrawn as the texture tile its
  row uses outside the text (the cell left of the text), with the ink in colour 1 (white).
- G3 command labels: raw 2bpp at 0xD45EB, 10 unit-menu slots of 6x2 tiles (48x16 px) then 7 map-menu slots of
  10x2 tiles (80x16 px); in each slot the top tile row, then the bottom one. Ink = plane 0, plane 1 = $FF.
  The menus copy whole slots to VRAM ($C0:0111 MVN, then DMA to $5100).

    python -X utf8 tools/gfx.py [--sheet work/gfx/en.png]
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import font

LABELS = 0xD45EB
UNIT_LABELS = ["Move", "Warp", "Action", "Special", "Shop", "Weapons", "Items", "Trade", "Rally", "Wait"]
MAP_LABELS = ["End Turn", "Full Map", "Unit List", "Objective", "Save", "Load", "Settings"]
LABEL_X = 1  # left margin of a label in its slot, px

TITLE_BLOCK = 0x6321
TITLE_LINES = ["New Game", "Continue", "Settings"]
# BG2 tile in each text cell (cols 12-19, rows 19-24 of the title tilemap), and the texture tile of each row
TITLE_CELLS = [list(range(0xB4, 0xBC)), list(range(0xBE, 0xC6)), list(range(0xC7, 0xCF)),
               [0xC6] + list(range(0xCF, 0xD6)), list(range(0xD6, 0xDE)), list(range(0xDE, 0xE6))]
TITLE_BG = [0xB3, 0xBD, 0xC6, 0xC6, 0xBD, 0xB3]
TITLE_INK = 1


def render(text, width, x=0, glyphs=None):
    """16 rows x `width` px of 0/1 ink, text starting at x. ValueError if it doesn't fit."""
    g = {ch: (data, adv) for ch, data, adv in (glyphs or font.load())}
    rows = [[0] * width for _ in range(16)]
    for ch in text:
        data, adv = g[ch]
        for y in range(16):
            for i in range(8):
                if data[y] & (0x80 >> i):
                    if x + i >= width:
                        raise ValueError(f"{text!r} is wider than {width} px")
                    rows[y][x + i] = 1
        x += adv
    return rows


def menu_labels(glyphs=None):
    """The G3 label tiles: bytes for LABELS."""
    out = bytearray()
    for text, w in [(t, 6) for t in UNIT_LABELS] + [(t, 10) for t in MAP_LABELS]:
        rows = render(text, w * 8, LABEL_X, glyphs)
        for band in (0, 8):
            for c in range(w):
                for y in range(band, band + 8):
                    out += bytes([sum(0x80 >> i for i in range(8) if rows[y][c * 8 + i]), 0xFF])
    return bytes(out)


def tile4(data, t):
    """Tile t of 4bpp planar data -> 8x8 colour indices."""
    b = data[t * 32:t * 32 + 32]
    return [[sum((b[y * 2 + (p & 1) + (p >> 1) * 16] >> (7 - x) & 1) << p for p in range(4)) for x in range(8)]
            for y in range(8)]


def untile4(px):
    b = bytearray(32)
    for y in range(8):
        for x in range(8):
            for p in range(4):
                if px[y][x] >> p & 1:
                    b[y * 2 + (p & 1) + (p >> 1) * 16] |= 0x80 >> x
    return bytes(b)


def title_menu(data, glyphs=None):
    """The unpacked title block with TITLE_LINES centred in the 64-px menu."""
    data = bytearray(data)
    width = 64
    w = font.widths(glyphs)
    ink = [render(t, width, (width - font.text_width(t, w) + 1) // 2, glyphs) for t in TITLE_LINES]
    for row, (cells, bg) in enumerate(zip(TITLE_CELLS, TITLE_BG)):
        lines = ink[row // 2]
        for col, t in enumerate(cells):
            px = [r[:] for r in tile4(data, bg)]
            hit = False
            for y in range(8):
                for x in range(8):
                    if lines[(row % 2) * 8 + y][col * 8 + x]:
                        px[y][x], hit = TITLE_INK, True
            if t in TITLE_BG:  # a texture tile shared with the frame: must stay blank
                if hit:
                    raise ValueError(f"title line {row // 2} needs ink in shared tile {t:02X}")
                continue
            data[t * 32:t * 32 + 32] = untile4(px)
    return bytes(data)


def sheet(path, glyphs=None):
    """Preview: the G3 labels (black on grey) and the title menu cells (grey levels)."""
    from PIL import Image
    lab = menu_labels(glyphs)
    img = Image.new("L", (80, 17 * 18 + 50), 160)
    off = 0
    for n, w in enumerate([6] * 10 + [10] * 7):
        for t in range(2 * w):
            for y in range(8):
                b = lab[off + t * 16 + y * 2]
                for x in range(8):
                    if b >> (7 - x) & 1:
                        img.putpixel(((t % w) * 8 + x, n * 18 + (t // w) * 8 + y), 0)
        off += w * 32
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    img.resize((img.width * 4, img.height * 4), Image.NEAREST).save(path)


def selftest():
    lab = menu_labels()
    assert len(lab) == 0x1040 and all(lab[i] == 0xFF for i in range(1, len(lab), 2))
    rows = render("A", 8, 1)
    assert rows[font.TOP][3] == 1 and rows[font.TOP][2] == 0  # A's apex at x = 1 + 2
    try:
        render("Weapons and more", 48)
        raise AssertionError("overflow not caught")
    except ValueError:
        pass
    t = bytes(range(32))
    assert untile4(tile4(t, 0)) == t


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheet", help="write a zoomed preview PNG of the G3 labels")
    a = ap.parse_args()
    selftest()
    print("gfx selftest ok")
    if a.sheet:
        sheet(a.sheet)


if __name__ == "__main__":
    main()
