# Text engine, encoding and pointers

Addresses: CPU `$Bk:addr` (HiROM, file offset = `addr & $3FFFFF`) and file offsets `0xNNNNNN`.

## Encoding (verified)

- Text is a stream of **16-bit little-endian words**. Draw loop: `$C0:2C53` (`LDA [$10],y` with Y = `$04CC`).
- Word `< $8000` = glyph index. Full-width mode: 16x16 font at `$C4:1000`, 32 bytes/glyph (index x32).
  Half-width mode: 8x16 font at `$C4:0000`, 16 bytes/glyph (index x16). Same index order in both fonts for
  `$00-$F0` (symbols, digits, A-Z, katakana, hiragana); `$100-$329` are kanji (16x16 only). Details: `font.md`.
- Table: `tbl/jp.tbl` (tbl.py syntax, keys are the raw byte pair, e.g. `0501` = word `$0105`). Started from
  Bongo's `FS2j.tbl`, every glyph then checked against `tools/fontsheet.py` sheets (2026-10-25). Fixed 9 errors:
  変/陸 swapped (`$0105`/`$0106`), 送 (`$018D`, was 迷), 色 (`$01F0`, was 角), 迷 `$0248` and 角 `$02EB` added,
  「」 (`$1E`/`$1F`, were 『』), ” (`$02`); `$9E` reads as the long-vowel mark ー (was －). Every non-blank glyph `$000-$329` has a reading; no duplicate values.
  Entries whose glyph is blank (`$03-$0A $10 $11 $13 $16-$1C $23 $7A $CD`) are Bongo's guesses and appear unused.
- Verified by decoding the opening narration at `0x483D9` ("アークがフェルサリアの王となって２０年...") and the
  STAGE cards, item names, unit names, battle messages (all read as correct Japanese).

## Control codes (verified: dispatch table `$C0:301C`, 16 word entries, handlers read)

| Word | tbl name | Args (words) | Effect |
|---|---|---|---|
| `$8000` | `{end}` | 0 | end of string (handled before the table, `$C0:2FF0`) |
| `$8001` | `{nl}` | 0 | new line (`$C0:303C`; `$04C4` = line, max 3 lines then scroll flag) |
| `$8002-$8005` | `{spd0}..{spd3}` | 0 | print speed `$04CE/$04D0` = 0, 1, 2, 4 (table `$C0:3083`) |
| `$8006` | `{half}` | 0 | 8x16 half-width font (`$04CA` bit 2 set) |
| `$8007` | `{full}` | 0 | 16x16 full-width font (`$04CA` bit 3) |
| `$8008/$8009` | `{f40on}/{f40off}` | 0 | `$04CA` bit 6 set/clear (seen as "instant print" in menus; guess) |
| `$800A/$800B` | `{f20on}/{f20off}` | 0 | `$04CA` bit 5 set/clear (meaning unknown) |
| `$800C` | `{wait}` | 0 | wait for a key press |
| `$800D` | `{pos:4}` | 2 | cursor column (word), row (word) -> `$04C3`, `$04C4` |
| `$800E` | `{delay:2}` | 1 | `$04C9` = value (pause / speed; low byte used) |
| `$800F` | `{clr}` | 0 | clear the window buffer (`$7E:xxxx` filled with `$FF00`) |

Dialogue boxes are 3 lines; the box width in glyphs is to be measured in phase 5.

## Where text lives (scan: `python -X utf8 tools/textscan.py`)

`tools/textscan.py` finds every run of glyph/control words ending in `$8000`. Real text clusters:

| Range (file) | Strings | Bytes | Content | Pointer form |
|---|---|---|---|---|
| `0x10000-0x1FFFF` | ~67 | ~1.4 KB | battle/shop/status messages inline in bank `$C1` code ("のこうげき！", "ゴールドになります") | 16-bit immediate in code (`LDA #lo`, bank set separately), e.g. `0x1EB12` from `0x10965` (verified by reference scan; exact opcode per site: phase 4) |
| `0x2465B-0x24AC3` | 75 | 1.1 KB | unit names, class names | struct table, 16-bit in-bank pointers, stride 10 (`0x245E5`, `0x245EF`, ...) and class table at `0x24925` (guess from refs) |
| `0x25231-0x253ED` | 25 | 0.4 KB | stage objectives ("ニセリアドを倒せ") | 16-bit table at `0x251FD` (refs) |
| `0x25F7D-0x26653` | 110 | 1.7 KB | item / weapon / spell names | 24-bit pointer inside 110-byte (`$6E`) item records from `0x254BD` |
| `0x2665B-0x27AEB` | 86 | 5 KB | item descriptions (`{clr}{pos}{full}...{nl}{half}<who can equip>`) | 16-bit table at `0x2665B` |
| `0x47800-0x6F9EE` | ~1250 | 81 KB | chapter scripts 0-29 (dialogue, narration, STAGE cards) | **24-bit pointers in script bytecode** (see below) |
| `0x2A3540-0x2A8DA3` | ~111 | 9 KB | chapter scripts 30-38 (late game, ending) | same, bank `$EA` |

Script text total ~92 KB of 16-bit words: English in a 1-byte or VWF encoding will be well under that, but
pointers are absolute, so text can move to expanded ROM.

## Script bytecode (verified for the pointer opcodes; other argument counts from Bongo, unverified)

- Chapter script table: `$C0:C9F0`, 39 x 3-byte pointers (index = chapter `$03B1`), entries `$C4:7800` ...
  `$EA:69DA`. Each entry points at a small 65816 stub that sets the bytecode pointer `$9B/$9D` and jumps into
  the VM loop `$C0:CEBA`.
- VM: 16-bit opcodes, `$FFFF` = end, handler table `$C0:CEEE` (89 opcodes `$00-$58`/`$59`). Bongo's argument
  list: `work/dl/bongo/x/Farland2/Asm/OpCodes.txt` (re-derived in phase 4 from the handlers before the
  extractor relies on it).
- Text opcodes `$3C`, `$3D`, `$41` (and `$42`?) take a 3-byte (24-bit) text pointer: e.g. at `0x4784C` the
  pointer `$C4:83D9` (opening narration). 1207 of the ~1250 script-bank strings have a 24-bit reference;
  the other ~42 (e.g. `0x49615` "しまった！") have none and are reached another way (fall-through after a
  previous string? a computed pointer?): phase 4 must account for them.
- Bongo's dump `Tools/FS2_VM/Pointers.txt` lists `.POINTER <target> @ <site>` for chapter 0.

## Open questions for phase 4

- Exact arg counts of all VM opcodes (`$26 $27 $4E-$53` are variable-length per Bongo).
- The ~42 script-bank strings without a direct pointer.
- Per-site opcode forms for the `$C1` inline strings, and the exact record layouts of the `$C2` tables.
- Names inserted into text: no name-variable control code seen; the hero name appears literal (リアド).
