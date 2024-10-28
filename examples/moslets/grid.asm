    .ASSUME	ADL = 1			
    INCLUDE "mos_api.inc"
    ORG $b0000 ; Is a moslet

    MACRO PROGNAME
    ASCIZ "grid.bin"
    ENDMACRO
    
    include "init.inc"
    include "parse.inc"

; API includes
    include "functions.inc"
    include "files.inc"
    include "timer.inc"
    include "vdu.inc"
    ; include "vdu_fonts.inc"
    include "vdu_plot.inc"

; Application includes
    ; include "fonts_list.inc"

hello_world: ASCIZ "Hello, World!\r\n"
goodbye_world: ASCIZ "Goodbye, Cruel World!\r\n"

; Main routine
_main:

; VDU 23, 0, &C0, n: Turn logical screen scaling on and off *
; inputs: a is scaling mode, 1=on, 0=off
; note: default setting on boot is scaling ON
    xor a
    call vdu_set_scaling

    ; ld hl,hello_world
    ; call printString

; VDU 18, mode, colour: Set graphics colour (GCOL mode, colour)
; inputs: a=mode, c=colour (add 128 to set background colour)
    xor a
    ld c,c_white
    call vdu_gcol

; VDU 5: Write text at graphics cursor
    ld a,5
    rst.lil $10

; draw horizontal grid lines
    ld iy,0 ; intial y coordinate
    ld b,24 ; number of lines
    ld a,-1 ; cell number
    ld (@cell_num),a
@loop_horizontal:
    push bc ; save loop counter
; VDU 25, mode, x; y;: PLOT command
; inputs: a=mode, ix=x0, iy=y0
; move cursor to left edge of screen
    ld a,plot_pt+mv_abs
    ld ix,0
    call plot
; plot line to right edge of screen
    ld a,plot_sl_both+dr_abs_fg
    ld ix,1023 ; max x coordinate for any screen mode
    call plot
; Write cell number at graphics cursor
    ld a,plot_pt+mv_abs
    ld ix,0
    call plot
    ld a,(@cell_num)
    inc a
    ld (@cell_num),a
    call printHex8
; increment y coordinate and loop
    lea iy,iy+32
    pop bc ; restore loop counter
    djnz @loop_horizontal

; draw vertical grid lines
    ld ix,0 ; initial x coordinate
    ld b,32 ; number of lines
    ld a,-1 ; cell number
    ld (@cell_num),a
@loop_vertical:
    push bc ; save loop counter
; VDU 25, mode, x; y;: PLOT command
; inputs: a=mode, ix=x0, iy=y0
; move cursor to top edge of screen
    ld a,plot_pt+mv_abs
    ld iy,0
    call plot
; plot line to bottom edge of screen
    ld a,plot_sl_both+dr_abs_fg
    ld iy,767 ; max y coordinate for any screen mode
    call plot
; Write cell number at graphics cursor
    ld a,plot_pt+mv_abs
    ld iy,0
    call plot
    ld a,(@cell_num)
    inc a
    ld (@cell_num),a
    call printHex8
; increment x coordinate and loop
    lea ix,ix+32
    pop bc ; restore loop counter
    djnz @loop_vertical

; ; print goodbye
;     ld hl,goodbye_world
;     call printString

; VDU 4: Write text at text cursor
    ld a,4
    rst.lil $10

@main_end:
; End with no error
    LD 	HL, 0
    RET

@cell_num: db 0

; VDU 25, mode, x; y;: PLOT command
; inputs: a=mode, ix=x0, iy=y0
plot:
    ld (@mode),a
    ld (@x0),ix
    ld (@y0),iy
	ld hl,@cmd
	ld bc,@end-@cmd
	rst.lil $18
	ret
@cmd:   db 25
@mode:  db 0
@x0: 	dw 0
@y0: 	dw 0
@end:   db 0 ; padding

; VDU 5: Write text at graphics cursor
; inputs: hl = pointer to text, ix=x0, iy=y0
; prerequisites: gcol foreground set
plot_text:
    push hl ; save text pointer
; move graphics cursor to x0, y0
    ld a,plot_pt+mv_abs
    call plot
; write text
    ld a,5 ; VDU 5 command
    rst.lil $10
    pop hl ; restore text pointer
    call printString
    ret