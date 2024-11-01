    include "mos_api.inc"

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

    call main

exit:
    pop iy 
    pop ix
    pop de
    pop bc
    pop af
    ld hl,0

    ret 
    
; API INCLUDES
    include "functions.inc"
    include "files.inc"
    include "timer.inc"
    include "vdu.inc"
    ; include "vdu_fonts.inc"
    include "vdu_plot.inc"

; SHAWN'S INCLUDES
	INCLUDE	"strings24.asm"
	INCLUDE	"arith24.asm"

main:
    ld hl,0xFFFFFF
    HLU_TO_A
    ld b,a
    call printHexBHL
    call printNewLine

    ld a,0xFF
    call printHexA
    call printNewLine

    call umul24x8
    call printHexABHL
    call printNewLine
    ret