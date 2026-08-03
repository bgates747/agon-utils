    .assume adl=1
    .org 0x040000

    jp format_start

    .align 64
    db "MOS",0,1

    include "format_config.inc"
    include "mos_api.inc"

format_start:
    push af
    push bc
    push de
    push ix
    push iy

    call format_run

    pop iy
    pop ix
    pop de
    pop bc
    pop af
    ld hl,0
    ret

format_run:
    call format_capture_screen_mode
    call format_initialize_ram
    call format_prepare_vdp
    call format_upload_bitmaps
    call format_plot_regular_bitmaps

    ld hl,format_help
    call vdu_print_cstr
    call format_show_labels

    ; Publish a matrix before activation so the first sprite render already
    ; exercises transformed private caches instead of a transient raw fallback.
    call vdu_affine_identity
    call vdu_affine_scale_2
    call format_create_sprites
    ld hl,format_scale_2_message
    call format_show_matrix_status

format_main_loop:
    call format_wait_vblank
    call format_poll_key

    ld a,(format_running)
    or a
    jr z,format_main_loop_done
    jr format_main_loop

format_main_loop_done:
    call format_release_vdp
    ret

format_capture_screen_mode:
    ld a,mos_sysvars
    rst.lil 08h
    ld a,(ix+sysvar_scrMode)
    ld (format_saved_screen_mode),a
    ret

format_initialize_ram:
    xor a
    ld (format_previous_key),a
    ld a,1
    ld (format_running),a
    ret

format_prepare_vdp:
    ld a,format_screen_mode
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

; All three generated payloads are comfortably below the one-block 65535-byte
; limit. The wide multi-block torture asset remains a separate stress phase.
format_upload_bitmaps:
    ld de,format_rgba2222_buffer_id
    ld hl,format_rgba2222_pixels
    ld bc,format_rgba2222_size
    call vdu_buffer_upload

    ld de,format_rgba2222_buffer_id
    call vdu_bitmap_select
    ld bc,format_rgba2222_width
    ld de,format_rgba2222_height
    ld a,vdu_bitmap_format_rgba2222
    call vdu_bitmap_create

    ld de,format_rgba8888_buffer_id
    ld hl,format_rgba8888_pixels
    ld bc,format_rgba8888_size
    call vdu_buffer_upload

    ld de,format_rgba8888_buffer_id
    call vdu_bitmap_select
    ld bc,format_rgba8888_width
    ld de,format_rgba8888_height
    ld a,vdu_bitmap_format_rgba8888
    call vdu_bitmap_create

    ld de,format_mask_buffer_id
    ld hl,format_mask_pixels
    ld bc,format_mask_size
    call vdu_buffer_upload

    ; Mask bitmap creation captures the current graphics foreground colour.
    xor a
    ld c,format_mask_foreground_colour
    call vdu_gcol
    ld de,format_mask_buffer_id
    call vdu_bitmap_select
    ld bc,format_mask_width
    ld de,format_mask_height
    ld a,vdu_bitmap_format_mask
    call vdu_bitmap_create
    ret

format_plot_regular_bitmaps:
    ld de,format_rgba2222_buffer_id
    call vdu_bitmap_select
    ld bc,format_raw_x
    ld de,format_rgba2222_y
    call vdu_bitmap_plot

    ld de,format_rgba8888_buffer_id
    call vdu_bitmap_select
    ld bc,format_raw_x
    ld de,format_rgba8888_y
    call vdu_bitmap_plot

    ld de,format_mask_buffer_id
    call vdu_bitmap_select
    ld bc,format_raw_x
    ld de,format_mask_y
    call vdu_bitmap_plot
    ret

