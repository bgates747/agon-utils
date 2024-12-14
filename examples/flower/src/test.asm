    assume adl=1 
    org 0x040000 
    jp start 
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

; API INCLUDES
    include "mos_api.inc"
    include "functions.inc"
    include "arith24.inc"
    include "maths.inc"
    include "files.inc"
    include "fixed168.inc"
    include "fonts.inc"
    include "images.inc"
    include "timer.inc"
    include "vdu.inc"

; --- MAIN PROGRAM FILE ---

init:

    ret

main:
    ld b,32 ; loop counter
@loop:
    push bc
    ld h,b
    ld l,8
    mlt hl
    ld h,l
    ld l,0
    call print_s168_hl
    ld de,100*256
    call polar_to_cartesian
    call print_s168_bc
    call print_s168_de
    call cartesian_to_polar
    call print_s168_hl
    call print_s168_de
    call printNewLine
    pop bc
    djnz @loop
    ret


    call printNewLine
    ld bc,1*256 ; 1.000 player_xvel
    ld de,-1*256 ; 2.000 player_yvel-1
    ; call cartesian_to_polar
    call atan2_168fast
    ; call distance168
    call print_s168_hl
    call printNewLine
    ; call print_s168_de
    ; call printNewLine
    ret