    assume adl=1   
    org 0x040000    

    include "mos_api.inc"

    MACRO PROGNAME
    ASCIZ "flower_demo"
    ENDMACRO

    jp start       

_exec_name:
	PROGNAME

    align 64      
    db "MOS"       
    db 00h         
    db 01h

start:              
    push af
    push bc
    push de
    push ix
    push iy

    call init
    call main

exit:

    pop iy 
    pop ix
    pop de
    pop bc
    pop af
    ld hl,0

    ret 

; --- MAIN PROGRAM ---
; APPLICATION INCLUDES

; --- INITIALIZATION ---
init:
    ret

; --- MAIN PROGRAM ---
main:
    call waitKeypress
    rst.lil 10h
    ret

; wait until user presses a key
; inputs: none
; outputs: ascii code of key pressed in a
; destroys: af,ix
waitKeypress:
    MOSCALL mos_getkey
    ret