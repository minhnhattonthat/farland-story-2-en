"""build.py: original dump + script/*.json -> build/farland2_en.sfc.

Text comes from the phase-4 script files (`en`, else `jp`), encoded through tbl/jp.tbl and written in place over the
original string (phase 7 adds relocation and pointer rewriting). LZ blocks (tools/lzscan.py) are recompressed only
when their unpacked bytes changed (our packer is not the original's, docs/re/compression.md).
`--identity` unpacks straight from the dump instead (tools/extract.py) and exits 1 unless the output equals it.

    python -X utf8 tools/build.py [--identity]
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import check_rom
import extract
import lz
import lzscan
from tbl import Table

ROOT = Path(__file__).resolve().parents[1]
ROM = ROOT / "rom" / "Farland Story 2 (Japan).sfc"
OUT = ROOT / "build" / "farland2_en.sfc"
END = b"\x00\x80"


def unpack(rom, table):
    """([script entries], {offset: (packed size, unpacked bytes)}) straight from the dump."""
    entries = [e for es in extract.collect(rom, table).values() for e in es]
    blocks = {src: (size, lz.decompress(rom, src)[0]) for src, (size, _, _) in lzscan.find_blocks(rom).items()}
    return entries, blocks


def load_script():
    return [e for p in sorted(extract.SCRIPT.glob("*.json")) for e in json.loads(p.read_text(encoding="utf-8"))]


def repack(rom, table, entries, blocks):
    out = bytearray(rom)
    for e in entries:
        b = table.encode(e["en"] or e["jp"]) + END
        if len(b) > e["len"]:
            raise ValueError(f"{e['id']}: {len(b)} bytes, room for {e['len']} (in place until phase 7)")
        a = int(e["addr"], 16)
        out[a:a + len(b)] = b
    for src, (size, data) in blocks.items():
        if data == lz.decompress(rom, src)[0]:
            continue
        b = lz.compress(data)
        if len(b) > size:
            raise ValueError(f"LZ block {src:06X}: {len(b)} bytes packed, room for {size}")
        out[src:src + len(b)] = b
    return bytes(out)


def build(identity=False):
    check_rom.check()
    rom, table = ROM.read_bytes(), Table.load(ROOT / "tbl" / "jp.tbl")
    entries, blocks = unpack(rom, table)
    if not identity:
        entries = load_script()
    return rom, repack(rom, table, entries, blocks), len(entries), len(blocks)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--identity", action="store_true", help="unpack from the dump; fail unless the output equals it")
    a = ap.parse_args()
    rom, out, nt, nb = build(a.identity)
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_bytes(out)
    print(f"{OUT.relative_to(ROOT)}: {nt} strings, {nb} LZ blocks, sha1 {hashlib.sha1(out).hexdigest()}")
    if a.identity:
        diff = [i for i in range(len(rom)) if rom[i] != out[i]] if len(out) == len(rom) else ["size"]
        if diff:
            sys.exit(f"NOT identical: {len(diff)} bytes differ, first {diff[0]}")
        print("identical")


if __name__ == "__main__":
    main()
