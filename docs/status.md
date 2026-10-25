# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 4 (extract) done 2026-10-25. Next: phase 5 (engine spike and marker build).
- **Done (phase 1):** prior work mined (`docs/re/prior-work.md`); `tbl/jp.tbl` verified; text map, script VM pointers,
  fonts, LZ codec, graphics-text survey (`docs/re/`). Tools: `textscan.py`, `fontsheet.py`, `lz.py`, `lzscan.py`,
  `gfxsweep.py`; tests in `tests/test_recon.py`.
- **Done (phase 2):** `tools/debug/warp.lua` + `scenes.lua` (notes `docs/re/debug.md`): title, every chapter
  start (`ch00`-`ch38`), every STAGE card (`stage01`-`stage25`), battle map + unit menu, move, post-move menu,
  weapons, items, item use/sell, exchange, unit/enemy status (Y), shop (+ buy prompt, no-money message), map menu,
  objective, save (+ confirm), load, settings, phase banners, battle scene, game over, ending, credits, THE END.
  `tools/debug/regen.py` warps them all from a cold boot (shots `work/qa/warp/shots/`, states `work/states/`).
- **Done (phase 3):** `tools/build.py --identity`: output byte-identical to the dump (`tests/test_build.py`).
- **Done (phase 4):** `script/*.json`, 1899 strings in 46 files (`ch00`-`ch38`, `units`, `classes`, `objectives`,
  `items`, `item_desc`, `system`, `battle`), found through pointers: `tools/vm.py` walks the script bytecode
  (arg lengths read off the handlers, plus the per-chapter talk-script tables at `$C0:CCBA`), `tools/extract.py`
  adds the `$C2` tables and code immediates (`imm:` with the bank immediate's offset). Format and pointer kinds:
  `docs/re/text.md` §Extraction. `build.py` now builds from the script files (`en`, else `jp`, in place);
  `--identity` extracts from the dump. Tests: roundtrip, files == fresh extraction, coverage of the text ranges,
  no overlaps, VM walk, identity. `tbl/jp.tbl` gained `$22` ▶, `$24` ▼, `$25` ↓ and `{gXX}` for blank glyphs.
- **Next (phase 5, marker build):** font/VWF decision (dialogue is 16x16 full-width, menus 8x16 half-width; an
  8x16 ASCII font already exists at `$C4:0000` for `$00-$F0`), English table + encoder, every string replaced by
  `[id]` markers (needs relocation: strings are short in place; plan 4 MiB expansion `docs/re/rom.md`, rewrite
  `vm`/`p24`/`p16`/`imm` pointers by kind), measure each window width in-game (`box` field: upper/lower/centre,
  menus) with the warp scenes, find non-text "strings" that show up. Entries flagged `notext` (controls only) and
  `unused` (no pointer) need no translation.
- **Known limits of the warp:** warped chapters get dummy party members (copies of the hero; party size found
  by search), and chapters 20, 34-38 run their script on chapter 19's / 33's map (`load` in `scenes.lua`), so
  battle-map scenes all use stage 1 from a real New Game; later-chapter commands (Warp, Special Attack, Gather, World Map, Unit) and
  post-battle level-up/item messages have no scene yet (`docs/re/debug.md` §Not covered).
- **Known extraction gap:** `system.016496` "はげんきになった！" has no pointer found (kept, flagged `unused`).
- **Open bugs:** none.
- **Waiting on the user:** nothing.
