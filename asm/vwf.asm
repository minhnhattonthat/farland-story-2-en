; Farland Story 2 English: variable-width font for the text engine (docs/re/vwf.md).
; The engine ($C0:2C33) draws one glyph per call into a 2bpp tile buffer in bank $7E: cell = 8 px column,
; plane 0 = ink, plane 1 = $FF (window fill $FF00). Glyph codes >= $0400 (and JP symbols/digits/A-Z remapped
; through vwf_remap) are drawn here from the build's 8x16 VWF font, shifted to the pixel cursor and ORed into
; the cell and the next one. Other codes (kana, kanji, menu cursor) take the original path.
; Applied by tools/build.py with asar after the ROM is expanded to 4 MiB; build/vwf_*.bin come from tools/font.py.
hirom
incsrc "../build/vwf_consts.asm"   ; !vwf_space: VWF index of the space glyph

!px    = $1E80   ; word: pixel offset in the current cell (0-7)
!col   = $1E82   ; cell ($04C3) and line ($04C4) the last VWF glyph left the cursor at; any other value means
!row   = $1E83   ; the game moved the cursor itself, so the pixel offset restarts at 0
!code  = $1E84   ; word: pending VWF code ($0400 + index) or 0
!dest  = $1E86   ; word: buffer offset of the cell
!keep  = $1E88   ; word: mask of the pixels left of the cursor in the cell
!right = $1E8A   ; word: nonzero = the glyph spills into the next cell
!w     = $1E8C   ; word: shifted glyph row (high byte = this cell, low byte = next cell)
!wid   = $1E8E   ; word: advance of the glyph

; --- hooks ---
org $C02C6A          ; glyph word in A (M=X=16): ASL x4 / TAX / ...
    jml vwf_glyph

org $C02CF1          ; X = buffer offset of the cell, Y = font offset: SEP #$20 / PHB / LDA #$C4
    jml vwf_draw
    nop

org $C032DA          ; {pos} handler: PLB / SEP #$20 / REP #$10
    jml vwf_pos
    nop

org $C03317          ; {clr} handler: PLB / SEP #$30 / LDX $04D3
    jml vwf_clr
    nop
    nop

; --- code ---
org $F00000
vwf_glyph:
    cmp #$0400
    bcs .vwf
    cmp #$004C
    bcs .orig
    tax
    lda.l vwf_remap,x
    and #$00FF
    cmp #$00FF
    beq .orig_x
    ora #$0400
.vwf:
    sta.l $7E0000+!code
    lda #$0000
    jml $C02C6E
.orig_x:
    txa
.orig:
    pha
    lda #$0000
    sta.l $7E0000+!code
    pla
    asl
    asl
    asl
    asl
    jml $C02C6E

vwf_draw:
    lda.l $7E0000+!code
    bne .vwf
    ; original glyph: start it on a fresh cell if a VWF glyph left the cursor mid-cell
    phb
    pea $7E7E
    plb
    plb
    sep #$20
    lda !px
    beq .orig_done
    lda $04C3
    cmp !col
    bne .orig_done
    lda $04C4
    cmp !row
    bne .orig_done
    inc $04C3
    rep #$21
    txa
    adc #$0010
    tax
.orig_done:
    rep #$20
    lda #$FFFF        ; invalidate: the cell grid takes over again
    sta !col
    stz !px
    plb
    sep #$20
    phb
    lda #$C4
    jml $C02CF6

.vwf:
    phb
    pea $7E7E
    plb
    plb
    stx !dest
    sep #$20
    lda $04C3
    cmp !col
    bne .reset
    lda $04C4
    cmp !row
    beq .synced
.reset:
    stz !px
    stz !px+1
.synced:
    rep #$30
    ; a space whose next word would pass the window's right edge breaks the line instead (lines joined at run
    ; time: "<name> attacks!"); script text is fitted by tools/wrap.py, so it never breaks there
    lda !code
    cmp.w #$0400+!vwf_space
    bne .draw
    jsr vwf_wordfits
    bcc .draw
    inc $04CC
    inc $04CC
    lda #$FFFF
    sta !col
    sep #$30
    lda $04D3          ; cell = width: the engine's own wrap starts the next line
    plb
    jml $C02F9A
.draw:
    lda !code
    sec
    sbc #$0400
    tax
    lda.l vwf_width,x
    and #$00FF
    sta !wid
    txa
    asl
    asl
    asl
    asl
    clc
    adc.w #vwf_font
    sta $14
    sep #$20
    lda.b #vwf_font>>16
    sta $16
    ; keep = pixels left of the cursor: high byte of ($FF00 >> px), inverted
    rep #$20
    lda !px
    and #$0007
    sta !px
    tax
    lda #$FF00
    cpx #$0000
    beq +
