"""build.py: original dump + script/*.json -> build/farland2_en.sfc.

Text comes from the script files: `en` (English table, tools/font.py) else `jp` (tbl/jp.tbl). The English build
is expanded to 4 MiB and gets the VWF engine (asm/vwf.asm, asar in tools/asar/). A string that fits its original
room stays in place; a longer one moves to banks $F2-$FF and every pointer to it is rewritten by kind (`vm`/`p24`
24-bit, `imm` 16-bit + bank immediates). A `p16` table whose strings change moves whole into bank $F1: its
entries are rewritten and every `LDA #bank` that pairs with a read of the table is patched to $F1.
LZ blocks (tools/lzscan.py) are recompressed only when their unpacked bytes changed (docs/re/compression.md).

    python -X utf8 tools/build.py [--identity] [--marker]

`--identity` unpacks straight from the dump (tools/extract.py), builds in place, and exits 1 unless the output
equals it. `--marker` fills every string with its `[id]` marker (tools/marker.py) -> build/farland2_marker.sfc.
"""
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import check_rom
import extract
import font
import lz
import lzscan
from tbl import Table

ROOT = Path(__file__).resolve().parents[1]
ROM = ROOT / "rom" / "Farland Story 2 (Japan).sfc"
OUT = ROOT / "build" / "farland2_en.sfc"
MARKER_OUT = ROOT / "build" / "farland2_marker.sfc"
ASAR = ROOT / "tools" / "asar" / "asar.exe"
ASM = ROOT / "asm" / "vwf.asm"
END = b"\x00\x80"
SIZE = 0x400000     # 4 MiB: banks $F0-$FF = file 0x300000-0x3FFFFF (docs/re/rom.md)
P16_BANK = 0x310000  # $F1: relocated p16 tables
FREE = (0x320000, 0x400000)  # $F2-$FF: relocated strings ($F0 holds the VWF code and font)
MOVES = {}  # filled by build(): relocated strings, written beside the ROM as <rom>.reloc.txt


def unpack(rom, table):
    """([script entries], {offset: (packed size, unpacked bytes)}) straight from the dump."""
    entries = [e for es in extract.collect(rom, table).values() for e in es]
    blocks = {src: (size, lz.decompress(rom, src)[0]) for src, (size, _, _) in lzscan.find_blocks(rom).items()}
    return entries, blocks


def load_script():
    return [e for p in sorted(extract.SCRIPT.glob("*.json")) for e in json.loads(p.read_text(encoding="utf-8"))]


def repack_lz(rom, out, blocks):
    for src, (size, data) in blocks.items():
        if data == lz.decompress(rom, src)[0]:
            continue
        b = lz.compress(data)
        if len(b) > size:
            raise ValueError(f"LZ block {src:06X}: {len(b)} bytes packed, room for {size}")
        out[src:src + len(b)] = b


def repack(rom, table, entries, blocks):
    """In-place build with one table (the identity build)."""
    out = bytearray(rom)
    for e in entries:
        b = table.encode(e["en"] or e["jp"]) + END
        if len(b) > e["len"]:
            raise ValueError(f"{e['id']}: {len(b)} bytes, room for {e['len']} (in place)")
        a = int(e["addr"], 16)
        out[a:a + len(b)] = b
    repack_lz(rom, out, blocks)
    return bytes(out)


def p16_tables():
    """[(table offset, entry count)] of the p16 tables in extract.TABLES."""
    return [(base, n) for _, base, n, _, kind in extract.TABLES if kind == "p16"]


def p16_bank_sites(rom, base, n):
    """Offsets of the `LDA #bank` immediates that pair with each `LDA $bb:tttt,x` read of the n-entry table at
    `base` (also reads of a later entry, e.g. the save slots' `+6`; the bank is stored to $16, 8-17 bytes after
    the read: docs/re/vwf.md §Relocation)."""
    bank = 0xC0 | base >> 16
    sites = []
    for t in range(base, base + 2 * n, 2):
        read, i = bytes([0xBF, t & 0xFF, t >> 8 & 0xFF, bank]), 0
        while (i := rom.find(read, i, 0x40000)) >= 0:
            w = rom[i + 4:i + 40]
            j = next((k for k in range(len(w) - 3) if w[k] == 0xA9 and w[k + 1] == bank and w[k + 2] == 0x85), None)
            if j is None:
                raise ValueError(f"p16 table {base:06X}: read at {i:06X} has no LDA #bank after it")
            sites.append(i + 4 + j + 1)
            i += 1
    if not sites:
        raise ValueError(f"p16 table {base:06X}: no reads found")
    return sites


# Blank templates the game copies to a RAM buffer and then overlays a name onto without its terminator
# ($C1:ECBA-ECDA: template -> $7E:F9D6, unit name over it, `JSL $C2:28E9`). A name longer than the template
# overwrites the terminator and the next concatenation runs away (hang after a battle, docs/re/vwf.md). English
# builds fill the template with zero-width blanks, one per character of the longest allowed name.
TEMPLATES = {"battle.01ED33": ("units", 16)}


def name_templates(entries, en):
    entries = [dict(e) for e in entries]
    for tid, (names, n) in TEMPLATES.items():
        t = next(e for e in entries if e["id"] == tid)
        t["en"] = t["en"] or font.ZWSP * n
        room = len(en.encode(t["en"]))
        for e in entries:
            if e["id"].split(".")[0] == names and e["en"] and len(en.encode(e["en"])) > room:
                raise ValueError(f"{e['id']}: {e['en']!r} is longer than the {n}-character name template {tid}")
    return entries


def cpu(off):
    return 0xC00000 | off


