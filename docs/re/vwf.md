# English engine: VWF, English table, relocation (phase 5)

## Font decision

All text, dialogue and menus alike, is drawn with one 8x16-cell variable-width font (`fonts/vwf.txt`, drawn
for this project, `tools/font.py`): caps 10 px, x-height 7, descenders 3, advance = glyph width + 1 (space 4,
`　` 6 = digit width, for code-padded numbers). Dialogue boxes are 18 cells = 144 px: about 26-30 characters a
line instead of 9 full-width or 18 fixed half-width glyphs. **Verified** in-game (marker build, `work/qa/p5m`).

## How the engine draws (verified: disassembly + marker build)

- `$C0:2C33` is called once per glyph (print speed counts frames in `$04CF/$04D0` first). The window is a
  linear 2bpp tile buffer in bank `$7E` at `$04C0`: cell = one 8x8 tile column (16 bytes), `$04D3` = width in
  cells, `$04D5` = `$04D3 * 16` (offset of the bottom tile row of a line), line = 2 tile rows. Fill `$FF00`:
  plane 1 = `$FF`, ink = plane 0 bit (colour 3 on colour 2).
- Cursor: `$04C3` cell, `$04C4` line, `$04D4` lines (3 in dialogue; `{nl}` on the last line scrolls,
  `$C0:303C`). After a glyph, `$C0:2F8F` adds 1 (half) or 2 (full) cells, `$C0:2F9A` wraps at `$04D3`.

## Hooks (`asm/vwf.asm`, code + data in `$F0:0000`)

| Org | Replaces | Why |
|---|---|---|
| `$C0:2C6A` | `ASL x4` (glyph word -> font offset) | codes `>= $0400`, and JP `$00-$4B` (symbols, digits, A-Z: `vwf_remap`), become a pending VWF code (`$1E84`); the original timing code then runs with glyph 0 |
| `$C0:2CF1` | `SEP #$20 : PHB : LDA #$C4` (start of the copy) | VWF code pending: OR the glyph shifted by the pixel offset into the cell and the next one (shift table, 8 x 256 words), advance `$04C3` by whole cells and rejoin the wrap check at `$C0:2F9A`. Else the original copy, moved to the next cell if a VWF glyph left the cursor mid-cell |

RAM `$1E80-$1E8F` (no code reference to `$1E8x`; never written in 7 gameplay states, `tools/lua/ramfree.lua`;
guess-level: a cold boot clears it): pixel offset, the cell/line the last VWF glyph left the cursor at (any other
value = the game moved the cursor, offset restarts at 0), pending code, scratch. The spill into the next cell
is skipped at the window's last cell (it would land in the next tile row).

## English table and text

`tools/font.py` builds it in memory: jp.tbl's control codes plus glyph i of `fonts/vwf.txt` = word `$0400 + i`.
`build.py` encodes `en` with it, `jp` with `tbl/jp.tbl` (kana and kanji still draw through the original path).

## Relocation (`tools/build.py`)

4 MiB image (`$F0-$FF` = file `0x300000-0x3FFFFF`, `$FF` fill). A string that fits its room stays in place;
a longer one moves to `$F2-$FF` (never across a bank) and every pointer is rewritten: `vm`/`p24` 24-bit,
`imm` the 16-bit and the bank immediates. `p16` tables (units, classes, objectives, item_desc, stage numbers,
save slots, stat names) are read only by `LDA $Cb:tttt,x : STA $14 ... LDA #$Cb : STA $16 : JSL/JSR copy`
(`$C2:28B6`, into a RAM buffer such as `$7E:F8D6`): a table with any English moves whole to `$F1` and those
bank immediates are patched (`build.p16_bank_sites`). Test: `tests/test_engine.py` follows every pointer of
every string in the marker build to its bytes.

p16 reads can start at a later entry (save slots: `LDA $C2:1329,x` = table + 6); `p16_bank_sites` takes every
entry address of the table.

## RAM string buffers and name templates (verified: hang reproduced and fixed, `work/qa/p5m/gocat`)

Menus and messages are built in `$7E:F8D6` / `$7E:F9D6` (256 bytes each) with `$C2:2882` (copy, with
terminator), `$C2:28BA` (append) and `$C2:28ED` (overlay: copy *without* the terminator). The battle window's
name line copies a 9-space template (`battle.01ED33`, `$C1:ED33`) to `$7E:F9D6`, overlays the unit name on it
(`$C1:ECDA`, the only overlay call) and appends it to `$7E:F8D6`: a name longer than the template overwrites the
terminator and the append copies the buffer into itself forever (black screen after the first battle). The
English build fills the template with 16 zero-width blanks (`\z` in `fonts/vwf.txt`) and fails if a unit name is
longer (`build.TEMPLATES`, `tests/test_engine.py`). In this line the name is followed by `LV` at cell 9 in the
Japanese layout: unit names must stay within 71 px there, or `battle.01ED47` starts with `{pos:09000000}`.
Probe: `tools/lua/catlog.lua` logs every append with both lengths.

`imm` bank immediates also come as `LDA #$00bb : STA $16` (16-bit A), and a JSR to the copy routine ends a
call setup (phase 5 fix in `extract.imm_refs`: 10 entries had the next string's bank site, 8 short
control-only/label strings were missing).
