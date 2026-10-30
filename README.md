# Farland Story 2 English translation

Unofficial English fan translation of **Farland Story 2** (Super Famicom, Banpresto / TGL, 1995): the source text and tools
that build the patch.

**Just want to play?** Download the patch from [Releases](../../releases) and follow its README. This repository holds
no game data you can play; you need your own dump of the Japanese game.

**Found a bug?** [Report it](../../issues/new/choose): untranslated text, typos, overflow, crashes. Attaching a savestate
helps most.

## Translation status

| Part | Status |
|---|---|
| Dialogue / story (every chapter, STAGE cards, ending) | Translated |
| Battle messages, items, units, classes, shops, status/save/settings screens, GAME OVER | Translated |
| Title menu and unit/map command menus (drawn as graphics) | Translated |
| Title logo | Left in Japanese (katakana logo; the English "FARLAND STORY 2" sub-logo below it names the game) |
| Staff roll | Translated |

Known issues: none known; [report one](../../issues/new/choose).

## What's here

| Path | What it is |
|---|---|
| `script/` | Every text block: original Japanese and English. Translation fixes go here. |
| `glossary.md` | Binding names, terms and style rules. |
| `tools/` | Python build chain: extract, insert, lint, release. |
| `tests/` | pytest suite (ROM-dependent tests skip when the ROM is absent). |
| `docs/re/` | Reverse-engineering notes. |
| `docs/decisions.md`, `docs/status.md` | Rulings with their reasons; current progress and open bugs. |
| `docs/fonts.md` | Fonts used and their licences. |
| `AGENTS.md` | Instructions for coding agents (`CLAUDE.md` points to it). |
| `.claude/agents/` | Subagent types (translator, reviewer, visual QA, playtester) with only the tools each needs. |

## Build your own patched ROM

Needs Python 3.12+ and your own dump of the Japanese game.

```sh
git clone https://github.com/minhnhattonthat/farland-story-2-en
cd farland-story-2-en
# copy your dump to: rom/Farland Story 2 (Japan).sfc
#   (3,145,728 bytes, SHA-1 fc2c596cc601e7d7dbb4abc7262bc91b97a5ceb7; the build refuses any other dump, see rom.sha1)
python -X utf8 tools/build.py                          # -> build/farland2_en.sfc
python -X utf8 tools/check.py                          # tests + text lint
```

## Support

If you enjoy this translation, you can support my work on Ko-fi:

[![Support me on Ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/minhnhattonthat)

## Licence

Tools and English translation: MIT. The original Japanese text in `script/` is Banpresto's and is included only so
the translation can be checked against it. Farland Story 2 is (c) Banpresto; this project is not affiliated with them.
Do not share patched ROMs.

The translation was made with extensive AI assistance (Claude by Anthropic). Corrections are very welcome.
