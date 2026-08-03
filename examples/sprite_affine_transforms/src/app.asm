    .assume adl=1
    .org 0x040000

    jp fixture_start

    .align 64
    db "MOS",0,1

    include "config.inc"
    include "mos_api.inc"

fixture_start:
    push af
    push bc
    push de
    push ix
    push iy

    call fixture_run

    pop iy
    pop ix
    pop de
    pop bc
    pop af
    ld hl,0
    ret

fixture_run:
    call fixture_capture_screen_mode
    call fixture_initialize_ram
    call fixture_prepare_vdp
    call fixture_upload_bitmap
    call fixture_plot_regular_bitmap
    call fixture_create_sprites

    ld hl,fixture_help
    call vdu_print_cstr

fixture_main_loop:
    call fixture_wait_vblank
    call fixture_poll_key

    ld a,(fixture_running)
    or a
    jr z,fixture_main_loop_done

    call fixture_animate_sprites
    jr fixture_main_loop

fixture_main_loop_done:
    call fixture_release_vdp
    ret

fixture_capture_screen_mode:
    ld a,mos_sysvars
    rst.lil 08h
    ld a,(ix+sysvar_scrMode)
    ld (fixture_saved_screen_mode),a
    ret

fixture_initialize_ram:
    ld hl,fixture_motion_left
    ld (fixture_motion_x),hl      ; ADL24 OK: fixture_motion_x is dl.

    xor a
    ld (fixture_previous_key),a
    ld a,1
    ld (fixture_running),a
    ret

; Every RUN reconstructs the VDP state. The order matters: sprites can hold
; pointers into bitmap buffers, so reset sprites before clearing all buffers.
fixture_prepare_vdp:
    ld a,fixture_screen_mode
    call vdu_set_screen_mode
    call vdu_logical_coordinates_off
    call vdu_cursor_hide
    call vdu_clear_screen

    call vdu_hardware_sprite_preference_clear
    call vdu_hardware_sprites_disable
    call vdu_sprite_reset
    call vdu_buffer_clear_all
    call vdu_hardware_sprites_enable
    ret

; Replace this routine with a file or AGNB loader if the fixture grows. The
; remaining bitmap/sprite setup only depends on the stable buffer ID.
fixture_upload_bitmap:
    ld de,fixture_bitmap_buffer_id
    ld hl,fixture_rgba2222_pixels
    ld bc,fixture_rgba2222_size
    call vdu_buffer_upload

    ld de,fixture_bitmap_buffer_id
    call vdu_bitmap_select
    ld bc,fixture_bitmap_width
    ld de,fixture_bitmap_height
    ld a,vdu_bitmap_format_rgba2222
    call vdu_bitmap_create
    ret

fixture_plot_regular_bitmap:
    ld de,fixture_bitmap_buffer_id
    call vdu_bitmap_select
    ld bc,fixture_bitmap_x
    ld de,fixture_bitmap_y
    call vdu_bitmap_plot
    ret

fixture_create_sprites:
    ld a,fixture_software_sprite_id
    call vdu_sprite_select
    call vdu_sprite_clear_frames
    ld de,fixture_bitmap_buffer_id
    call vdu_sprite_add_buffer_frame
    call vdu_sprite_make_software
    ld bc,fixture_motion_left
    ld de,fixture_sprite_y
    call vdu_sprite_move_absolute
    call vdu_sprite_show

    ld a,fixture_hardware_sprite_id
    call vdu_sprite_select
    call vdu_sprite_clear_frames
    ld de,fixture_bitmap_buffer_id
    call vdu_sprite_add_buffer_frame
    ; Activate it once as software so the VDP allocates saved-background state.
    ; That makes the interactive hardware -> software transition safe.
    call vdu_sprite_make_software
    ld bc,fixture_motion_left+fixture_motion_offset
    ld de,fixture_sprite_y
    call vdu_sprite_move_absolute
    call vdu_sprite_show

    ld a,fixture_sprite_count
    call vdu_sprite_activate

    ; Command 19 is deliberately issued after both the RGBA2222 frame and the
    ; software activation exist. Hardware sprites keep the fallback storage.
    call fixture_set_right_hardware
    ret

