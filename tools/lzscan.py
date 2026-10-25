"""List every LZ-compressed block the game loads (callers of $C0:167D, docs/re/compression.md): direct calls with
an immediate source, and the 3-byte pointer tables the other callers index. Prints file offset, packed and
unpacked size; --dump DIR writes each unpacked block as DIR/<offset>.bin for the graphics sweep.

    python -X utf8 tools/lzscan.py [--dump work/lz]
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lz import decompress

ROOT = Path(__file__).parent.parent
# Direct calls: source set by LDA #lo / STA $10, bank by LDA/LDX #bank / STA $12 just before JSL $C0167D.
DIRECT = [0x0034A6, 0x003D3F, 0x003D7B, 0x003F1A, 0x004520, 0x00454A, 0x008065, 0x00468C, 0x009C3B, 0x008F80,
          0x005FD0, 0x006321, 0x007CD9]
# Pointer tables read as LDA table,x (lo/hi) + LDA table+2,x (bank); stride 3 (x = index * 3).
TABLES = {0x0236CB: "$C1:2512 caller", 0x023548: "$C1:2624", 0x02354B: "$C1:2642", 0x023D91: "$C1:2720",
          0x02456E: "$C1:AE6D", 0x024595: "$C1:AEB0", 0x04D2A9: "$C1:B5CE..B9FF", 0x04D1E6: "$C1:BB3B..BBD7",
          0x023D7C: "$C2:31E5", 0x0242E8: "$C1:2939"}


def table_entries(rom, base, limit=256):
    """Walk a 3-byte pointer table until an entry is not a plausible block (bank < $C0, or bad sizes)."""
    out = []
    for i in range(limit):
        p = base + 3 * i
        lo, hi, bank = rom[p], rom[p + 1], rom[p + 2]
        if bank < 0xC0:
            break
        src = (bank << 16 | hi << 8 | lo) & 0x3FFFFF
        try:
            data, size = decompress(rom, src)
        except IndexError:
            break
        if not data or len(data) > 0x10000 or size < 4:
            break
        out.append((i, src, size, len(data)))
    return out


def find_blocks(rom):
    """{file offset: (packed size, unpacked size, where it was found)} for every known block."""
    blocks = {}
    for src in DIRECT:
        data, size = decompress(rom, src)
        blocks.setdefault(src, (size, len(data), "direct"))
    for base, who in TABLES.items():
        for i, src, size, n in table_entries(rom, base):
            blocks.setdefault(src, (size, n, f"table {base:06X}[{i}] ({who})"))
    return blocks


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dump", help="write unpacked blocks here")
    a = ap.parse_args()
    rom = (ROOT / "rom" / "Farland Story 2 (Japan).sfc").read_bytes()
    blocks = find_blocks(rom)
    for src in sorted(blocks):
        size, n, who = blocks[src]
        print(f"{src:06X} packed {size:5d} unpacked {n:5d}  {who}")
        if a.dump:
            Path(a.dump).mkdir(parents=True, exist_ok=True)
            Path(a.dump, f"{src:06X}.bin").write_bytes(decompress(rom, src)[0])
    print(f"{len(blocks)} blocks")


if __name__ == "__main__":
    main()
