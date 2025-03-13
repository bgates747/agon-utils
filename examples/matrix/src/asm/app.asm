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
fn_img: asciz "ctl_panel_navball.rgba2"
img_width: equ 79
img_height: equ 79
buff_img: equ 256
buff_xform: equ 257
buff_img_xform: equ 258
rotation: dw32 0 ; rotation to apply in unsigned 24.8 fixed-point format, degrees 360

; --- MAIN PROGRAM FILE ---
init:
; get current screen mode and save it so we can return to it on exit
    call vdu_get_screen_mode
    ld (original_screen_mode),a
; clear all buffers
    call vdu_clear_all_buffers
; set up the display
    ; ld a,20 ; 512x384x64 60Hz single-buffered
    ; ld a,8 ; 320x240x64 60Hz single-buffered
    ld a,8+128 ; 320x240x64 60Hz double-buffered
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
    ld c,c_blue_dk+128
    call vdu_gcol
    call vdu_cls
; set the cursor off
    call vdu_cursor_off
    ret

; end init
main:
; load a test bitmap
    ld a,1 ; type rgba2222
    ld hl,buff_img ; bufferId
    ld bc,img_width ; width
    ld de,img_height ; height
    ld iy,fn_img ; filename
    call vdu_load_img

; enable transform matrices
    call vdu_enable_transforms

    ; ld hl,-1        ; anticlockwise degrees 360 in 16.0 fixed-point
    ; ld hl,1*256   ; anticlockwise degrees in 16.8 fixed-point
    ld hl,0x2478 ; 1 degree converted to radians in floating point
    ld (rotation),hl
@loop:
; create a rotation transform matrix
    ; ld a,2 ; anticlockwise rotation in degrees
    ld a,3 ; anticlockwise rotation in radians

    ; ld ixl,$80 | $40 | 0 ; 16-bit | fixed-point | 0 shift = 16.0 fixed-point
    ld ixl,$80 | $00 | 0 ; 16-bit | floating-point | 0 shift = 16.0 fixed-point
    ld bc,2 ; argument length: 2 bytes to a 16.0 fixed-point number

    ld de,rotation ; argument pointer
    ld hl,buff_xform ; matrix bufferId
    call vdu_do_2d_matrix_transform

; apply transform matrix to bitmap
    xor a ; clear options
    ; set 1,a ; automatically resize bitmap
    ; set 2,a ; resize bitmap to specified dimensions
    ; ld ix,24 ; x size
    ; ld iy,24 ; y size
    ; set 4,a ; automatically translate target bitmap position
    ld hl,buff_img ; source bitmap bufferId
    ld de,buff_img_xform ; destination bufferId
    ld bc,buff_xform ; transform matrix bufferId
    call vdu_transform_bitmap

; plot the transformed bitmap
    ; ld a,%00100000
    ; call multiPurposeDelay
    call vdu_cls
    ld hl,buff_img_xform
    call vdu_buff_select
    ld bc,128 ; x
    ld de,64 ; y
    call vdu_plot_bmp
    call vdu_flip

; ; plot the raw bitmap
;     ld hl,buff_img
;     call vdu_buff_select
;     ld bc,0 ; x
;     ld de,8 ; y
;     call vdu_plot_bmp

    jr @loop

    ret ; back to MOS
; end main

; must be final include in program so file data does not stomp on program code or other data
    include "files.inc"