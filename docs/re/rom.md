# ROM layout

- Header `$FFC0`: title `FARLANDSTORY2`, map `$31` (HiROM + FastROM), type `$02` (ROM + RAM + battery), size
  byte `$0C` (4 MiB) although the file is 3 MiB (`0x300000`), SRAM `$03` (8 KiB), region `$00` Japan,
  checksum `$98 0A` / complement `$67 F5`.
- Banks `$C0-$EF` = file `0x000000-0x2FFFFF`. Code in `$C0-$C2` (engine, VM, battle), fonts and chapter
  scripts 0-29 in `$C4-$C6`, scripts 30-38 in `$EA`; the rest is graphics/maps (largely LZ, `compression.md`).

## Free space (verified by scan, not by trap-and-tour)

- No run of `$00`/`$FF` longer than 723 bytes in the whole 3 MiB file (total of runs >= 200 bytes: 6.5 KB).
  Largest: `0x4753F` (705 bytes after the 16x16 font, before the scripts), `0x2E2752` (723), `0x42E1E` (484).
- **Plan: expand to 4 MiB** (banks `$F0-$FF`, file `0x300000-0x3FFFFF`, 1 MiB). The header already declares
  4 MiB, so no header change is needed for mapping; the release step fixes the checksum. Script text uses
  24-bit pointers, so it can move there wholesale. Check in phase 3/5 that nothing mirrors into `$F0-$FF`
  (a 3 MiB image on a 4 MiB map: some emulators mirror `$E0-$EF` there).
