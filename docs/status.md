# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 5 (engine spike and marker build) done 2026-10-25. Next: phase 6 (translate).
- **Done (phase 1):** prior work mined (`docs/re/prior-work.md`); `tbl/jp.tbl` verified; text map, script VM pointers,
  fonts, LZ codec, graphics-text survey (`docs/re/`). Tools: `textscan.py`, `fontsheet.py`, `lz.py`, `lzscan.py`,
  `gfxsweep.py`; tests in `tests/test_recon.py`.
- **Done (phase 2):** `tools/debug/warp.lua` + `scenes.lua` (notes `docs/re/debug.md`), every chapter, STAGE card,
  battle-map menu, shop, save/load, settings, battle, game over, ending, credits. `tools/debug/regen.py` warps them
  all (`--out`, `--script` probe, `--hold N` = keep clicking A through the scene's text, `--shot-every`).
- **Done (phase 3):** `tools/build.py --identity`: output byte-identical to the dump (`tests/test_build.py`).
- **Done (phase 4):** `script/*.json`, 1907 strings in 46 files (8 more since phase 4: `imm` bank-site fix,
  `docs/re/vwf.md`), found through pointers (`docs/re/text.md` §Extraction).
- **Done (phase 5):** `docs/re/vwf.md`.
  - VWF for all text: `fonts/vwf.txt` (drawn, MIT), `tools/font.py` (binaries, English table = jp.tbl controls +
    glyph i -> word `$0400+i`, `text_width`), `asm/vwf.asm` (2 hooks in `$C0:2C33`, code/data `$F0`, RAM `$1E80`;
    asar 1.91 in `tools/asar/`). JP symbols/digits/A-Z also draw with the VWF font.
  - `build.py`: 4 MiB, strings in place when they fit, else relocated to `$F2-$FF` with pointers rewritten by
    kind; p16 tables with English move whole to `$F1` and their bank immediates are patched. `--marker`
    (`tools/marker.py`), `--qa ID=TEXT`, `--out`. Test: `tests/test_engine.py` follows every pointer.
  - Width gate: `data/windows.json` (`tools/windows.py`: `budget(entry)`; no args = report). Dialogue boxes
    (upper/lower/centre) 143 px a line, 136 on the line before `{wait}` (arrow), 3 lines (torture + arrow shots
    `work/qa/p5m`); battle messages 111 (fragments share the line with a name); unit names 71 px and at most 16
    characters (battle name line + name template); classes 79; item names 63 (9-cell lists); item_desc 143x3;
    objectives 143; status labels 71 and other row-sharing fields in `override`; other system strings from their
    window seen in the tour (`tools/lua/textlog.lua`), 47 tagged guesses in `static` (level-up, post-battle and
    error messages no warp shows yet).
  - Fixed on the way: p16 reads at a later table entry (save slots), the battle name template that let a long
    name clobber its terminator (hang after the first battle; `build.TEMPLATES`, `docs/re/vwf.md`).
  - Marker tour: `work/qa/marker` (all 92 scenes, `--hold 1500`); `tools/marker.py --check ROM work/qa/marker`
    lists drawn strings still Japanese. Warp scenes keyed to a JP string address follow `<rom>.reloc.txt`.
    Stage cards can miss under 6 parallel jobs (stage03 once); rerun alone.
- **Next (phase 6):** translator brief must give the budgets (`windows.budget`), and box text should be wrapped by
  a tool (pixel widths: `font.text_width`), not by translators. Glossary names first (D2). `en` may use `　` (6 px)
  for alignment. `battle.01ED47` ("LV") should start with `{pos:09000000}` so LV stays in its column after a
  variable-width name.
- **Engine work queued for phase 7:** item list and shop list windows are 9 cells (63 px for names: "Bastard Sword"
  needs 75). Window opens are `LDA #x/#y/#w/#h : STA $10/$11/$14/$15 : JSL $C2:1FC4` (36 call sites, record at
  `$7E:D58C + 11*depth`). Widening the shop list (`$C1:3137`, x/w immediates at `0x01313A`/`0x013142`, 9 -> 12)
  garbled the top of the screen (`work/qa/widen2`): window buffers/VRAM slots look fixed-size; needs RE of the
  allocation (`$C2:257F`). Until then, item names over 63 px are flagged, not abbreviated (D4).
- **Known limits of the warp:** warped chapters get dummy party members; chapters 20, 34-38 run on chapter 19's /
  33's map; later-chapter commands and post-battle level-up/item messages have no scene yet (`docs/re/debug.md`).
- **Known extraction gap:** `system.016496` "はげんきになった！" has no pointer found (kept, flagged `unused`).
- **Open bugs:** none.
- **Waiting on the user:** nothing.
