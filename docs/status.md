# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 1 (research and recon) done 2026-10-25. Next: phase 2 (debug tool). No build yet.
- **Done (phase 1):** Bongo's abandoned 2006 project found and mined (`docs/re/prior-work.md`); `tbl/jp.tbl`
  verified glyph by glyph against the font (9 fixes) with all 16 control codes from the dispatch table; text map
  (script bytecode with 24-bit pointers in `$C4-$C6`/`$EA`, struct tables in `$C2`, inline strings in `$C1`);
  fonts (16x16 + 8x16 half-width, upper-case only); LZ codec + 285-block list; no free space -> expand to 4 MiB;
  graphics-text survey from tour + static sweep (`docs/re/graphics.md`). Tools: `textscan.py`, `fontsheet.py`,
  `lz.py`, `lzscan.py`, `gfxsweep.py`; tests in `tests/test_recon.py`.
- **Next (phase 2, debug tool):** cold boot reaches the first battle map only after ~14000 frames of intro, and
  menus need real cursor play. Find the chapter variable (`$03B1` is read by the chapter loader `$C0:C9C3`) and
  a way to start any chapter / battle / ending from boot (RAM poke at the right moment, or the script table
  `$C0:C9F0`). Scene list must cover: title menu, each chapter's STAGE card, map menu (ターン終了...), unit
  command menu, status screen, shop, battle scene, save/load screens, game over, ending + credits.
- **States:** `work/qa/tour2/s004000.mss` etc. = first battle map (chapter 0), gitignored.
- **Open bugs:** none.
- **Waiting on the user:** nothing.
