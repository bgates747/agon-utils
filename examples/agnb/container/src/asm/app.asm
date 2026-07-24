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

    ; jp temp
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
    include "macros.inc" ; needs to be above any other includes that use these macros
    include "agnb.inc"
    include "input.inc"
    include "images.inc"
    include "timer.inc"
    include "includes.inc"
    include "debug.inc" ; TODO: for application testing only, remove for production
    include "functions.inc" ; TODO: contains dependencies of debug.inc. may not be required for production
    include "maths.inc" ; TODO: contains dependencies of functions.inc. may not be required for production

init:
; set screen mode
    ; ld a,0 ; 640x480x16 single-buffered
    ; ld a,19 ; 1024x768x4 single-buffered
    ; ld a,8 ; 320x240x64 single-buffered
    ld a,20 ; 512x384x64 single-buffered
    ; ld a,23 ; 512x384x2 single-buffered
    call vdu_set_screen_mode

; set screen scaling and background colors
    ld hl,@beg
    ld bc,@end-@beg
    rst.lil $18
    jp @end
@beg:
;   VDU 23, 0, &C0, 0: Normal coordinates
    db 23,0,$C0,0
;   VDU 17, color : set text background color
    db 17,12+128 ; blue
;   VDU 18, color : set gfx background color
    db 18,0,12+128 ; blue
@end:
    call cursor_off
    call vdu_cls

; initialize main loop timer
main_loop_timer_reset: equ 60 ; 120ths of a second
    ld hl,main_loop_timer_reset
    call tmr_main_loop_set
    call tmr_slideshow_set
    ret ; init

main:
; begin temporary testing code
; Open the container and read through the first image's DATA header. No image
; payload bytes are read or uploaded by this test.
    ld de,agnb_filename
    call agnb_open
    ; call dumpFlags ; DEBUG
    jr nz,@agnb_done

    call agnb_read_riff_header
    ; call dumpFlags ; DEBUG
    jr nz,@agnb_close

    call agnb_read_vers
    ; call dumpFlags ; DEBUG
    jr nz,@agnb_close

    call agnb_read_buffer_list
    ; call dumpFlags ; DEBUG
    jr nz,@agnb_close

; Stream and consolidate the first DATA payload in its explicit VDP buffer.
    call agnb_stream_data
    ; call dumpFlags ; DEBUG
    jr nz,@agnb_close

; Apply the retained IMAG metadata, then plot the selected bitmap below the
; diagnostic text.
    call agnb_finalize_image
    ; call dumpFlags ; DEBUG
    jr nz,@agnb_close
    ld bc,0
    ld de,120
    call vdu_plot_bmp

@agnb_close:
    call agnb_close
    ; call dumpFlags ; DEBUG
@agnb_done:
; Dump normalized metadata for the first manifest image:
;     00 01  10 00  23 00  01  30 02 00 00
;     ID     width  height  fmt DATA size
    ; ld hl,agnb_metadata
    ; ld a,agnb_meta_size
    ; call dumpMemoryHex

; Dump the DATA chunk header at which parsing stopped:
;     44 41 54 41  30 02 00 00
;     D  A  T  A   payload size
    ; ld hl,agnb_header
    ; ld a,agnb_chunk_header_size
    ; call dumpMemoryHex

; Dump calculated width*height followed by the declared DATA size. Both u32
; values must be identical:
;     30 02 00 00
;     30 02 00 00
    ; ld hl,agnb_expected_data_size
    ; ld a,4
    ; call dumpMemoryHex
    ; ld hl,agnb_metadata+agnb_meta_data_size
    ; ld a,4
    ; call dumpMemoryHex
    ret
; end temporary testing code

    ld de, 0
    jp rendbmp

mainloop:
    call reset_keys

waitloop:
    call set_keys
    call tmr_main_loop_get
    jp z, do_input
    jp m, do_input
    jp waitloop

rendbmp:
; test de for wraparound
    ld hl,0
    xor a ; clear carry
    sbc hl,de
    jp z,@not_neg
    jp m,@not_neg
    ld de,num_images-1
    jp @load_image
@not_neg:
    ld hl,num_images-1
    xor a ; clear carry
    sbc hl,de
    jp p,@load_image
    ld de,0
@load_image:
    ld (current_image_index),de
    ld d,image_record_size
    mlt de
    ld iy,image_list
    add iy,de
    ld a,(iy+image_type) ; get image type
    ld bc,(iy+image_width) ; get image width
    ld de,(iy+image_height) ; get image height
    ld ix,(iy+image_filesize) ; get image file size

; TODO: implement here everything that vdu_load_img does,
; except loading the image buffers from disk since that is already done in the container loader


; plot image
    call vdu_cls
    ld bc,0 ; x
    ld de,0 ; y
    call vdu_plot_bmp

no_move:
    ld hl,main_loop_timer_reset
    call tmr_main_loop_set
    jp mainloop

main_end:
; exit program gracefully
    xor a ; 640x480x16 single-buffered
    call vdu_set_screen_mode
    ld a,1 ; scaling on
    call vdu_set_scaling
    call cursor_on
    ret

; load to onboard 8k sram
filedata: equ 0xB7E000
