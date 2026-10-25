# Reverse-engineering notes

One file per subsystem (text engine, pointers, compression, font, graphics). Mark every finding with how far it is
proven, so a later session doesn't build on a guess:

- **verified** - and how: a decoded known string, a corrupt-and-boot test, a breakpoint hit on the drawing path, a
  passing roundtrip test. Name the test or savestate.
- **guess** - and why it seems likely (byte pattern, another game, an earlier patch's notes). Promote it to verified
  before code depends on it.

Addresses are for the dump in `rom.sha1` unless a note says otherwise.

| File | Covers | State |
|---|---|---|
| [prior-work.md](prior-work.md) | Bongo's abandoned project (tables, notes, menu IPS), Eien Ni Hen's partial script | done |
| [rom.md](rom.md) | header, bank map, free space, 4 MiB expansion plan | verified (scan) |
| [text.md](text.md) | encoding, control codes, script VM, extraction (every pointer form and table) | verified (`tests/test_recon.py`, `tests/test_build.py`: roundtrip, coverage, VM walk) |
| [font.md](font.md) | 16x16 and 8x16 fonts | verified (rendered + draw code) |
| [compression.md](compression.md) | LZ codec, block list | verified (`tools/lz.py`, test) |
| [graphics.md](graphics.md) | graphics-text survey (tour + static sweep) | see file |
| [debug.md](debug.md) | game state RAM, warps, menus, shop, game over: the debug tool's basis | verified (warps reach every scene, `tools/debug/regen.py`) |

Tools: `tools/extract.py` (script dump), `tools/vm.py` (script bytecode walker), `tools/textscan.py` (text runs), `tools/fontsheet.py` (font vs table), `tools/lz.py` + `tools/lzscan.py`
(LZ blocks), `tools/gfxsweep.py` (static graphics sheets).
