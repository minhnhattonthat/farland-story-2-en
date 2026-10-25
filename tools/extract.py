"""extract.py: find every text string through the pointers that reach it and dump script/*.json (phase 4).

Pointer kinds (`ptrs` entries, `kind:hex file offset`):
- `vm`   24-bit pointer, argument of a script text opcode ($3C/$3D/$41; tools/vm.py)
- `p24`  24-bit pointer in a data record
- `p16`  16-bit in-bank pointer in a table (bank = the string's bank)
- `imm`  `LDA #addr` in code: the offset of the 16-bit immediate; `/` then the `LDA #bank` immediate's offset
Strings no pointer reaches (dead scenes) are kept with `"ptrs": []` so the coverage test still accounts for them.

    python -X utf8 tools/extract.py           # summary only
    python -X utf8 tools/extract.py --write   # write missing script/*.json (never overwrites; --force to)
"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import textscan
import vm
from tbl import Table

ROOT = Path(__file__).resolve().parents[1]
ROM = ROOT / "rom" / "Farland Story 2 (Japan).sfc"
SCRIPT = ROOT / "script"
CTRL_ARGS = {0x800D: 2, 0x800E: 1}  # control word -> argument words
BOX = {0x3C: "upper", 0x3D: "lower", 0x41: "centre"}  # script text opcode -> window (Bongo's names; phase 5 checks)

# (file, table offset, entries, stride, kind): verified tables (docs/re/text.md §Tables)
TABLES = [
    ("units", 0x245E3, 60, 2, "p16"),
    ("classes", 0x24923, 32, 2, "p16"),
    ("objectives", 0x251F3, 31, 2, "p16"),
    ("items", 0x25465, 129, 22, "p24"),
    ("item_desc", 0x2665B, 129, 2, "p16"),
    ("system", 0x23764, 39, 2, "p16"),   # stage numbers "０１".."２５" by chapter
    ("system", 0x21323, 6, 2, "p16"),    # save slot lines
    ("system", 0x1F1B2, 6, 2, "p16"),    # level-up stat names
]
# `LDA #lo/hi : STA $10|$14` with `LDA #bank : STA $12|$16` close by (text pointer in direct page)
IMM = re.compile(rb"\xa9(..)\x85([\x10\x14])", re.S)
# a call between the pointer and a bank store ends the call setup: JSL, or JSR (not the $20 of REP/SEP #$20)
JSL = re.compile(rb"\x22..[\xc0-\xef]|(?<![\xc2\xe2])\x20..", re.S)
# `LDY #1 : LDA #lo/hi : STA [$28],y` ... `LDY #3 : LDA #bank : STA [$28],y` (battle messages built in RAM)
IMM28 = re.compile(rb"\xa0\x01\x00\xa9(..)\x97\x28\xe2\x30\xa0\x03\xa9(.)\x97\x28", re.S)
CODE = [(0x000000, 0x040000), (0x2A0000, 0x2C0000)]  # banks $C0-$C3, $EA-$EB (code; $EA:0F98 = game over)
# where text lives (docs/re/text.md): code/data banks $C1-$C3, scripts $C4-$C6 and $EA. Every textscan run in
# here must be an entry (the coverage test); runs elsewhere are font and graphics data that happen to decode.
TEXT_RANGES = [(0x010000, 0x040000), (0x047800, 0x070000), (0x2A3540, 0x2C0000)]
NOT_TEXT = {0x025F69: "item record bytes before the first item name"}


def text_end(rom, p, maxlen=2048):
    """End offset of a well-formed string at p (glyphs/controls up to {end}), else 0."""
    s = p
    while p - s < maxlen and p + 1 < len(rom):
        w = rom[p] | rom[p + 1] << 8
        if w == 0x8000:
            return p + 2
        if w < 0x032A:
            p += 2
        elif 0x8001 <= w <= 0x800F:
            p += 2 + 2 * CTRL_ARGS.get(w, 0)
        else:
            return 0
    return 0


def imm_refs(rom):
    """{text offset: ['imm:LO/BANK', ...]} from code that loads a text pointer as immediates."""
    refs = {}
    for lo, hi in CODE:
        for m in IMM.finditer(rom, lo, hi):
            # the bank is the `STA dp+2` of the same call setup: the next one unless a JSL comes first, else the
            # previous one with no JSL in between; it must store an `LDA #bank` of a ROM bank
            sta = re.compile(rb"\x85" + bytes([m[2][0] + 2]))
            after = sta.search(rom, m.end(), m.end() + 24)
            if after and JSL.search(rom[m.end():after.start()]):
                after = None
            before = list(sta.finditer(rom, m.start() - 24, m.start()))
            if before and JSL.search(rom[before[-1].end():m.start()]):
                before = []
            b = after or (before[-1] if before else None)
            if not b:
                continue
            if rom[b.start() - 2] == 0xA9:  # LDA #bank (8-bit A)
                bank = b.start() - 1
            elif rom[b.start() - 3] == 0xA9 and rom[b.start() - 1] == 0:  # LDA #$00bb (16-bit A)
                bank = b.start() - 2
            else:
                continue
            if not 0xC0 <= rom[bank] <= 0xEF:
                continue
            t = vm.off(rom[bank] << 16 | int.from_bytes(m[1], "little"))
            if text_end(rom, t) > t + 2:
                refs.setdefault(t, []).append(f"imm:{m.start() + 1:06X}/{bank:06X}")
        for m in IMM28.finditer(rom, lo, hi):
            t = vm.off(m[2][0] << 16 | int.from_bytes(m[1], "little"))
            if text_end(rom, t):
                refs.setdefault(t, []).append(f"imm:{m.start() + 4:06X}/{m.start() + 12:06X}")
    return refs


def table_refs(rom):
    """{text offset: (file, ['p16:..'|'p24:..'])} from TABLES."""
    refs = {}
    for name, base, n, stride, kind in TABLES:
        for i in range(n):
            p = base + stride * i
            if kind == "p16":
                t = p & 0x3F0000 | rom[p] | rom[p + 1] << 8
            else:
                t = vm.off(int.from_bytes(rom[p:p + 3], "little"))
            assert text_end(rom, t), f"{name} entry {i} at {p:06X} -> {t:06X} is not text"
            refs.setdefault(t, (name, []))[1].append(f"{kind}:{p:06X}")
    return refs


def in_text_ranges(s):
    return any(a <= s < b for a, b in TEXT_RANGES)


def code_file(t):
    return "battle" if t >= 0x2A0000 or 0x1E000 <= t < 0x20000 or 0x30000 <= t < 0x40000 else "system"


def chapter_of(rom, addr):
    """Chapter whose script block holds `addr` (blocks start at the chapter table entries, $C0:C9F0)."""
    starts = sorted((vm.off(int.from_bytes(rom[0xC9F0 + 3 * c:0xC9F3 + 3 * c], "little")), c)
                    for c in range(vm.CHAPTERS))
    return max(((s, c) for s, c in starts if s <= addr), default=(0, None))[1]


def collect(rom, table):
    """{file name: [entry]}: every string reached by a pointer, plus unreferenced script-bank strings."""
    found = {}  # text offset -> (file, ptrs)
    for t, sites in vm.text_refs(rom).items():  # filed under the chapter whose bytecode shows it
        found[t] = (f"ch{chapter_of(rom, min(sites)):02d}", [f"vm:{s:06X}" for s in sites])
    for t, (name, ptrs) in table_refs(rom).items():
        found.setdefault(t, (name, []))[1].extend(ptrs)
    for t, ptrs in imm_refs(rom).items():
        found.setdefault(t, (code_file(t), []))[1].extend(ptrs)
    for s, e in textscan.runs(rom, 3, 2):  # strings no pointer reaches: kept (unused) so coverage accounts for them
        if s not in found and in_text_ranges(s) and s not in NOT_TEXT:
            found[s] = (code_file(s) if s < 0x40000 else f"ch{chapter_of(rom, s):02d}", [])
    files = {}
    for t in sorted(found):
        name, ptrs = found[t]
        end = text_end(rom, t)
        text, _ = table.decode(rom, t, end - t - 2)
        e = {"id": f"{name}.{t:06X}", "addr": f"{t:06X}", "len": end - t, "ptrs": sorted(set(ptrs)), "jp": text,
             "en": ""}
        boxes = {BOX[rom[int(p[3:], 16) - 2]] for p in ptrs if p.startswith("vm:")}
        if boxes:
            e["box"] = "/".join(sorted(boxes))
        if not ptrs:
            e["unused"] = True
        if not table.encode(re.sub(r"\{[^}]*\}|　", "", text)):
            e["notext"] = True  # controls / blanks only (box setup, cursor positions): nothing to translate
        files.setdefault(name, []).append(e)
    return files


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--force", action="store_true", help="overwrite existing script files (loses English)")
    a = ap.parse_args()
    rom, table = ROM.read_bytes(), Table.load(ROOT / "tbl" / "jp.tbl")
    files = collect(rom, table)
    n = sum(map(len, files.values()))
    flag = lambda k: sum(e.get(k, False) for f in files.values() for e in f)  # noqa: E731
    print(f"{n} strings in {len(files)} files, {flag('unused')} unused, {flag('notext')} control-only")
    if a.write:
        SCRIPT.mkdir(exist_ok=True)
        for name, entries in files.items():
            path = SCRIPT / f"{name}.json"
            if path.exists() and not a.force:
                print(f"keep {path.relative_to(ROOT)} (exists; --force overwrites)")
                continue
            path.write_text(json.dumps(entries, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