-   lsr
    dex
    bne -
+   xba
    eor #$00FF
    and #$00FF
    sta !keep
    ; right = px + wid > 8 and the next cell is inside the window
    stz !right
    lda !px
    clc
    adc !wid
    cmp #$0009
    bcc +
    lda $04C3
    and #$00FF
    inc
    sep #$20
    cmp $04D3
    rep #$20
    bcs +
    inc !right
+
    ldy #$0000
.row:
    ; w = (glyph row << 8) >> px, from the shift table
    lda [$14],y
    and #$00FF
    asl
    sta !w
    lda !px
    xba
    asl
    clc
    adc !w
    tax
    lda.l vwf_shift,x
    sta !w
    ; buffer index: top cell row for rows 0-7, bottom for 8-15
    tya
    and #$0007
    asl
    clc
    adc !dest
    cpy #$0008
    bcc +
    clc
    adc $04D5
+   tax
    lda $0000,x
    and !keep
    sta $0000,x
    lda !w
    xba
    and #$00FF
    ora $0000,x
    ora #$FF00
    sta $0000,x
    lda !right
    beq +
    lda !w
    and #$00FF
    ora #$FF00
    sta $0010,x
+   iny
    cpy #$0010
    bne .row
    ; advance: px += wid, whole cells go to $04C3 through the engine's own wrap check at $C0:2F9A
    inc $04CC
    inc $04CC
    lda !px
    clc
    adc !wid
    pha
    and #$0007
    sta !px
    pla
    lsr
    lsr
    lsr
    sep #$30
    clc
    adc $04C3
    sta !col
    pha
    lda $04C4
    sta !row
    pla
    plb
    jml $C02F9A       ; A = new cell (M=X=8): CMP $04D3 / BCC store / else next line

; C set = the word after the space at text offset $04CC ends past the window ($04D3 cells); M=X=16, DB=$7E.
; Scans the string ([$04C6] + offset) to the next space or control code. Kana/kanji count 8 px.
vwf_wordfits:
    lda $04C3
    and #$00FF
    asl
    asl
    asl
    clc
    adc !px
    bne +
    clc               ; at the line start: breaking would only add an empty line
    rts
+   sta !w
    lda.l vwf_width+!vwf_space
    and #$00FF
    clc
    adc !w
    sta !w
    lda $10
    pha
    lda $12
    pha
    lda $04C6
    sta $10
    lda $04C8
    sta $12
    ldy $04CC
.next:
    iny
    iny
    lda [$10],y
    bmi .done         ; control code or end
    cmp #$0400
    bcs .vwf
    cmp #$004C
    bcs .wide
    tax
    lda.l vwf_remap,x
    and #$00FF
    cmp #$00FF
    beq .wide
    bra .idx
.vwf:
    sec
    sbc #$0400
.idx:
    cmp.w #!vwf_space
    beq .done
    tax
    lda.l vwf_width,x
    and #$00FF
    bra .add
.wide:
    lda #$0008
.add:
    clc
    adc !w
    sta !w
    bra .next
.done:
    pla
    sta $12
    pla
    sta $10
    lda $04D3
    and #$00FF
    asl
    asl
    asl
    sta !keep         ; scratch: window width in px
    lda !w
    cmp !keep         ; C = end >= width
    rts

; {pos} and {clr} place the cursor themselves: forget where the last VWF glyph left it, so the next glyph starts
; at pixel 0 of its cell even when {pos} lands on that same cell (a string after {clr}{pos:0,0} began 3-4 px in).
vwf_pos:
    plb
    sep #$20
    rep #$10
    lda #$FF
    sta.l $7E0000+!col
    jml $C032DF
vwf_clr:
    plb
    sep #$30
    lda #$FF
    sta.l $7E0000+!col
    ldx $04D3
    jml $C0331D

vwf_remap:   incbin "../build/vwf_remap.bin"   ; JP code $00-$4B -> VWF index, $FF = original glyph
vwf_width:   incbin "../build/vwf_width.bin"   ; advance per VWF index
vwf_shift:   incbin "../build/vwf_shift.bin"   ; [px][byte] = (byte << 8) >> px, words
vwf_font:    incbin "../build/vwf_font.bin"    ; 16 bytes per VWF index, 1bpp rows 0-15
vwf_end:
warnpc $F0F000

incsrc "windows.asm"