; Build all six sprites as software first. Activation allocates the saved
; framebuffer state required by the three later hardware requests.
format_create_sprites:
    ld a,format_rgba2222_software_sprite_id
    call vdu_sprite_select
    call vdu_sprite_clear_frames
    ld de,format_rgba2222_buffer_id
    call vdu_sprite_add_buffer_frame
    call vdu_sprite_make_software
    ld bc,format_software_x
    ld de,format_rgba2222_y
    call vdu_sprite_move_absolute
    call vdu_sprite_show
    ld de,format_transform_buffer_id
    call vdu_sprite_bind_transform

    ld a,format_rgba2222_hardware_sprite_id
    call vdu_sprite_select
    call vdu_sprite_clear_frames
    ld de,format_rgba2222_buffer_id
    call vdu_sprite_add_buffer_frame
    call vdu_sprite_make_software
    ld bc,format_hardware_x
    ld de,format_rgba2222_y
    call vdu_sprite_move_absolute
    call vdu_sprite_show
    ld de,format_transform_buffer_id
    call vdu_sprite_bind_transform

    ld a,format_rgba8888_software_sprite_id
    call vdu_sprite_select
    call vdu_sprite_clear_frames
    ld de,format_rgba8888_buffer_id
    call vdu_sprite_add_buffer_frame
    call vdu_sprite_make_software
    ld bc,format_software_x
    ld de,format_rgba8888_y
    call vdu_sprite_move_absolute
    call vdu_sprite_show
    ld de,format_transform_buffer_id
    call vdu_sprite_bind_transform

    ld a,format_rgba8888_hardware_sprite_id
    call vdu_sprite_select
    call vdu_sprite_clear_frames
    ld de,format_rgba8888_buffer_id
    call vdu_sprite_add_buffer_frame
    call vdu_sprite_make_software
    ld bc,format_hardware_x
    ld de,format_rgba8888_y
    call vdu_sprite_move_absolute
    call vdu_sprite_show
    ld de,format_transform_buffer_id
    call vdu_sprite_bind_transform

    ld a,format_mask_software_sprite_id
    call vdu_sprite_select
    call vdu_sprite_clear_frames
    ld de,format_mask_buffer_id
    call vdu_sprite_add_buffer_frame
    call vdu_sprite_make_software
    ld bc,format_software_x
    ld de,format_mask_y
    call vdu_sprite_move_absolute
    call vdu_sprite_show
    ld de,format_transform_buffer_id
    call vdu_sprite_bind_transform

    ld a,format_mask_hardware_sprite_id
    call vdu_sprite_select
    call vdu_sprite_clear_frames
    ld de,format_mask_buffer_id
    call vdu_sprite_add_buffer_frame
    call vdu_sprite_make_software
    ld bc,format_hardware_x
    ld de,format_mask_y
    call vdu_sprite_move_absolute
    call vdu_sprite_show
    ld de,format_transform_buffer_id
    call vdu_sprite_bind_transform

    ld a,format_sprite_count
    call vdu_sprite_activate

    ld a,format_rgba2222_hardware_sprite_id
    call format_mark_hardware_requested
    ld a,format_rgba8888_hardware_sprite_id
    call format_mark_hardware_requested
    ld a,format_mask_hardware_sprite_id
    call format_mark_hardware_requested
    ret

; Input: A = sprite ID. Hide and refresh while it is still software so the
; renderer cannot leave a stale saved-background image when changing backend.
; Mask deliberately retains a hardware request in logical state but must be
; rendered through the firmware's software fallback.
format_mark_hardware_requested:
    call vdu_sprite_select
    call vdu_sprite_hide
    call vdu_sprite_refresh
    call vdu_sprite_make_hardware
    call vdu_sprite_show
    jp vdu_sprite_refresh

format_poll_key:
    ld a,mos_sysvars
    rst.lil 08h

    ld a,(ix+sysvar_vkeydown)
    or a
    jr z,format_key_released

    ld a,(ix+sysvar_keyascii)
    ld b,a
    ld a,(format_previous_key)
    cp b
    ret z

    ld a,b
    ld (format_previous_key),a
    or a
    ret z

    cp 27
    jp z,format_request_exit
    cp '0'
    jp z,format_request_identity
    cp '2'
    jp z,format_request_scale_2
    cp '3'
    jp z,format_request_rotate_90

    or 20h
    cp 'q'
    jp z,format_request_exit
    ret

format_key_released:
    xor a
    ld (format_previous_key),a
    ret

format_request_exit:
    xor a
    ld (format_running),a
    ret

