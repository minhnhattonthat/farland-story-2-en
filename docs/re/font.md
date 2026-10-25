# Fonts

| Font | ROM | Format | Glyphs | Used by |
|---|---|---|---|---|
| 16x16 full-width | `$C4:1000` (`0x41000-0x4753F`) | 1bpp, 4 tiles of 8x8 (8 bytes each) in order TL, BL, TR, BR; 32 bytes/glyph | `$000-$329` (810): symbols, 0-9, A-Z, katakana, hiragana, 554 kanji | `{full}` text (dialogue) |
| 8x16 half-width | `$C4:0000` (`0x40000-0x40FFF`) | 1bpp, 2 tiles (top, bottom); 16 bytes/glyph | `$00-$F0` (same order as the 16x16 font); `$F1-$FF` blank | `{half}` text (menus, names, item "equip" lines) |

- **Verified**: layout read from `$C0:2C6A` (index x16, doubled unless `$04CA` bit 2 = half-width) and by
  rendering both fonts with `tools/fontsheet.py` (sheets match the table readings).
- The 8x16 font has **upper-case A-Z only**, no lower case. `0x4753F` onward is zero-filled (705 bytes) before
  the script data at `0x47800`.
- Menu labels drawn as tiles (not this font) are listed in `graphics.md`.
- English plan (phase 5): the half-width font already proves the engine can draw 8-px-wide cells; a VWF or a
  lower-case set in the 8x16 font is the likely route. Decide in phase 5 with the width gate.

Render: `python -X utf8 tools/fontsheet.py --out work/font/k --from 0x100 --to 0x32A [--fmt 8x16]`.
