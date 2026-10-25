"""Scan the ROM for runs that decode as script text: 16-bit words, each a glyph (< $032A) or a control ($8001-$800F),
ending in {end} ($8000). Prints one line per run: file offset, length, decoded text. Used in recon to map text
regions (docs/re/text.md); both byte alignments are scanned.

    python -X utf8 tools/textscan.py [--min 3] [--kana 2] [--ranges]
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from tbl import Table

ROOT = Path(__file__).parent.parent
ARGS = {0x800D: 2, 0x800E: 1}  # control -> argument words


def runs(rom, min_chars, min_kana):
    n = len(rom)
    for align in (0, 1):
        start, chars, kana, p = None, 0, 0, align
        while p + 1 < n:
            w = rom[p] | rom[p + 1] << 8
            if start is None:
                start, chars, kana = p, 0, 0
            if w == 0x8000:
                if chars >= min_chars and kana >= min_kana:
                    yield start, p + 2
                start = None
                p += 2
            elif w < 0x032A:
                chars += 1
                kana += 0x4C <= w < 0xF1 or w >= 0x100
                p += 2
            elif 0x8001 <= w <= 0x800F:
                p += 2 + 2 * ARGS.get(w, 0)
            else:
                start = None
                p += 2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min", type=int, default=3, help="min glyphs per run")
    ap.add_argument("--kana", type=int, default=2, help="min kana/kanji per run")
    ap.add_argument("--ranges", action="store_true", help="merge adjacent runs, print ranges only")
    a = ap.parse_args()
    rom = (ROOT / "rom" / "Farland Story 2 (Japan).sfc").read_bytes()
    t = Table.load(ROOT / "tbl" / "jp.tbl")
    found = sorted(runs(rom, a.min, a.kana))
    if a.ranges:
        merged = []
        for s, e in found:
            if merged and s - merged[-1][1] <= 0x40:
                merged[-1][1] = e
                merged[-1][2] += 1
            else:
                merged.append([s, e, 1])
        for s, e, k in merged:
            print(f"{s:06X}-{e:06X} {e - s:6d} bytes {k:5d} strings")
        print(f"total {sum(e - s for s, e, _ in merged)} bytes in {len(found)} strings")
        return
    for s, e in found:
        text, _ = t.decode(rom, s, e - s)
        print(f"{s:06X} {e - s:5d} {text}")


if __name__ == "__main__":
    main()
