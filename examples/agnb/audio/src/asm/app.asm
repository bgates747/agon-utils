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

    include "mos_api.inc"
    include "macros.inc" ; must precede includes that use these macros
    include "agnb.inc"   ; proven generic RIFF/AGNB and VDP-buffer API
    include "audio.inc"  ; audio-container scaffold
    include "includes.inc"
    include "vdu_sound.inc"
    include "debug.inc"  ; retained dependency of the copied AGNB API
    include "functions.inc" ; retained dependency of debug.inc
    include "maths.inc"  ; retained dependency of functions.inc

init:
; No application initialization is required yet. Screen, input, timer, and
; slideshow setup belonged to the image test application and was removed.
    ret

main:
; Load, finalize, and interactively play every audio record in sfx.agnb.
    call agnb_load_audio
    ret
