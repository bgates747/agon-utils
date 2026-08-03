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

    ld hl,fixture_help
    call vdu_print_cstr

    call fixture_create_sprites
    call fixture_request_identity

fixture_main_loop:
    call fixture_wait_vblank
    call fixture_poll_key

    ld a,(fixture_running)
    or a
    jr z,fixture_main_loop_done

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
    xor a
    ld (fixture_previous_key),a
    ld (fixture_transforms_bound),a
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
    call vdu_affine_matrices_enable
    call vdu_hardware_sprites_enable
    call vdu_sprite_affine_enable
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
    ld bc,fixture_software_sprite_x
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
    ld bc,fixture_hardware_sprite_x
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

    cp '0'
    jp z,fixture_request_identity
    cp '1'
    jp z,fixture_request_translate
    cp '2'
    jp z,fixture_request_scale_2
    cp '3'
    jp z,fixture_request_rotate_90
    cp '4'
    jp z,fixture_request_shear
    cp '5'
    jp z,fixture_request_reflect_x
    cp '6'
    jp z,fixture_request_pivot_rotate_90
    cp '7'
    jp z,fixture_request_singular
    cp '8'
    jp z,fixture_request_unbind

    or 20h
    cp 'q'
    jp z,fixture_request_exit
    cp 'h'
    jp z,fixture_request_hardware
    cp 's'
    jp z,fixture_request_software
    ret

fixture_key_released:
    xor a
    ld (fixture_previous_key),a
    ret

fixture_request_exit:
    xor a
    ld (fixture_running),a
    ret

; All valid states rebuild the same matrix ID. Once bound, transitions exercise
; live matrix mutation without repeating the 1412h binding command.
fixture_request_identity:
    call vdu_affine_identity
    call fixture_ensure_transforms_bound
    call vdu_sprite_refresh
    ld hl,fixture_identity_message
    jp fixture_show_matrix_status

fixture_request_translate:
    call vdu_affine_identity
    call vdu_affine_translate_8_4
    call fixture_ensure_transforms_bound
    call vdu_sprite_refresh
    ld hl,fixture_translate_message
    jp fixture_show_matrix_status

fixture_request_scale_2:
    call vdu_affine_identity
    call vdu_affine_scale_2
    call fixture_ensure_transforms_bound
    call vdu_sprite_refresh
    ld hl,fixture_scale_2_message
    jp fixture_show_matrix_status

fixture_request_rotate_90:
    call vdu_affine_identity
    call vdu_affine_rotate_90
    call fixture_ensure_transforms_bound
    call vdu_sprite_refresh
    ld hl,fixture_rotate_90_message
    jp fixture_show_matrix_status

fixture_request_shear:
    call vdu_affine_identity
    call vdu_affine_shear_negative_half_x
    call fixture_ensure_transforms_bound
    call vdu_sprite_refresh
    ld hl,fixture_shear_message
    jp fixture_show_matrix_status

fixture_request_reflect_x:
    call vdu_affine_identity
    call vdu_affine_reflect_x
    call fixture_ensure_transforms_bound
    call vdu_sprite_refresh
    ld hl,fixture_reflect_x_message
    jp fixture_show_matrix_status

fixture_request_pivot_rotate_90:
    call vdu_affine_identity
    call vdu_affine_translate_negative_pivot
    call vdu_affine_rotate_90
    call vdu_affine_translate_positive_pivot
    call fixture_ensure_transforms_bound
    call vdu_sprite_refresh
    ld hl,fixture_pivot_rotate_90_message
    jp fixture_show_matrix_status

; Publish a known scale-2 generation, then replace it with a singular candidate
; without rebinding. The visible scale-2 generation must remain last-known-good.
fixture_request_singular:
    call vdu_affine_identity
    call vdu_affine_scale_2
    call fixture_ensure_transforms_bound
    call vdu_sprite_refresh
    call fixture_wait_vblank
    call fixture_wait_vblank

    call vdu_affine_identity
    call vdu_affine_scale_singular
    call vdu_sprite_refresh
    ld hl,fixture_singular_message
    jp fixture_show_matrix_status

