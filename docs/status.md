# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 7 (insert, fit, check) done 2026-10-25. Next: phase 8 (QA in the emulator), starting with the
  graphics-text insertion below.
- **Done (phase 1-6):** recon (`docs/re/`), debug warp (`tools/debug/`, `docs/re/debug.md`), identity build,
  extraction (`script/*.json`, `docs/re/text.md`), VWF engine + relocation + marker build + width gate
  (`docs/re/vwf.md`, `data/windows.json`), full English script (`tools/batches.py`, `tools/wrap.py`, D9-D11).
- **Done (phase 7):** build gate green (`tools/check.py`: 29 tests).
  - `tools/lint.py` = whole-script lint (batch checks: font, pages, control codes, px per line/field, glossary,
    honorifics; + no Japanese in `en`, no untranslated text unless `unused`/`notext`, no widow last line).
    `tests/test_insert.py` runs it, so the pre-commit hook gates on it. `{pos}` args may differ from the JP.
  - `tools/wrap.py`: no widows (pulls a word down when a paragraph's last line is under 6 characters).
  - Item names: every item window widened to 12 name cells / 95 px (`asm/windows.asm`: BG3 window tiles past
    256 move to tile 384; `docs/re/vwf.md` §Window tiles). Verified with 96-px ruler names in shop, items,
    use/sell, exchange, weapons (`work/qa/p7e`).
  - Unit names: LV fixed at cell 10 by the name template's `{pos}` (budget 79 px; "Serena LV1" fixed).
  - Run-time word wrap in the VWF (`vwf_wordfits`): "Armor Knight 1 / attacks!", sell prompt with the longest
    item name (`work/qa/p7f/bt`, `p7h`). " gained " and " sells for " got their space before the number.
  - ROM checks: `build.py` logs every write (`put()`, `build/*.writes.txt`) and fails on any romdiff error
    (`data/romdiff.txt` = assembler ranges); `tools/hookcheck.py`: no branch into a hook; relocated strings
    leave no stale pointer (one-off scan: 68 byte coincidences, none code). All in `tests/test_insert.py`.
  - Tour of all 92 scenes on the build (`work/qa/p7g/shots`, states in `work/qa/p7g/states`): prompts (save,
    load, buy, sell, no gold), Yes/No rows, settings, status, battle lines read right.
- **Next (phase 8):**
  - **Graphics text first** (`docs/re/graphics.md`): G2 title menu (はじめから/つづきから/環境設定, LZ `0x6321`)
    and G3 command menus (unit menu 移動/武器/アイテム/交換/買物, standby 待機, map menu ターン終了/状況/
    セーブ/ロード/環境設定; raw `0xD45EB-0xD5617`, 1bpp rows in odd bytes) are still Japanese in the tour.
    Bongo's IPS layout is the reference (`docs/re/prior-work.md`). G1 logo stays (D5).
  - Then QA per the skill: routes through changed scenes, contact sheets, visual-qa verdicts (`qa_gate.py`),
    `jp_left.py`. `work/states/*.mss` are stale (pre-phase-7 code): regenerate with `tools/debug/regen.py`.
- **Known limits of the warp:** warped chapters get dummy party members; chapters 20, 34-38 run on chapter 19's /
  33's map; later-chapter commands and post-battle level-up/item messages have no scene yet (`docs/re/debug.md`).
- **Known extraction gap:** `system.016496` "はげんきになった！" has no pointer found (kept, flagged `unused`).
- **Open bugs:** none.
- **Waiting on the user:** nothing blocking. Non-blocking: D9 (register, SFX), D10 (fan spellings like Serena,
  Cifil, Lodoss kept per D2; 破亡の舞 = "Dance of Ruin") were controller defaults; override any in docs/decisions.md.
