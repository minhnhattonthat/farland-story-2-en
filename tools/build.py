"""build.py: original dump -> build/farland2_en.sfc.

Phase 3 (identity build): unpack every text run (tools/textscan.py) and LZ block (tools/lzscan.py), repack with no
edits. Text is re-encoded through tbl/jp.tbl; a block is recompressed only when its unpacked bytes changed (our
packer is not the original's, docs/re/compression.md). `--identity` exits 1 unless the output equals the dump.
Later phases swap in the phase-4 script files and the English table here.

    python -X utf8 tools/build.py [--identity]
"""
import argparse
import hashlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import check_rom
import lz
import lzscan
import textscan
from tbl import Table

ROOT = Path(__file__).resolve().parents[1]
ROM = ROOT / "rom" / "Farland Story 2 (Japan).sfc"
OUT = ROOT / "build" / "farland2_en.sfc"


def unpack(rom, table):
    """({offset: (decoded text, byte length)}, {offset: (packed size, unpacked bytes)})."""
    texts = {s: (table.decode(rom, s, e - s)[0], e - s) for s, e in textscan.runs(rom, 3, 2)}
    blocks = {src: (size, lz.decompress(rom, src)[0]) for src, (size, _, _) in lzscan.find_blocks(rom).items()}
    return texts, blocks


def repack(rom, table, texts, blocks):
    out = bytearray(rom)
    # shortcut: in-place only (runs found by scan, 11 overlap across byte alignments); phase 4 replaces this
    # with pointer-based script files, phase 7 with relocation.
    for s, (text, n) in texts.items():
        b = table.encode(text)
        if len(b) > n:
            raise ValueError(f"text at {s:06X}: {len(b)} bytes, room for {n}")
        out[s:s + len(b)] = b
    for src, (size, data) in blocks.items():
        if data == lz.decompress(rom, src)[0]:
            continue
        b = lz.compress(data)
        if len(b) > size:
            raise ValueError(f"LZ block {src:06X}: {len(b)} bytes packed, room for {size}")
        out[src:src + len(b)] = b
    return bytes(out)


def build():
    check_rom.check()
    rom, table = ROM.read_bytes(), Table.load(ROOT / "tbl" / "jp.tbl")
    texts, blocks = unpack(rom, table)
    return rom, repack(rom, table, texts, blocks), len(texts), len(blocks)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--identity", action="store_true", help="fail unless the output equals the dump")
    a = ap.parse_args()
    rom, out, nt, nb = build()
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_bytes(out)
    print(f"{OUT.relative_to(ROOT)}: {nt} text runs, {nb} LZ blocks, sha1 {hashlib.sha1(out).hexdigest()}")
    if a.identity:
        diff = [i for i in range(len(rom)) if rom[i] != out[i]] if len(out) == len(rom) else ["size"]
        if diff:
            sys.exit(f"NOT identical: {len(diff)} bytes differ, first {diff[0]}")
        print("identical")


if __name__ == "__main__":
    main()