def english(rom, entries, blocks, moves=None):
    """4 MiB build: English strings placed (in place or relocated), pointers rewritten, VWF applied.
    `moves` (a dict) receives {old offset: new offset} of every relocated string."""
    moves = {} if moves is None else moves
    jp, en = Table.load(ROOT / "tbl" / "jp.tbl"), font.english_table()
    out = bytearray(rom) + b"\xff" * (SIZE - len(rom))
    entries = name_templates(entries, en)
    enc = {e["id"]: (en.encode(e["en"]) if e["en"] else jp.encode(e["jp"])) + END for e in entries}
    # p16 tables with any English move whole to P16_BANK
    table_of = {}
    for base, n in p16_tables():
        for i in range(n):
            table_of[base + 2 * i] = base
    moved_tables = {table_of[int(p[4:], 16)] for e in entries if e["en"]
                    for p in e["ptrs"] if p.startswith("p16:")}
    p16_free, free = P16_BANK, FREE[0]
    for e in entries:
        b, a = enc[e["id"]], int(e["addr"], 16)
        p16 = [int(p[4:], 16) for p in e["ptrs"] if p.startswith("p16:")]
        if p16 and any(table_of[p] in moved_tables for p in p16):
            if not all(table_of[p] in moved_tables for p in p16):
                raise ValueError(f"{e['id']}: shared by a moved and an unmoved p16 table")
            new, p16_free = p16_free, p16_free + len(b)
            if p16_free > P16_BANK + 0x10000:
                raise ValueError("p16 bank full")
        elif len(b) <= e["len"]:
            out[a:a + len(b)] = b
            continue
        elif p16:
            raise ValueError(f"{e['id']}: {len(b)} bytes, room for {e['len']}, and its p16 table stays in place")
        else:
            if free >> 16 != (free + len(b) - 1) >> 16:
                free = (free | 0xFFFF) + 1  # never cross a bank
            new, free = free, free + len(b)
            if free > FREE[1]:
                raise ValueError("expansion full")
        out[new:new + len(b)] = b
        moves[a] = new
        for p in e["ptrs"]:
            kind, at = p.split(":")
            if kind in ("vm", "p24"):
                out[int(at, 16):int(at, 16) + 3] = cpu(new).to_bytes(3, "little")
            elif kind == "p16":
                out[int(at, 16):int(at, 16) + 2] = (new & 0xFFFF).to_bytes(2, "little")
            elif kind == "imm":
                lo, bank = (int(x, 16) for x in at.split("/"))
                out[lo:lo + 2] = (new & 0xFFFF).to_bytes(2, "little")
                out[bank] = cpu(new) >> 16
    for base, n in p16_tables():
        if base not in moved_tables:
            continue
        for s in p16_bank_sites(rom, base, n):
            out[s] = cpu(P16_BANK) >> 16
    repack_lz(rom, out, blocks)
    return apply_asm(out)


def apply_asm(out):
    """Write the VWF binaries, assemble asm/vwf.asm onto the image with asar, return the patched bytes."""
    OUT.parent.mkdir(exist_ok=True)
    for name, data in font.binaries().items():
        (OUT.parent / name).write_bytes(data)
    tmp = OUT.parent / "asm_tmp.sfc"
    tmp.write_bytes(out)
    r = subprocess.run([str(ASAR), "--fix-checksum=off", str(ASM), str(tmp)], capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(f"asar failed:\n{r.stdout}{r.stderr}")
    data = tmp.read_bytes()
    tmp.unlink()
    if len(data) != SIZE:
        raise RuntimeError(f"asar changed the size to {len(data):#x}")
    return data


def build(identity=False, marker=False, qa=()):
    check_rom.check()
    rom, table = ROM.read_bytes(), Table.load(ROOT / "tbl" / "jp.tbl")
    entries, blocks = unpack(rom, table)
    if identity:
        return rom, repack(rom, table, entries, blocks), len(entries), len(blocks)
    entries = load_script()
    if marker:
        import marker as mk
        entries = mk.fill(entries)
    override = dict(q.split("=", 1) for q in qa)
    if set(override) - {e["id"] for e in entries}:
        raise ValueError(f"--qa: unknown id(s) {sorted(set(override) - {e['id'] for e in entries})}")
    entries = [dict(e, en=override[e["id"]]) if e["id"] in override else e for e in entries]
    out = english(rom, entries, blocks, MOVES)
    return rom, out, len(entries), len(blocks)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--identity", action="store_true", help="unpack from the dump; fail unless the output equals it")
    ap.add_argument("--marker", action="store_true", help="every string replaced by its [id] marker")
    ap.add_argument("--qa", action="append", default=[], metavar="ID=TEXT", help="override one string (stress tests)")
    ap.add_argument("--out", help="output path (default build/farland2_en.sfc, or _marker with --marker)")
    a = ap.parse_args()
    rom, out, nt, nb = build(a.identity, a.marker, a.qa)
    dest = Path(a.out).resolve() if a.out else MARKER_OUT if a.marker else OUT
    dest.parent.mkdir(exist_ok=True)
    dest.write_bytes(out)
    # for tools/debug/warp.lua: scenes keyed to a Japanese string's address find the moved string
    dest.with_suffix(".reloc.txt").write_text("".join(f"{cpu(o):06X} {cpu(n):06X}\n" for o, n in sorted(MOVES.items())))
    print(f"{dest.relative_to(ROOT)}: {nt} strings, {nb} LZ blocks, sha1 {hashlib.sha1(out).hexdigest()}")
    if a.identity:
        diff = [i for i in range(len(rom)) if rom[i] != out[i]] if len(out) == len(rom) else ["size"]
        if diff:
            sys.exit(f"NOT identical: {len(diff)} bytes differ, first {diff[0]}")
        print("identical")


if __name__ == "__main__":
    main()
