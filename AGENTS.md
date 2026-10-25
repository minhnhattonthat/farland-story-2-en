# Farland Story 2 (SNES) English translation

Skill: translate-retro-game (Claude Code: plugin, enabled in .claude/settings.json; other agents: `<SKILL_DIR>/SKILL.md`; `$SKILL` = the directory holding its SKILL.md, printed by `python tools/skill.py`). Read it before ROM, text or QA work.

## Commands (run from repo root)
- Build:    `python -X utf8 tools/build.py`        -> build/farland2_en.sfc (checks the dump against `rom.sha1` first; not written yet, phase 3)
- Check:    `python -X utf8 tools/check.py`  (tests + lint; the pre-commit hook runs this)
- Smoke:    `python -X utf8 $SKILL/scripts/emu.py build/farland2_en.sfc --out work/qa/smoke --route tools/routes/boot.txt --smoke`
- Warp:     `python -X utf8 $SKILL/scripts/emu.py build/farland2_en.sfc --out work/qa/warp --script tools/debug/warp.lua --var "SCENE='<name>'" --frames 900 --sheet` (scenes: `tools/debug/scenes.lua`, phase 2; never ask the user to play to a scene)
- Release:  `python -X utf8 tools/release.py` (patch + verify; never publish without the user)
- Clean:    `python -X utf8 tools/clean.py` (published projects: lists rebuildable/downloadable files; `--yes` deletes)

## Paths
- Original ROM: `rom/Farland Story 2 (Japan).sfc` (gitignored; SHA-1 in `rom.sha1`, checked by `tools/check_rom.py`). HiROM+FastROM (map $31), 3 MiB, 8 KiB SRAM, no copier header.
- Emulator: this repo's own MesenCE in `tools/mesen/` (release 2.2.1, https://github.com/nesdev-org/MesenCE/releases/download/2.2.1/Mesen_2.2.1_Windows.zip, via `$SKILL/scripts/fetch_emu.py mesen`; gitignored; GUI settings with key mappings in `tools/emu-config/mesen-settings.json`, copy to `tools/mesen/settings.json` on a fresh clone). Savestates: `work/states/`.
- Text: `script/` (format decided in phase 4). Tables: `tbl/`. Glossary: `glossary.md`. RE notes index: `docs/re/README.md`. Fonts and their licences: `docs/fonts.md`.
- `tools/tbl.py`, `bps.py`, `romdiff.py` are copies from `$SKILL/scripts/` so a clone builds without the skill.

## Rulings
- Edit source files (.py .lua .asm .tbl .json) only with the file-edit tool; scripts here read and analyse, never `.replace()` and write back.
- Subagents: dispatch the `.claude/agents/` types (translator, reviewer, visual-qa, playtester), never general-purpose: their short tool list cuts each agent's start-up context from ~43k to ~9k tokens.
- The user's decisions, with the options and reasons: `docs/decisions.md`. Read it before asking the user anything; add each new ruling there the same session.
- Player bug reports: GitHub issues (`gh issue list --label bug`). Copy the attached save into `work/states/`, reproduce in the emulator, fix, commit with `Fixes #N`, and update `docs/status.md`.
- The guard hook is wired in `.claude/settings.json` via `$HOME/.claude/plugins/marketplaces/...` (the plugin's own hook doesn't load in every Claude profile). Canary: `sed -i s/a/a/ hook-canary.py` must be blocked.
- Cold boot reaches the title at ~1000 frames (logos + intro); Start opens the New/Continue menu (`tools/routes/boot.txt`).

## Status
`docs/status.md`: done, next, open bugs. Update it at the end of every session.
