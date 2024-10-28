	.assume adl=1   
    .org 0x040000    

    jp start       

    .align 64      
    .db "MOS"       
    .db 00h         
    .db 01h       

start:              
    push af
    push bc
    push de
    push ix
    push iy

	call _main

exit:
    pop iy
    pop ix
    pop de
    pop bc
    pop af
    ld hl,0
    ret

; API includes
    include "mos_api.inc"
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

    ld hl,hello_world
    call printString

; VDU 18, mode, colour: Set graphics colour (GCOL mode, colour)
; inputs: a=mode, c=colour (add 128 to set background colour)
    xor a
    ld c,c_white
    call vdu_gcol
; draw horizontal grid lines
    ld iy,@y
    ld ix,0 ; intial y coordinate
    ld b,32 ; number of lines
@loop_horizontal:
    ld (iy),ix ; set y coordinate
    push bc ; save loop counter
; VDU 25, mode, x; y;: PLOT command
; inputs: a=mode, bc=x0, de=y0
; move cursor to left edge of screen
    ld a,plot_pt+mv_abs
    ld bc,0
    ld de,(iy)
    call dumpRegistersHex
    call vdu_plot
; plot line to right edge of screen
    ld a,plot_sl_both+dr_abs_fg
    ld bc,1023 ; max x coordinate for any screen mode
    ld de,(iy)
    ; call dumpRegistersHex
    call vdu_plot
; increment y coordinate and loop
    lea ix,ix+32
    pop bc ; restore loop counter
    djnz @loop_horizontal

; print goodbye
    ld hl,goodbye_world
    call printString

@main_end:		
    ret

@x: dl 0 ; current x coordinate
@y: dl 0 ; current y coordinate
