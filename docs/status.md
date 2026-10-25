# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** Step 0 (repo setup) done 2026-10-25. Next: phase 1 (research and recon). No build yet.
- **Done:** template filled (AGENTS.md, README, rom.sha1, decisions D1-D8, glossary rulings); MesenCE 2.2.1 in `tools/mesen/`;
  original ROM smoke passes, Start on the title opens the New/Continue menu, Lua probe logs land in `log.txt`, GUI
  default key mappings saved to `tools/emu-config/mesen-settings.json`; guard hook wired in `.claude/settings.json` and
  blocks the canary; pre-commit runs `tools/check.py` and rejects a failing test; `tools/skill.py` prints the skill path;
  `tbl.py`/`bps.py`/`romdiff.py` copied into `tools/`; subagent briefs copied into `docs/`.
- **ROM facts so far:** header title `FARLANDSTORY2`, map $31 (HiROM FastROM), size byte $0C but file 3 MiB, SRAM 8 KiB,
  region Japan. Banpresto / TGL, released 1995-12-22.
- **Next (phase 1):** look for an earlier SFC fan patch (romhacking.net; don't confuse with the PC-98 "Farland Story
  Denki: Arc Ou no Ensei"); find the text encoding (relsearch), font, pointer tables, control codes, compression;
  survey graphics text (title logo, menus, battle UI, chapter cards); write `docs/re/*.md`.
- **Open bugs:** none.
- **Waiting on the user:** nothing.
