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
    include "maths.inc"
	INCLUDE	"arith24.inc"
    include "trig24.inc"
    include "files.inc"
    include "timer.inc"
    include "vdu.inc"
    ; include "vdu_fonts.inc"
    include "vdu_plot.inc"

; SHAWN'S INCLUDES
	INCLUDE	"strings24.asm"

main:

    call test_umul24x24
    ; call test_umul24x8

    ret

test_umul24x24:
    ld hl,2
    ld de,3
    call printHexUHL
    call printNewLine
    ex de,hl
    call printHexUHL
    call printNewLine
    call printNewLine
    ex de,hl

    call umul24x24
    ld hl,(umul24x24out+3)
    call printHexUHL
    ld hl,(umul24x24out)
    call printHexUHL
    call printNewLine
    ret

test_umul24x8:
    ld hl,2
    ld a,3
    call printHexUHL
    call printNewLine
    call printHexA
    call printNewLine
    call umul24x8
    call printHexA
    call printHexUHL
    call printNewLine
    ret