fixture_poll_key:
    ld a,mos_sysvars
    rst.lil 08h

    ld a,(ix+sysvar_vkeydown)
    or a
    jr z,fixture_key_released

    ld a,(ix+sysvar_keyascii)
    ld b,a
    ld a,(fixture_previous_key)
    cp b
    ret z

    ld a,b
    ld (fixture_previous_key),a
    or a
    ret z

    cp 27
    jr z,fixture_request_exit

    or 20h
    cp 'q'
    jr z,fixture_request_exit
    cp 'h'
    jr z,fixture_request_hardware
    cp 's'
    jr z,fixture_request_software
    ret

fixture_key_released:
    xor a
    ld (fixture_previous_key),a
    ret

fixture_request_exit:
    xor a
    ld (fixture_running),a
    ret

fixture_request_hardware:
    call fixture_set_right_hardware
    ld hl,fixture_hardware_message
    call vdu_print_cstr
    ret

fixture_request_software:
    call fixture_set_right_software
    ld hl,fixture_software_message
    call vdu_print_cstr
    ret

; A visible software sprite has pixels saved in the framebuffer. Hide and
; refresh it while it is still software before changing to the overlay path,
; otherwise those old pixels can remain as a ghost.
fixture_set_right_hardware:
    ld a,fixture_hardware_sprite_id
    call vdu_sprite_select
    call vdu_sprite_hide
    call vdu_sprite_refresh
    call vdu_sprite_make_hardware
    call vdu_sprite_show
    ret

; Sprite 1 was activated as software at startup, so its saved-background
; allocation exists. Hide the overlay before returning to that path.
fixture_set_right_software:
    ld a,fixture_hardware_sprite_id
    call vdu_sprite_select
    call vdu_sprite_hide
    call vdu_sprite_make_software
    call vdu_sprite_show
    call vdu_sprite_refresh
    ret

fixture_animate_sprites:
    ld hl,(fixture_motion_x)      ; ADL24 OK: fixture_motion_x is dl.
    inc hl
    push hl
    ld de,fixture_motion_right+1
    or a
    sbc hl,de
    pop hl
    jr c,fixture_motion_in_range
    ld hl,fixture_motion_left

fixture_motion_in_range:
    ld (fixture_motion_x),hl      ; ADL24 OK: fixture_motion_x is dl.

    ld a,fixture_software_sprite_id
    call vdu_sprite_select
    ld hl,(fixture_motion_x)      ; ADL24 OK: fixture_motion_x is dl.
    push hl
    pop bc
    ld de,fixture_sprite_y
    call vdu_sprite_move_absolute

    ld a,fixture_hardware_sprite_id
    call vdu_sprite_select
    ld hl,(fixture_motion_x)      ; ADL24 OK: fixture_motion_x is dl.
    ld de,fixture_motion_offset
    add hl,de
    push hl
    pop bc
    ld de,fixture_sprite_y
    call vdu_sprite_move_absolute

    ; Required by the software sprite and harmless for the hardware sprite.
    call vdu_sprite_refresh
    ret

fixture_wait_vblank:
    ld a,mos_sysvars
    rst.lil 08h
    ld a,(ix+sysvar_time)
fixture_wait_vblank_loop:
    cp a,(ix+sysvar_time)
    jr z,fixture_wait_vblank_loop
    ret

fixture_release_vdp:
    xor a
    call vdu_sprite_activate
    call vdu_sprite_reset
    call vdu_buffer_clear_all
    call vdu_hardware_sprites_disable
    call vdu_hardware_sprite_preference_clear

    ld a,(fixture_saved_screen_mode)
    call vdu_set_screen_mode
    call vdu_logical_coordinates_on
    call vdu_cursor_show
    ret

fixture_help:
    db "Bitmap and sprite API fixture",13,10
    db "Top: ordinary buffered bitmap",13,10
    db "Bottom: software left, hardware right",13,10
    db "H/S changes right sprite; ESC/Q exits",13,10,0

fixture_hardware_message:
    db "Right sprite: hardware",13,10,0

fixture_software_message:
    db "Right sprite: software",13,10,0

fixture_saved_screen_mode:
    db 0

fixture_running:
    db 0

fixture_previous_key:
    db 0

fixture_motion_x:
    dl 0

    include "vdu_system.inc"
    include "vdu_buffer.inc"
    include "vdu_bitmap.inc"
    include "vdu_sprite.inc"
    include "fixture_assets.inc"
