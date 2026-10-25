# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 9 (release) done 2026-10-26. The run's goal is met: `release/FarlandStory2_EN_v1.0.zip` built and
  verified. Nothing is published (owner's call).
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
    `docs/visual-qa-brief.md`. Each tour re-shoots ~30 sheets differently (typing timing), so expect one short
    review round after any re-tour.
  - 6 review rounds; `qa_gate.py check`: 299 sheets, all ok. Fixed: STAGE cards (lost `{nl}`, indents), GAME OVER
    (second copy `$EA:0FF4`), THE END spacing, VWF `{pos}`/`{clr}` reset, warp party record 0, wrap widows and
    one-line last pages, ch08/ch14/ch20/ch37 lines.
- **Done (phase 9):** `python -X utf8 tools/release.py [--version X.Y] [--force]`: build, check, smoke, `jp_left`
  over every English string's span (0 runs), gate tied to the toured sha1, SNES checksum, BPS re-applied and
  compared, zip (patch + README from `docs/README.release.txt`). v1.0: patch sha1 `f4eccbcb...`, patched ROM
  CRC32 `26D95D60`; playable image `build/farland2_en_v1.0.sfc` (smoke ok).
- **Next:** playtest by the owner; bug reports via GitHub issues (AGENTS.md). Any text/code fix: rebuild,
  `tools/qa_tour.py`, review the changed sheets, then `tools/release.py --version 1.1`.
- **Cosmetic, allowed by the wrap rules:** "the Dance / of Ruin" splits across lines (ch29 and viewer pages).
- **Known limits of the warp:** warped chapters get dummy party members; chapters 20, 34-38 run on chapter 19's /
  33's map; later-chapter commands and post-battle level-up/item messages have no scene (the viewer shows them).
- **Known extraction gap:** `system.016496` "はげんきになった！" has no pointer found (kept, flagged `unused`).
- **Open bugs:** none.
- **Waiting on the user:** nothing blocking. Non-blocking: publishing v1.0 (`gh release create`) is the owner's
  call. D9 (register, SFX), D10 (fan spellings like Serena, Cifil, Lodoss kept per D2; 破亡の舞 = "Dance of
  Ruin") were controller defaults; override any in docs/decisions.md.