fixture_request_unbind:
    call fixture_clear_both_transform_bindings
    call vdu_sprite_refresh
    ld hl,fixture_unbound_message
    jp fixture_show_matrix_status

fixture_request_hardware:
    jp fixture_set_right_hardware

fixture_request_software:
    jp fixture_set_right_software

fixture_ensure_transforms_bound:
    ld a,(fixture_transforms_bound)
    or a
    ret nz

fixture_bind_both_transforms:
    ld a,fixture_software_sprite_id
    call vdu_sprite_select
    ld de,fixture_sprite_transform_id
    call vdu_sprite_bind_transform

    ld a,fixture_hardware_sprite_id
    call vdu_sprite_select
    ld de,fixture_sprite_transform_id
    call vdu_sprite_bind_transform

    ld a,1
    ld (fixture_transforms_bound),a
    ret

fixture_clear_both_transform_bindings:
    ld a,fixture_software_sprite_id
    call vdu_sprite_select
    call vdu_sprite_clear_transform

    ld a,fixture_hardware_sprite_id
    call vdu_sprite_select
    call vdu_sprite_clear_transform

    xor a
    ld (fixture_transforms_bound),a
    ret

; Input: HL = zero-terminated status, C = fixed text row. The line is cleared
; first so switching from a longer label never leaves stale characters.
fixture_show_status:
    push hl
    push bc
    ld b,0
    call vdu_text_cursor_move
    ld hl,fixture_status_blank
    call vdu_print_cstr
    pop bc
    ld b,0
    call vdu_text_cursor_move
    pop hl
    jp vdu_print_cstr

fixture_show_backend_status:
    ld c,fixture_backend_status_row
    jp fixture_show_status

fixture_show_matrix_status:
    ld c,fixture_matrix_status_row
    jp fixture_show_status

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
    ld hl,fixture_hardware_message
    call fixture_show_backend_status
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
    ld hl,fixture_software_message
    call fixture_show_backend_status
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
    call fixture_clear_both_transform_bindings
    call vdu_sprite_reset
    call vdu_buffer_clear_all
    call vdu_sprite_affine_disable
    call vdu_affine_matrices_disable
    call vdu_hardware_sprites_disable
    call vdu_hardware_sprite_preference_clear

    ld a,(fixture_saved_screen_mode)
    call vdu_set_screen_mode
    call vdu_logical_coordinates_on
    call vdu_cursor_show
    ret

fixture_help:
    db "Sprite affine regression",13,10
    db "Top raw; bottom SW-left / HW-right",13,10
    db "0 identity  1 translate  2 scale2",13,10
    db "3 rot90  4 shear  5 reflectX",13,10
    db "6 pivot90  7 singular  8 unbind",13,10
    db "H/S right backend; Q/ESC exits",13,10,0

fixture_hardware_message:
    db "Right backend: hardware-requested",0

fixture_software_message:
    db "Right backend: software",0

fixture_identity_message:
    db "M0 identity: both match raw shape",0

fixture_translate_message:
    db "M1 translate (+8,+4)",0

fixture_scale_2_message:
    db "M2 scale 2x: expect 32x32",0

fixture_rotate_90_message:
    db "M3 rotate +90: pixels above anchor",0

fixture_shear_message:
    db "M4 shear X=-0.5: negative X bounds",0

fixture_reflect_x_message:
    db "M5 reflect X: pixels left of anchor",0

fixture_pivot_rotate_90_message:
    db "M6 center-pivot +90: remains 16x16",0

fixture_singular_message:
    db "M7 singular rejected: scale2 remains",0

fixture_unbound_message:
    db "M8 unbound: raw sprites expected",0

fixture_status_blank:
    db "                                       ",0

fixture_saved_screen_mode:
    db 0

fixture_running:
    db 0

fixture_previous_key:
    db 0

fixture_transforms_bound:
    db 0

    include "vdu_system.inc"
    include "vdu_buffer.inc"
    include "vdu_bitmap.inc"
    include "vdu_sprite.inc"
    include "vdu_affine.inc"
    include "fixture_assets.inc"
