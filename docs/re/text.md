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
  Phase 4 added the codes the table lacked, so every word decodes on its own: `$22` ▶ (menu cursor), `$24` ▼,
  `$25` ↓ (8x16 arrows; blank in 16x16), and `{g26} {g27} {gCE} {gF1}..{gFF}` for glyphs blank in both fonts.
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

Dialogue boxes are 18 cells x 3 lines (143 px per English line, 136 on the line before `{wait}`); every window
budget: `data/windows.json`, `vwf.md`.

## Extraction (phase 4, verified: `tests/test_build.py`)

`python -X utf8 tools/extract.py --write` dumps `script/*.json` (never overwrites without `--force`): 1907 strings (1899 before the phase-5 `imm` fix, `vwf.md`)
in 46 files, found through the pointers that reach them, not by scanning. Each entry: `id` (`<file>.<addr>`),
`addr`, `len` (bytes incl. `{end}`: the in-place room), `ptrs`, `jp` (without the final `{end}`), `en`, and
`box` (script windows), `unused` (no pointer reaches it: 49 dead-scene lines + 1), `notext` (controls/blanks only).
Tests: every `jp` re-encodes to the ROM bytes, the files match a fresh extraction, every textscan run in the text
ranges (`extract.TEXT_RANGES`: `0x10000-0x3FFFF`, `0x47800-0x6FFFF`, `0x2A3540-0x2BFFFF`) is inside an entry
(`NOT_TEXT` lists the one false run), no two entries overlap.

| File(s) | Strings | Pointer kind (`ptrs`) | Where |
|---|---|---|---|
| `ch00`-`ch38` | 1362 | `vm:` 24-bit arg of script text ops | `$C4-$C6`, `$EA`; filed by the chapter block holding the op |
| `units` | 60 | `p16:` table `0x245E3` | unit names |
| `classes` | 32 | `p16:` table `0x24923` | class names |
| `objectives` | 25 | `p16:` table `0x251F3` (31 entries, some shared) | stage objectives |
| `items` | 129 | `p24:` name pointer at `0x25465 + 22 * n` (22-byte item records) | item / weapon / spell names |
| `item_desc` | 128 | `p16:` table `0x2665B` (129 entries) | item descriptions |
| `system` | 130 | `imm:` + `p16:` tables `0x23764` (stage numbers by chapter), `0x21323` (save slots), `0x1F1B2` (stat names) | menus, shop, save/load, settings, status |
| `battle` | 33 | `imm:` | battle messages (`$C1`, `$C3`, `$EA/$EB` code) |

`imm:LO/BANK` = the code loads the pointer as immediates: `LDA #addr : STA $10|$14` plus `LDA #bank : STA
$12|$16` in the same call setup (no JSL between), or `LDY #1 : LDA #addr : STA [$28],y ... LDY #3 : LDA #bank :
STA [$28],y` (battle summon messages). The two offsets are the 16-bit and the bank immediates, so phase 7 can
move these strings to another bank.

Known gaps: `system.016496` "はげんきになった！" has no pointer form found (probably `$C1:647E` + offset, or unused);
the 49 unused chapter lines sit in dead bytecode (e.g. `0x5A458`, no pointer to it) or after it.

## Script bytecode (verified: `tools/vm.py` walks every reachable op with no unknown opcode)

- Chapter script table: `$C0:C9F0`, 39 x 3-byte pointers (index = chapter `$03B1`), entries `$C4:7800` ...
  `$EA:69DA`. Each entry points at a small 65816 stub that sets the bytecode pointer `$9B/$9D`
  (`LDA #bank : STA $9D : REP #$20 : LDA #addr : STA $9B`) and runs the VM loop `$C0:CEBA`. 193 such stubs exist
  (chapter starts plus in-chapter events).
- **Talk scripts:** `$C0:CC4F` reads `[$C0:CCBA + 3 * chapter]` -> a table of 24-bit bytecode pointers indexed by
  `$03C8` (town people, "町人"). Each table runs until its own scripts start. Op `$42` points at the map/event
  data block that precedes such a table (e.g. `$C4:82DE`).
- VM: 16-bit opcodes, `$FFFF` = end, handler table `$C0:CEEE` (`$00-$59`). Argument bytes, read off the handlers
  (count of `INC $9B` per path; `tools/vm.py` `ARGS`/`BRANCH`):
  - 0: `$00-$03 $05-$0B $0E-$11 $15 $1A-$1D $23 $2E-$31 $34-$3B $3E-$40 $45-$47 $59` (`$59` ends the script)
  - 1: `$13 $14 $16-$19 $21 $22 $2C $2D $32 $33 $43 $44 $55 $56`; 2: `$04 $0C $0D $1E $24 $25 $2A $2B`;
    3: `$12 $28 $29`; 4: `$1F $20`
  - 3 = 24-bit pointer: `$3C` (upper window), `$3D` (lower), `$41` (centre) text; `$42` event data; `$54` goto
  - `$26 $27`: 1 byte, a `$FF`-terminated byte list, 1 byte (unit move paths)
  - conditional branches = condition bytes + 24-bit target: `$48-$4D $57 $58` 1 byte, `$52 $53` 2,
    `$4E $4F` 4, `$50 $51` 6. Bongo's "variable length" for `$4E-$53` was the early-exit paths, all the same length.

## Open questions

- Names inserted into text: no name-variable control code seen; the hero name appears literal (リアド).
- `{f40on}`/`{f20on}` meaning (phase 5 marker build).
