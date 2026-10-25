; Wider item windows (docs/re/vwf.md §Window tiles). Included by vwf.asm.
; Each open window owns w*h BG3 tiles: base = $20 + the areas of the windows under it ($C2:1FC8, record at
; $7E:D58C + 11*depth: +6 area, +8 base). BG3 tiles sit at VRAM $5000, its map at $5800 (only the left 32x32 screen
; is uploaded, from $7E:A0AC), so a run past tile 255 overwrote the map. English windows are wider: a window whose
; run would cross tile 256 starts at tile 384 instead ($5C00, the unused right screen of BG3's 64x32 map). Its RAM
; shadow ($7E:D5CE + (base-$20)*16) then reaches $7E:F3CE; $7E:E3CE-$F3FF is never written by the game (watch
; probe over 16 warp scenes, docs/re/vwf.md §Window tiles).

!rec = $7ED58C       ; window records, 11 bytes each

; --- allocator: replaces LDA $24 / CLC / ADC #$0020 / STA $7ED594,x (X = record offset, M=X=16)
assert read4($C22048) == $691824A5 && read4($C2204C) == $949F0020 && read2($C22050) == $7ED5, "allocator moved"
org $C22048
    jsl win_alloc
    nop
    nop
    nop
    nop
    nop
    nop

; --- window sizes: LDA #w before the window-open call (tools/winsites.py)
macro width(at, old, new)
    assert read1(<at>-1) == $A9 && read1(<at>) == <old>, "window immediate at <at> is not LDA #<old>"
    org <at>
    db <new>
endmacro
%width($C13142, 9, 13)    ; shop list: cursor + 12 cells (95 px names)
%width($C1313A, 15, 13)   ; shop list x: keep the frame on screen
%width($C13BA5, 11, 14)   ; item list: blank, cursor, 12 cells
%width($C13E32, 1, 11)    ; use/sell sub-window y: below the item list instead of over its right end
%width($C14EEF, 12, 15)   ; exchange, upper: blank, cursor, mark, 12 cells
%width($C14F08, 12, 15)   ; exchange, lower
%width($C13898, 11, 14)   ; weapons window

org $F0F000           ; after the VWF code and font (vwf.asm warnpc)
win_alloc:
    cpx #$0000
    bne .prev
    lda #$0020
    bra .fit
.prev:
    lda.l !rec+8-11,x    ; previous window's base + area = the original sum
    clc
    adc.l !rec+6-11,x
.fit:
    cmp #$0180
    bcs .store
    pha
    clc
    adc.l !rec+6,x
    cmp #$0101           ; past tile 256: move the whole run to tile 384
    pla
    bcc .store
    lda #$0180
.store:
    sta.l !rec+8,x
    rtl
warnpc $F10000
