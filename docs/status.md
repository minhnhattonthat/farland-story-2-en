# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 2 (debug tool) done 2026-10-25. Next: phase 3 (identity build). No build yet.
- **Done (phase 1):** prior work mined (`docs/re/prior-work.md`); `tbl/jp.tbl` verified; text map, script VM pointers,
  fonts, LZ codec, graphics-text survey (`docs/re/`). Tools: `textscan.py`, `fontsheet.py`, `lz.py`, `lzscan.py`,
  `gfxsweep.py`; tests in `tests/test_recon.py`.
- **Done (phase 2):** `tools/debug/warp.lua` + `scenes.lua` (notes `docs/re/debug.md`): title, every chapter
  start (`ch00`-`ch38`), every STAGE card (`stage01`-`stage25`), battle map + unit menu, move, post-move menu,
  weapons, items, item use/sell, exchange, unit/enemy status (Y), shop (+ buy prompt, no-money message), map menu,
  objective, save (+ confirm), load, settings, phase banners, battle scene, game over, ending, credits, THE END.
  `tools/debug/regen.py` warps them all from a cold boot (shots `work/qa/warp/shots/`, states `work/states/`).
- **Next (phase 3, identity build):** `tools/build.py`: unpack (text + LZ blocks) and repack with no edits,
  byte-identical to the dump, as a test.
- **Known limits of the warp:** warped chapters get dummy party members (copies of the hero; party size found
  by search), and chapters 20, 34-38 run their script on chapter 19's / 33's map (`load` in `scenes.lua`), so
  battle-map scenes all use stage 1 from a real New Game; later-chapter commands (Warp, Special Attack, Gather, World Map, Unit) and
  post-battle level-up/item messages have no scene yet (`docs/re/debug.md` §Not covered).
- **Open bugs:** none.
- **Waiting on the user:** nothing.
