# Graphics-text survey

Japanese (and English) drawn as tiles rather than from the font. Sources: emulator tour of boot, title, intro,
first battle map and its menus (`work/qa/tour1`, `tour2`, `menus2`), Bongo's menu IPS (`prior-work.md`), and a
static sweep of the whole ROM and all 285 unpacked LZ blocks (below).

## List

| # | Screen | Text | Source | Format | State |
|---|---|---|---|---|---|
| G1 | Title screen | katakana logo ファーランドストーリー (above the English "FARLAND STORY 2" sub-logo) | LZ block `0x8065` (8 KB, `+0-+1000`) | 4bpp BG | seen in tour (`tour1/f001200`) + sweep. D5: keep unless an official English logo exists; the English sub-logo already names the game |
| G2 | Title menu | はじめから / つづきから / 環境設定 (16-px glyphs split in 8-px top/bottom tile rows, normal + highlighted copies) | LZ block `0x6321` (8 KB), tiles about `+1000-+2000` | 4bpp BG on stone texture | seen in tour + sweep; Bongo's IPS replaced it ("Start / Continue / Settings", booted) |
| G3 | Map menu, unit command menu (and likely the other command windows) | ターン終了 / 状況 / セーブ / ロード / 環境設定, 待機, ... (kanji not in the 16x16 font, e.g. 了 況 環 境) | raw `0xD45EB-0xD5617` | 1bpp glyph rows in the odd bytes of 2bpp data (even bytes `$FF`), not plain 8x8 tile order (8x16 strips; layout to be worked out in the graphics phase; Bongo's `Menus/` + `Tools/Font8x8` handled it) | seen in tour (`menus2/f000760`, `f000200`) + sweep; **verified**: Bongo's IPS (which writes only `0x6321` and this range) booted from the same battle state shows "Standby" and "End Turn / Objective / Save Game / Load Game / Settings" (`work/qa/bongo_map`) |
| E1 | Boot logos | BANPRESTO, TGL "TECHNICAL GROUP LABORATORY" | LZ `0x34A6`, `0x3F1A` | 4bpp | English, keep |
| E2 | Title | FARLAND STORY 2, PUSH START, ©TGL 1995, ©BANPRESTO 1995 | LZ `0x468C` (copy in `0x6321`) | 4bpp | English, keep |
| E3 | Unit sprites | small Z / P / C status letters beside unit heads (sleep / poison / confuse?) | raw `~0x131000-0x167FFF` (unit sprite sets) | 4bpp sprites | English, keep |

Not tile text (font-drawn, extracted with the script): STAGE cards (`{full}　ＳＴＡＧＥ２５ ... ＜ギボゲラ＞`),
settings window (かんきょうせってい / BGM / SE / モード ステレオ), item, unit and class names, battle messages.

Still to confirm by warping (phase 2 debug tool, then the phase 5 marker tour): battle scene UI, status screen,
shop, save/load screens, game over, ending and credits. The static sweep found no other Japanese tile art, so
these are expected to be font text or the G3 label set; any that are not get a row here.

## Static sweep (recon, 2026-10-25)

- `python -X utf8 tools/lzscan.py --dump work/lz` then `tools/gfxsweep.py`:
  - `--out work/sweep/rom4 --fmt 4bpp --rows 48` (whole ROM, 32 sheets),
  - `--out work/sweep/lz4 --fmt 4bpp --rows 48 --lz work/lz` (all LZ blocks, 17 sheets),
  - `--fmt 2bpp --rank 0.45` on the ROM (2 sheets) and on the LZ blocks (19 sheets): 2bpp only for chunks
    whose tiles are mostly two-colour strokes (menu glyph tiles score 0.6-0.8, other data < 0.25); every
    skipped chunk is listed with its score in `skipped_r2bpp.tsv`.
- 70 sheets read by 4 visual-qa subagents (`work/sweep/findings_*.md` and their reports): results are the
  table above. Limits: 2bpp data scoring under 0.45 was only seen in the 4bpp render (where 2bpp text still
  shows as text-like noise, e.g. G3 was spotted in both); LZ table walks may have missed blocks loaded through
  pointers not in `lzscan.py`'s table list.
