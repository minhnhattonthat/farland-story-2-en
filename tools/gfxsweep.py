"""Static graphics sweep (docs/re/graphics.md): render the whole ROM, and every unpacked LZ block, as tile sheets
so a reader can spot tile-drawn Japanese. Each sheet is 512 px wide (64 tiles of 8x8), one row label per
64 tiles in the left margin (file offset, or block:offset). Writes an index of every sheet and prints every
region it skipped and why.

    python -X utf8 tools/gfxsweep.py --out work/sweep [--fmt 2bpp|4bpp] [--rows 64] [--zoom 2] [--lz work/lz]
    python -X utf8 tools/gfxsweep.py --out work/sweep --fmt 2bpp --rank 0.45     # only text-like 2 KB chunks
"""
import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).parent.parent
COLS, MARGIN = 64, 72


def tile(data, off, bpp):
    """8x8 SNES planar tile -> 64 values 0..(2^bpp-1)."""
    px = []
    for y in range(8):
        planes = [data[off + y * 2], data[off + y * 2 + 1]]
        if bpp == 4:
            planes += [data[off + 16 + y * 2], data[off + 16 + y * 2 + 1]]
        for x in range(8):
            bit = 7 - x
            px.append(sum(((p >> bit) & 1) << i for i, p in enumerate(planes)))
    return px


def textlike(data, start, end, bpp):
    """Fraction of non-blank tiles that use exactly two colours with 10-60% ink: menu/label glyph tiles do,
    map and sprite tiles mostly don't. A prefilter only; it ranks chunks, it proves nothing."""
    tsize, hits, total = 8 * bpp, 0, 0
    for off in range(start, end - tsize + 1, tsize):
        vals = tile(data, off, bpp)
        cols = set(vals)
        if len(cols) == 1:
            continue
        total += 1
        if len(cols) == 2:
            ink = sum(v != max(set(vals), key=vals.count) for v in vals)
            hits += 6 <= ink <= 38
    return hits / total if total else 0.0, total


def sheet(data, start, end, bpp, label, rows):
    tsize = 8 * bpp
    n = (end - start) // tsize
    nrows = (n + COLS - 1) // COLS
    img = Image.new("L", (MARGIN + COLS * 8, nrows * 8), 255)
    pix = img.load()
    scale = 255 // ((1 << bpp) - 1)
    for t in range(n):
        vals = tile(data, start + t * tsize, bpp)
        tx, ty = MARGIN + t % COLS * 8, t // COLS * 8
        for i, v in enumerate(vals):
            pix[tx + i % 8, ty + i // 8] = 255 - v * scale
    d = ImageDraw.Draw(img)
    f = ImageFont.load_default()
    for r in range(0, nrows, 2):
        d.text((1, r * 8 - 1), label(start + r * COLS * tsize), font=f, fill=0)
    return img


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--fmt", choices=["2bpp", "4bpp"], default="2bpp")
    ap.add_argument("--rows", type=int, default=64, help="tile rows per sheet")
    ap.add_argument("--zoom", type=int, default=2)
    ap.add_argument("--lz", help="directory of unpacked LZ blocks (tools/lzscan.py --dump) to sweep instead of the ROM")
    ap.add_argument("--rank", type=float, help="only render 2 KB chunks whose textlike() score >= this, "
                    "zoomed x2 and merged into runs; every other chunk is listed as skipped with its score")
    a = ap.parse_args()
    if a.rank is not None:
        return ranked(a)
    bpp = int(a.fmt[0])
    span = a.rows * COLS * 8 * bpp
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    index = []
    sources = []
    starts = []  # LZ mode: all blocks concatenated, each starting on a fresh sheet row
    if a.lz:
        row = COLS * 8 * bpp
        combined = bytearray()
        for p in sorted(Path(a.lz).glob("*.bin")):
            starts.append((len(combined), p.stem))
            b = p.read_bytes()
            combined += b + bytes(-len(b) % row)
        sources.append(("lz", bytes(combined)))
    else:
        sources.append(("rom", (ROOT / "rom" / "Farland Story 2 (Japan).sfc").read_bytes()))
    for name, data in sources:
        usable = len(data) - len(data) % (8 * bpp)
        if usable < len(data):
            print(f"skip {name}: last {len(data) - usable} bytes (not a whole tile)")
        for s in range(0, usable, span):
            e = min(s + span, usable)
            def lab(o):
                if not starts:
                    return f"{o:06X}"
                base, blk = max((b, n) for b, n in starts if b <= o)
                return f"{blk}+{o - base:X}"
            img = sheet(data, s, e, bpp, lab, a.rows)
            img = img.resize((img.width * a.zoom, img.height * a.zoom), Image.NEAREST)
            fn = out / f"{a.fmt}_{name}_{s:06X}.png"
            img.save(fn)
            index.append(f"{fn.name}\t{name}\t{s:06X}-{e:06X}")
    (out / f"index_{a.fmt}.tsv").write_text("\n".join(index) + "\n", encoding="utf-8")
    print(f"{len(index)} sheets in {out}")


def ranked(a):
    bpp = int(a.fmt[0])
    chunk = 2048
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    sources = [(p.stem, p.read_bytes()) for p in sorted(Path(a.lz).glob("*.bin"))] if a.lz else \
        [("rom", (ROOT / "rom" / "Farland Story 2 (Japan).sfc").read_bytes())]
    index, skipped = [], []
    for name, data in sources:
        runs = []
        for s in range(0, len(data) - len(data) % (8 * bpp), chunk):
            e = min(s + chunk, len(data) - len(data) % (8 * bpp))
            score, n = textlike(data, s, e, bpp)
            if score >= a.rank and n >= 8:
                if runs and runs[-1][1] == s and runs[-1][1] - runs[-1][0] < 8 * chunk:
                    runs[-1][1] = e
                else:
                    runs.append([s, e])
            else:
                skipped.append(f"{name}\t{s:06X}\tscore {score:.2f}\ttiles {n}")
        for s, e in runs:
            lab = (lambda o: f"{o:06X}") if name == "rom" else (lambda o, n=name: f"{n[-4:]}+{o:X}")
            img = sheet(data, s, e, bpp, lab, 0)
            img = img.resize((img.width * 2, img.height * 2), Image.NEAREST)
            fn = out / f"r{a.fmt}_{name}_{s:06X}.png"
            img.save(fn)
            index.append(f"{fn.name}\t{name}\t{s:06X}-{e:06X}")
    (out / f"index_r{a.fmt}.tsv").write_text("\n".join(index) + "\n", encoding="utf-8")
    (out / f"skipped_r{a.fmt}.tsv").write_text("\n".join(skipped) + "\n", encoding="utf-8")
    print(f"{len(index)} sheets, {len(skipped)} chunks skipped (listed in skipped_r{a.fmt}.tsv) in {out}")


if __name__ == "__main__":
    main()
