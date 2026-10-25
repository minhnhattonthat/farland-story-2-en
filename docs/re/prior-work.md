# Prior work

## Bongo' abandoned project (romhacking.net "Abandoned Projects", 2006, archive dated 2011)

- Source: `http://www.romhacking.net/abandoned/[8]Farland2.zip` (fetched through the Wayback Machine,
  `web.archive.org/web/2020id_/...`; romhacking.net itself answers 403). Unpacked, untrusted, never run:
  `work/dl/bongo/x/Farland2/` (gitignored; re-download with the URL above).
- It is for this SNES game (the PC-98 "Farland Story 2" / Arc Ou no Ensei has its own patch by BTAxis).
- Contents and what we took from it:
  - `FS2j.tbl`: 16-bit table, kana + 554 kanji. Basis of `tbl/jp.tbl`; 9 errors fixed against the font (`text.md`).
  - `Asm/*.rtf`: annotated trace logs. Text draw `$C0:2C53`, script VM `$C0:CEBA`, chapter table `$C0:C9F0`,
    opcode table `$C0:CEEE`, LZ decompressor `$C0:167D`, battle-intro code `$C1:01DA`. All re-checked in our
    disassembly before use (`text.md`, `compression.md`).
  - `Asm/OpCodes.txt`: argument byte counts for the 89 VM opcodes (unverified; some marked "varies").
  - `Tools/`: C++Builder sources for a text dumper (`FS_Text`), script VM walker (`FS2_VM`, with
    `Pointers.txt` for chapter 0), LZ compressor (`FS2_Comp`), 8x8 font masker. Read for format hints only.
  - `ips/FS2_menu95%.ips`: menu patch. Changes LZ block `0x6321` (title menu: Start / Continue / Settings)
    and the raw 2bpp menu label tiles at `0xD45EB-0xD5617` (in-game command menus). Booted on a scratch copy:
    the title menu reads "Start / Continue / Settings". It maps two graphics-text sources (`graphics.md`).
  - `script/farland1-4.txt`, `farland5-10.txt`: an English **script translation (chapters 1-10) by Eien Ni
    Hen**, prose only, not inserted. Useful as a name reference: Ark, Felsaria, Ionia, Val, Valdes Empire,
    Gibogera, Nereid, Paracel. Per D2 these are "earlier fan" spellings, below any official English.

## Other searches (2026-10-25)

- No released English patch for the SNES game found (romhacking.net, general web).
- The Saturn port "Farland Story: Habou no Mai" is an enhanced remake of this game; no English release either.
