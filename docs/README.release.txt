Farland Story 2 (SNES) - English Translation v{VERSION}
=======================================================

An unofficial fan translation of Banpresto / TGL's 1995 Super Famicom strategy RPG
"Farland Story 2" into English.

Translated:
- The whole story: every chapter's dialogue, the STAGE cards, the ending and the
  staff roll.
- Battle messages, level-ups, item and unit names, classes, shops, the status,
  save/load and settings screens, GAME OVER.
- The title menu (New Game / Continue / Settings) and the unit and map command
  menus, which the original draws as graphics.

A variable-width font replaces the Japanese 16x16 text, and the ROM is expanded
to 4 MiB to make room for the English.

Applying the patch
------------------
Apply FarlandStory2_EN_v{VERSION}.bps to an unmodified, unheadered dump with
Flips, Beat or RomPatcher.js (https://www.marcrobledo.com/RomPatcher.js/).

Base ROM: Farland Story 2 (Japan).sfc (No-Intro), 3,145,728 bytes
  {BASE}
Patched ROM: 4,194,304 bytes
  {PATCHED}

If your file is 3,146,240 bytes it has a 512-byte copier header: remove it first.

Notes
-----
- Tested in Mesen 2.2.1. Start from a fresh boot: save states made with the
  Japanese game carry the old text engine.
- Names follow earlier English fan work on the series where it exists (Ark,
  Felsaria, Valdes Empire...).

Known issues
------------
- The katakana title logo is kept; the English "FARLAND STORY 2" sub-logo below
  it already names the game.

Credits
-------
Translation, hacking and tools: minhnhattonthat, with AI assistance (Anthropic
Claude). Thanks to Bongo for the table, trace notes and menu-patch layout of the
abandoned 2006 project, and to Eien Ni Hen for the chapter 1-10 script used as a
name reference.

Bug reports: https://github.com/minhnhattonthat/farland-story-2-en/issues

This is an unofficial fan work, not affiliated with Banpresto or TGL.
Do not distribute pre-patched ROMs.
