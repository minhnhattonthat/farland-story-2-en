"""hookcheck.py: does any branch or call land strictly inside a code span the assembler overwrote?

Byte scan (no instruction alignment, so it over-reports: read each hit in the disassembly) of +-4 KB around every
code hook listed in data/romdiff.txt with a size > 1 in banks $C0-$C3: rel8 branches, BRL, JMP/JSR abs, JML/JSL.

    python -X utf8 tools/hookcheck.py        # exit 1 on any hit
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import build

REL8 = {0x10, 0x30, 0x50, 0x70, 0x80, 0x90, 0xB0, 0xD0, 0xF0}


def spans():
    out = []
    for line in build.RANGES.read_text(encoding="utf-8").splitlines():
        rng = line.split("#")[0].strip()
        if "-" in rng:
            lo, hi = (int(x, 16) for x in rng.split("-"))
            if hi < 0x40000:
                out.append((lo, hi))
    return out


def hits(rom, lo, hi):
    """[(offset, opcode, target)] for branches into (lo, hi]."""
    found = []
    for i in range(max(0, lo - 0x1000), min(len(rom) - 4, hi + 0x1000)):
        op, t = rom[i], None
        if op in REL8:
            t = i + 2 + (rom[i + 1] - 256 if rom[i + 1] & 0x80 else rom[i + 1])
        elif op == 0x82:
            d = int.from_bytes(rom[i + 1:i + 3], "little")
            t = i + 3 + (d - 0x10000 if d & 0x8000 else d)
        elif op in (0x4C, 0x20):
            t = (i & 0xFF0000) | int.from_bytes(rom[i + 1:i + 3], "little")
        elif op in (0x5C, 0x22):
            t = int.from_bytes(rom[i + 1:i + 4], "little") & 0x3FFFFF
        if t is not None and lo < t <= hi:
            found.append((i, op, t))
    return found


def main():
    rom = build.ROM.read_bytes()
    n = 0
    for lo, hi in spans():
        for i, op, t in hits(rom, lo, hi):
            print(f"{build.cpu(i):06X} op {op:02X} -> {build.cpu(t):06X} inside hook {build.cpu(lo):06X}-{build.cpu(hi):06X}")
            n += 1
    print(f"{n} possible branches into hooks")
    sys.exit(1 if n else 0)


if __name__ == "__main__":
    main()
