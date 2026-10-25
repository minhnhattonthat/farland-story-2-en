# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 6 (translate) done 2026-10-25. Next: phase 7 (insert, fit, check).
- **Done (phase 1-5):** recon (`docs/re/`), debug warp (`tools/debug/`, `docs/re/debug.md`), identity build,
  extraction (`script/*.json`, `docs/re/text.md`), VWF engine + relocation + marker build + width gate
  (`docs/re/vwf.md`, `data/windows.json`).
- **Done (phase 6):** every string with text has `en` (1772 merged; `unused`/`notext` keep Japanese).
  - Tools: `tools/batches.py` (split/check/merge/pairs, `tests/test_batches.py`), `tools/wrap.py` (box text: one
    paragraph per page, lines broken by pixel width and pages added at build time, D11). `{wait}` pages map 1:1
    to translator pages (` || `).
  - Docs: `docs/synopsis.md` (cast, chapters, reveals), `docs/style-reference.md` (voices, pilot pairs),
    `glossary.md` (names per D2/D10, terms, address forms), `docs/translator-brief.md`, `docs/reviewer-brief.md`,
    decisions D9-D11.
  - Pilot ch00-01, units/classes/items/objectives, battle/system by the controller (b001-b003); b004-b015 by 4
    translator agents; 7 reviewer passes: every Critical/Important fixed, Minors applied in one polish pass.
  - Font: `▶` glyph added (English yes/no lines; the JP menu cursor keeps its own glyph, `font.remap`).
  - Pilot seen in-game (`work/qa/p6`, `p6b`): prologue scroll narration, dialogue, status, settings, save,
    objective, stage card, credits wrap fine.
- **Next (phase 7):** fit and engine work found so far:
  - Item names over 63 px (31, e.g. Bastard Sword 75) and unit names over 71 px (7, e.g. Mini Gibogera 1 75):
    `batches.py check` prints them as `LONG` (fields with `engine` in `data/windows.json`). Widen item/shop
    lists (`$C2:257F` allocation RE, see below) and move LV in the battle name line.
  - Battle name line reads "SerenaLV1": `battle.01ED47` needs `{pos:09000000}` (or similar) so LV keeps its column.
  - Battle messages: fragment + longest name can pass 111 px ("Armor Knight 1 attacks!" cut in `work/qa/p6`
    battle shot); check where the game wraps and fit (lint: fragment + longest unit/item name).
  - Prompts are overdrawn, not cleared: English prompts are padded with `　` (6 px) to cover the previous string
    (save/load/continue prompts in `system`). Check every menu prompt pair in a tour.
  - Yes/No prompt alignment (`system.0214AC`/`0214D0`, `0168BA`, `016B92`) computed for 8-px half-width cells; verify.
  - Lint `tools/batches.py` style checks (width per box/field) over the whole script = the build gate.
- **Engine work queued:** item list and shop list windows are 9 cells (63 px for names). Window opens are
  `LDA #x/#y/#w/#h : STA $10/$11/$14/$15 : JSL $C2:1FC4` (36 call sites, record at `$7E:D58C + 11*depth`).
  Widening the shop list (`$C1:3137`, x/w immediates at `0x01313A`/`0x013142`, 9 -> 12) garbled the top of the
  screen (`work/qa/widen2`): window buffers/VRAM slots look fixed-size; needs RE of the allocation (`$C2:257F`).
- **Known limits of the warp:** warped chapters get dummy party members; chapters 20, 34-38 run on chapter 19's /
  33's map; later-chapter commands and post-battle level-up/item messages have no scene yet (`docs/re/debug.md`).
- **Known extraction gap:** `system.016496` "はげんきになった！" has no pointer found (kept, flagged `unused`).
- **Open bugs:** none.
- **Waiting on the user:** nothing blocking. Non-blocking: D9 (register, SFX), D10 (fan spellings like Serena,
  Cifil, Lodoss kept per D2; 破亡の舞 = "Dance of Ruin") were controller defaults; override any in docs/decisions.md.
