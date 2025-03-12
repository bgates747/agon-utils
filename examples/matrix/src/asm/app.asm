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
    include "macros.inc"
    include "functions.inc"
    include "arith24.inc"
    include "maths.inc"
    include "fixed168.inc"
    include "timer.inc"
    include "vdu.inc"
    include "vdu_buffered_api.inc"
    include "vdu_fonts.inc"
    include "vdu_plot.inc"
    include "vdu_sound.inc"

    include "fpp.inc"
    include "fpp_ext.inc"

; APPLICATION INCLUDES
    
    include "debug.inc"

original_screen_mode: db 0
fn_seeker: asciz "images/seeker_000.rgba2"
buff_seeker: equ 256

; --- MAIN PROGRAM FILE ---
init:
; get current screen mode and save it so we can return to it on exit
    call vdu_get_screen_mode
    ld (original_screen_mode),a
; clear all buffers
    call vdu_clear_all_buffers
; set up the display
    ld a,20 ; 512x384x64 60Hz single-buffered
    call vdu_set_screen_mode
    xor a
    call vdu_set_scaling
; set text background color
    ld a,c_blue_dk+128
    call vdu_colour_text
; set text foreground color
    ld a,c_white
    call vdu_colour_text
; set gfx bg color
    xor a ; plotting mode 0
    ld a,c_blue_dk+128
    call vdu_gcol
    call vdu_cls
; set the cursor off
    call vdu_cursor_off
    ret

; end init
main:
; load a test bitmap
    ld a,1 ; type rgba2222
    ld hl,buff_seeker ; bufferId
    ld bc,16 ; width
    ld de,16 ; height
    ld iy,fn_seeker ; filename
    call vdu_load_img
; plot the image
    ld hl,buff_seeker
    call vdu_buff_select
    ld bc,64 ; x
    ld de,64 ; y
    call vdu_plot_bmp

    ret ; back to MOS
; end main

; must be final include in program so file data does not stomp on program code or other data
    include "files.inc"