format_request_identity:
    call vdu_affine_identity
    call vdu_sprite_refresh
    ld hl,format_identity_message
    jp format_show_matrix_status

format_request_scale_2:
    call vdu_affine_identity
    call vdu_affine_scale_2
    call vdu_sprite_refresh
    ld hl,format_scale_2_message
    jp format_show_matrix_status

format_request_rotate_90:
    call vdu_affine_identity
    call vdu_affine_rotate_90
    call vdu_sprite_refresh
    ld hl,format_rotate_90_message
    jp format_show_matrix_status

format_show_labels:
    ld b,0
    ld c,format_column_heading_row
    ld hl,format_column_heading
    call format_print_at

    ld b,0
    ld c,format_rgba2222_label_row
    ld hl,format_rgba2222_label
    call format_print_at

    ld b,0
    ld c,format_rgba8888_label_row
    ld hl,format_rgba8888_label
    call format_print_at

    ld b,0
    ld c,format_mask_label_row
    ld hl,format_mask_label
    jp format_print_at

; Input: B = text column, C = text row, HL = zero-terminated text.
format_print_at:
    push hl
    push bc
    call vdu_text_cursor_move
    pop bc
    pop hl
    jp vdu_print_cstr

format_show_matrix_status:
    push hl
    ld b,0
    ld c,format_matrix_status_row
    call vdu_text_cursor_move
    ld hl,format_status_blank
    call vdu_print_cstr
    ld b,0
    ld c,format_matrix_status_row
    call vdu_text_cursor_move
    pop hl
    jp vdu_print_cstr

format_wait_vblank:
    ld a,mos_sysvars
    rst.lil 08h
    ld a,(ix+sysvar_time)
format_wait_vblank_loop:
    cp a,(ix+sysvar_time)
    jr z,format_wait_vblank_loop
    ret

format_clear_transform_bindings:
    ld a,format_rgba2222_software_sprite_id
    call vdu_sprite_select
    call vdu_sprite_clear_transform
    ld a,format_rgba2222_hardware_sprite_id
    call vdu_sprite_select
    call vdu_sprite_clear_transform
    ld a,format_rgba8888_software_sprite_id
    call vdu_sprite_select
    call vdu_sprite_clear_transform
    ld a,format_rgba8888_hardware_sprite_id
    call vdu_sprite_select
    call vdu_sprite_clear_transform
    ld a,format_mask_software_sprite_id
    call vdu_sprite_select
    call vdu_sprite_clear_transform
    ld a,format_mask_hardware_sprite_id
    call vdu_sprite_select
    call vdu_sprite_clear_transform
    ret

format_release_vdp:
    xor a
    call vdu_sprite_activate
    call format_clear_transform_bindings
    call vdu_sprite_reset
    call vdu_buffer_clear_all
    call vdu_sprite_affine_disable
    call vdu_affine_matrices_disable
    call vdu_hardware_sprites_disable
    call vdu_hardware_sprite_preference_clear

    ld a,(format_saved_screen_mode)
    call vdu_set_screen_mode
    call vdu_logical_coordinates_on
    call vdu_cursor_show
    ret

format_help:
    db "Sprite affine format suite",13,10
    db "raw / software / hardware-requested",13,10
    db "0 identity  2 scale2  3 rotate90",13,10
    db "Q/ESC exits; mask HW must fall back",13,10,0

format_column_heading:
    db "           raw    software   HW-request",0

format_rgba2222_label:
    db "RGBA2222",0

format_rgba8888_label:
    db "RGBA8888",0

format_mask_label:
    db "Mask cyan",0

format_identity_message:
    db "Identity; RGBA A1/A63 must be opaque",0

format_scale_2_message:
    db "Scale2; RGBA A1/A63 must be opaque",0

format_rotate_90_message:
    db "Rotate90; all six remain coherent",0

format_status_blank:
    db "                                       ",0

format_saved_screen_mode:
    db 0

format_running:
    db 0

format_previous_key:
    db 0

    include "vdu_system.inc"
    include "vdu_buffer.inc"
    include "vdu_bitmap.inc"
    include "vdu_sprite.inc"
    include "vdu_affine.inc"
    include "format_assets.inc"
