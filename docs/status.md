# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 8 (QA in the emulator) in its last gate run 2026-10-25; then phase 9 (release, `tools/release.py`).
- **Done (phase 1-6):** recon (`docs/re/`), debug warp (`tools/debug/`, `docs/re/debug.md`), identity build,
  extraction (`script/*.json`, `docs/re/text.md`), VWF engine + relocation + marker build + width gate
  (`docs/re/vwf.md`, `data/windows.json`), full English script (`tools/batches.py`, `tools/wrap.py`, D9-D11).
- **Done (phase 7):** build gate green (`tools/check.py`: 31 tests; lint, romdiff + write log, hookcheck).
- **Done (phase 8):**
  - Graphics text: G2 title menu and G3 command labels in English (`tools/gfx.py`, glossary §Menu labels,
    `docs/re/graphics.md`); G1 katakana logo kept (D5).
  - QA pipeline: `tools/qa_tour.py` = 92 warp scenes + per-page tour of all 39 chapters (`tools/lua/pageshot.lua`)
    + string viewer for the 595 box strings no chapter start shows (`tools/viewer.py`, `tools/coverage.py`)
    + contact sheets (`tools/qa_sheets.py`) + `qa_gate.py init` (`work/qa/p8/manifest.tsv`, verdicts in
    `work/qa/p8/verdicts/`); writes `work/qa/p8/rom.sha1` = the build it shot. Reviewer brief
    `docs/visual-qa-brief.md`.
  - Fixed from 3 review rounds: STAGE cards (lost `{nl}`), GAME OVER (second copy `$EA:0FF4`, extractor code
    range widened), THE END spacing, VWF `{pos}`/`{clr}` reset (`asm/vwf.asm`), warp party record 0 (ch02 portrait
    garbage), wrap widows / one-line last pages (`tools/wrap.py`), ch08/ch14/ch20 lines.
- **Next:** when the running tour (`work/qa/p8/qa_tour5.log`) ends: `qa_gate.py todo work/qa/p8/manifest.tsv
  work/qa/p8/verdicts --out-dir work/qa/p8/chunks`, one visual-qa agent per chunk, fix issues, repeat until
  `qa_gate.py check` exits 0. Then phase 9: `python -X utf8 tools/release.py` (build, check, smoke, jp_left over
  every English span, gate tied to the toured sha1, BPS re-applied, zip in `release/`). Never publish.
- **Cosmetic, allowed by the wrap rules:** "the Dance / of Ruin" splits across lines (ch29 and viewer pages).
- **Known limits of the warp:** warped chapters get dummy party members; chapters 20, 34-38 run on chapter 19's /
  33's map; later-chapter commands and post-battle level-up/item messages have no scene (the viewer shows them).
- **Known extraction gap:** `system.016496` "はげんきになった！" has no pointer found (kept, flagged `unused`).
- **Open bugs:** none.
- **Waiting on the user:** nothing blocking. Non-blocking: D9 (register, SFX), D10 (fan spellings like Serena,
  Cifil, Lodoss kept per D2; 破亡の舞 = "Dance of Ruin") were controller defaults; override any in docs/decisions.md.
