# Graphics-text survey

Japanese (and English) drawn as tiles rather than from the font. Sources: emulator tour of boot, title, intro,
first battle map and its menus (`work/qa/tour1`, `tour2`, `menus2`), Bongo's menu IPS (`prior-work.md`), and a
static sweep of the whole ROM and all 285 unpacked LZ blocks (below).

## List

| # | Screen | Text | Source | Format | State |
|---|---|---|---|---|---|
| G1 | Title screen | katakana logo ファーランドストーリー (above the English "FARLAND STORY 2" sub-logo) | LZ block `0x8065` (8 KB, `+0-+1000`) | 4bpp BG | seen in tour (`tour1/f001200`) + sweep. D5: keep unless an official English logo exists; the English sub-logo already names the game |
| G2 | Title menu | はじめから / つづきから / 環境設定 | LZ block `0x6321` unpacks to the BG2 tiles at VRAM byte `0x4000`; text = tiles `$B4-$E5`, 8x6 cells (tilemap cols 12-19, rows 19-24; one cell is the shared texture tile `$C6`) | 4bpp, white ink (colour 1) on a stone texture that repeats per tile row; the highlight is a colour effect, not tiles | **English** (New Game / Continue / Settings), `tools/gfx.py` `title_menu`; zoomed shots normal + highlighted `work/qa/p8/g/tz.png` |
| G3 | Unit and map command menus | 17 labels: 移動 ワープ 攻／回 必殺 買物 武器 アイテム 交換 集合 待機 (unit menu) + ターン終了 全体マップ ユニット一覧 状況 セーブ ロード 環境設定 (map menu) | raw `0xD45EB-0xD562A`: 10 slots of `0xC0` (6x2 tiles, 48x16 px), then 7 slots of `0x140` (10x2 tiles, 80x16 px) from `0xD4D6B`; per slot the top tile row then the bottom one | 2bpp, ink in plane 0, plane 1 = `$FF`; a menu copies whole slots (MVN at `$00:0111` -> `$7E:D5CE`, DMA to VRAM `$5100`) | **English** (glossary §Menu labels), `tools/gfx.py` `menu_labels`; in game: `work/qa/p8/g/four.png`, slots no stage-1 menu offers shown with `tools/lua/labelswap.lua` (`swap.png`) |
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
