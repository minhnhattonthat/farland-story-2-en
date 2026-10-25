"""winsites.py: every window-open call (`JSL $C2:1FC4`) with the x/y/w/h immediates stored before it.

The game opens a window with `LDA #imm : STA $10/$11/$14/$15` (8- or 16-bit A) then `JSL $C2:1FC4`. Prints one
line per call site: CPU address, then each field with the file offset of its immediate byte (to patch widths).

    python -X utf8 tools/winsites.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import build

CALL = bytes.fromhex("22c41fc2")
FIELDS = {0x10: "x", 0x11: "y", 0x14: "w", 0x15: "h"}


def sites(rom):
    """[(call offset, {field: (value, immediate offset)})] for the code banks $C0-$C3."""
    out, i = [], 0
    while (i := rom.find(CALL, i, 0x40000)) >= 0:
        got, j = {}, i - 1
        while j > i - 48 and len(got) < 4:
            # STA dp (85 dd) preceded by LDA #imm8 (A9 ii) or LDA #imm16 (A9 lo hi: the low byte is the field,
            # the high byte the next field when 16-bit A stores a pair)
            if rom[j - 1] == 0x85 and rom[j] in FIELDS:
                dp = rom[j]
                if rom[j - 3] == 0xA9:      # 8-bit
                    got.setdefault(FIELDS[dp], (rom[j - 2], j - 2))
                if rom[j - 4] == 0xA9:      # 16-bit: low byte -> dp, high byte -> dp+1
                    got.setdefault(FIELDS[dp], (rom[j - 3], j - 3))
                    if dp + 1 in FIELDS:
                        got.setdefault(FIELDS[dp + 1], (rom[j - 2], j - 2))
            j -= 1
        out.append((i, got))
        i += 1
    return out


def main():
    rom = build.ROM.read_bytes()
    for at, got in sites(rom):
        print(f"{build.cpu(at):06X}", " ".join(f"{k}={v:2d}@{o:06X}" for k, (v, o) in sorted(got.items())))


if __name__ == "__main__":
    main()
