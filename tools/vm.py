"""Walk the event-script bytecode (VM loop $C0:CEBA, handler table $C0:CEEE) and list every text pointer it holds.

Opcode argument lengths were read off the handlers (docs/re/text.md §Script bytecode). Entry points are the 65816
stubs that load the bytecode pointer (`LDA #bank : STA $9D : REP #$20 : LDA #addr : STA $9B`); the walker follows
every branch target from there. An unknown opcode raises, so a wrong length shows up at once.

    python -X utf8 tools/vm.py            # summary: entries, ops, text pointers
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROM = ROOT / "rom" / "Farland Story 2 (Japan).sfc"

# argument bytes after the 16-bit opcode; None = variable ($26/$27: 1 byte, $FF-terminated list, 1 byte)
ARGS = {0x04: 2, 0x0C: 2, 0x0D: 2, 0x12: 3, 0x13: 1, 0x14: 1, 0x16: 1, 0x17: 1, 0x18: 1, 0x19: 1, 0x1E: 2,
        0x1F: 4, 0x20: 4, 0x21: 1, 0x22: 1, 0x24: 2, 0x25: 2, 0x26: None, 0x27: None, 0x28: 3, 0x29: 3,
        0x2A: 2, 0x2B: 2, 0x2C: 1, 0x2D: 1, 0x32: 1, 0x33: 1, 0x3C: 3, 0x3D: 3, 0x41: 3, 0x42: 3, 0x43: 1,
        0x44: 1, 0x55: 1, 0x56: 1}
# conditional branches: condition bytes, then a 24-bit target (taken) or fall through
BRANCH = {0x48: 1, 0x49: 1, 0x4A: 1, 0x4B: 1, 0x4C: 1, 0x4D: 1, 0x4E: 4, 0x4F: 4, 0x50: 6, 0x51: 6, 0x52: 2,
          0x53: 2, 0x57: 1, 0x58: 1}
GOTO, LAST = 0x54, 0x59
TEXT = {0x3C, 0x3D, 0x41}  # 24-bit text pointer (upper box, lower box, centre)
CHAPTERS, NPC = 39, 0xCCBA
SCRIPT_BANKS = {0xC4, 0xC5, 0xC6, 0xEA}
ENTRY = re.compile(rb"\xa9(.)\x85\x9d\xc2\x20\xa9(..)\x85\x9b", re.S)


def off(cpu):
    return cpu & 0x3FFFFF


def npc_tables(rom):
    """{chapter: [script file offsets]}: talk scripts, `$C0:CC4F` reads table[$03B1 chapter] at `$C0:CCBA`, entry
    [$03C8]. A table runs until its own scripts start (the bytecode follows it)."""
    out = {}
    for ch in range(CHAPTERS):
        base = off(int.from_bytes(rom[NPC + 3 * ch:NPC + 3 * ch + 3], "little"))
        p, ptrs = base, []
        while rom[p + 2] in SCRIPT_BANKS and p < min(ptrs, default=1 << 24):
            ptrs.append(off(int.from_bytes(rom[p:p + 3], "little")))
            p += 3
        out[ch] = ptrs
    return out


def entries(rom):
    """{bytecode file offset: where it is started from} for every VM entry: the 65816 stubs that load the bytecode
    pointer, and the per-chapter talk-script tables."""
    ent = {off(m[1][0] << 16 | int.from_bytes(m[2], "little")): m.start() for m in ENTRY.finditer(rom)
           if m[1][0] >= 0xC0}
    for ch, ptrs in npc_tables(rom).items():
        for p in ptrs:
            ent.setdefault(p, NPC + 3 * ch)
    return ent


def ops(rom, start):
    """Decode one straight-line run from `start`: yields (offset, opcode, arg bytes, branch target or None).
    Stops after $FFFF, a goto or $59 (end of script)."""
    p = start
    while True:
        op = rom[p] | rom[p + 1] << 8
        if op == 0xFFFF:
            yield p, op, b"", None
            return
        if op > LAST:
            raise ValueError(f"bad opcode {op:04X} at {p:06X} (run from {start:06X})")
        a = p + 2
        if op in BRANCH:
            n = BRANCH[op]
            tgt = int.from_bytes(rom[a + n:a + n + 3], "little")
            yield p, op, bytes(rom[a:a + n + 3]), off(tgt)
            p = a + n + 3
        elif op == GOTO:
            yield p, op, bytes(rom[a:a + 3]), off(int.from_bytes(rom[a:a + 3], "little"))
            return
        else:
            n = ARGS.get(op, 0)
            if n is None:
                n = rom.index(b"\xff", a + 1) - a + 2
            yield p, op, bytes(rom[a:a + n]), None
            p = a + n
            if op == LAST:
                return


def walk(rom, starts=None):
    """{op offset: (opcode, args)} for all code reachable from `starts` (default: every entry stub)."""
    todo, seen, code = list(starts or entries(rom)), set(), {}
    while todo:
        s = todo.pop()
        if s in seen:
            continue
        seen.add(s)
        for p, op, args, tgt in ops(rom, s):
            if p in code and p != s:
                break  # joined code already walked
            code[p] = (op, args)
            if tgt is not None:
                todo.append(tgt)
    return code


def text_refs(rom, code=None):
    """{text file offset: [pointer site file offsets]} from the text opcodes."""
    refs = {}
    for p, (op, args) in sorted((code or walk(rom)).items()):
        if op in TEXT:
            refs.setdefault(off(int.from_bytes(args, "little")), []).append(p + 2)
    return refs


def main():
    rom = ROM.read_bytes()
    ent = entries(rom)
    code = walk(rom, ent)
    refs = text_refs(rom, code)
    print(f"{len(ent)} entry stubs, {len(code)} ops, {len(refs)} text targets, "
          f"{sum(map(len, refs.values()))} text pointers")


if __name__ == "__main__":
    main()
