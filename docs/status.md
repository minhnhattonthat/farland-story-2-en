# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 3 (identity build) done 2026-10-25. Next: phase 4 (extract).
- **Done (phase 1):** prior work mined (`docs/re/prior-work.md`); `tbl/jp.tbl` verified; text map, script VM pointers,
  fonts, LZ codec, graphics-text survey (`docs/re/`). Tools: `textscan.py`, `fontsheet.py`, `lz.py`, `lzscan.py`,
  `gfxsweep.py`; tests in `tests/test_recon.py`.
- **Done (phase 2):** `tools/debug/warp.lua` + `scenes.lua` (notes `docs/re/debug.md`): title, every chapter
  start (`ch00`-`ch38`), every STAGE card (`stage01`-`stage25`), battle map + unit menu, move, post-move menu,
  weapons, items, item use/sell, exchange, unit/enemy status (Y), shop (+ buy prompt, no-money message), map menu,
  objective, save (+ confirm), load, settings, phase banners, battle scene, game over, ending, credits, THE END.
  `tools/debug/regen.py` warps them all from a cold boot (shots `work/qa/warp/shots/`, states `work/states/`).
- **Done (phase 3):** `tools/build.py [--identity]`: unpacks 2269 text runs (textscan) + 285 LZ blocks (lzscan),
  repacks (text re-encoded via `tbl/jp.tbl`; a block recompressed only if its data changed), output byte-identical
  to the dump (`tests/test_build.py`, also checks all 285 blocks recompress in place, ~40 s). Smoke ok.
- **Next (phase 4, extract):** script format in `script/` (JSON per chapter/table, `id`/`ptr`/`jp`/`en`/...),
  derived from pointers, not the textscan heuristic: VM opcode arg counts from the handlers (`$C0:CEEE`), the ~42
  script strings with no direct pointer, `$C1` inline-string sites, `$C2` record layouts (`docs/re/text.md` §Open
  questions). Then switch `build.py` `unpack`/`repack` to the script files and keep `test_identity` green
  (the in-place text writer and the 11 cross-alignment overlapping runs go away then). Roundtrip + coverage tests.
- **Known limits of the warp:** warped chapters get dummy party members (copies of the hero; party size found
  by search), and chapters 20, 34-38 run their script on chapter 19's / 33's map (`load` in `scenes.lua`), so
  battle-map scenes all use stage 1 from a real New Game; later-chapter commands (Warp, Special Attack, Gather, World Map, Unit) and
  post-battle level-up/item messages have no scene yet (`docs/re/debug.md` §Not covered).
- **Open bugs:** none.
- **Waiting on the user:** nothing.
