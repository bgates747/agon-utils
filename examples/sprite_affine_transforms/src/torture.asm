    .assume adl=1
    .org 0x040000

    jp torture_start

    .align 64
    db "MOS",0,1

    include "torture_config.inc"
    include "mos_api.inc"

torture_start:
    push af
    push bc
    push de
    push ix
    push iy

    call torture_run

    pop iy
    pop ix
    pop de
    pop bc
    pop af
    ld hl,0
    ret

torture_run:
    call torture_capture_screen_mode
    call torture_initialize_ram
    call torture_prepare_vdp
    call torture_upload_status_buffers
    call torture_upload_bitmaps
    call torture_prepare_secondary_matrices
    call torture_create_static_sprites
    call torture_restore_good_state
    call torture_print_ui
    call torture_plot_raw_bitmaps

    ld hl,torture_phase_initial
    call torture_show_phase
    ld a,torture_hardware_sprite_id
    call torture_show_status_for_sprite

torture_main_loop:
    call torture_wait_vblank
    call torture_poll_key

    ld a,(torture_running)
    or a
    jr z,torture_main_loop_done
    jr torture_main_loop

torture_main_loop_done:
    call torture_release_vdp
    ret

torture_capture_screen_mode:
    ld a,mos_sysvars
    rst.lil 08h
    ld a,(ix+sysvar_scrMode)
    ld (torture_saved_screen_mode),a
    ret

torture_initialize_ram:
    xor a
    ld (torture_previous_key),a
    ld (torture_requested_frame),a
    ld a,1
    ld (torture_running),a
    ret

torture_prepare_vdp:
    ld a,torture_screen_mode
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

; Each buffer is executable VDU text, not a zero-terminated CPU string.
; Conditional buffered calls select exactly one of these from VDP variable
; &1413, which makes the experimental status API visible without a VDP-to-eZ80
; bulk readback channel.
torture_upload_status_buffers:
    ld de,torture_status_unbound_buffer
    ld hl,torture_status_unbound_text
    ld bc,torture_status_unbound_text_end-torture_status_unbound_text
    call vdu_buffer_upload

    ld de,torture_status_disabled_buffer
    ld hl,torture_status_disabled_text
    ld bc,torture_status_disabled_text_end-torture_status_disabled_text
    call vdu_buffer_upload

    ld de,torture_status_pending_buffer
    ld hl,torture_status_pending_text
    ld bc,torture_status_pending_text_end-torture_status_pending_text
    call vdu_buffer_upload

    ld de,torture_status_cached_sw_buffer
    ld hl,torture_status_cached_sw_text
    ld bc,torture_status_cached_sw_text_end-torture_status_cached_sw_text
    call vdu_buffer_upload

    ld de,torture_status_cached_hw_buffer
    ld hl,torture_status_cached_hw_text
    ld bc,torture_status_cached_hw_text_end-torture_status_cached_hw_text
    call vdu_buffer_upload

    ld de,torture_status_stale_sw_buffer
    ld hl,torture_status_stale_sw_text
    ld bc,torture_status_stale_sw_text_end-torture_status_stale_sw_text
    call vdu_buffer_upload

    ld de,torture_status_stale_hw_buffer
    ld hl,torture_status_stale_hw_text
    ld bc,torture_status_stale_hw_text_end-torture_status_stale_hw_text
    call vdu_buffer_upload

    ld de,torture_status_invalid_buffer
    ld hl,torture_status_invalid_text
    ld bc,torture_status_invalid_text_end-torture_status_invalid_text
    call vdu_buffer_upload

    ld de,torture_status_resource_buffer
    ld hl,torture_status_resource_text
    ld bc,torture_status_resource_text_end-torture_status_resource_text
    call vdu_buffer_upload

    ld de,torture_status_missing_buffer
    ld hl,torture_status_missing_text
    ld bc,torture_status_missing_text_end-torture_status_missing_text
    jp vdu_buffer_upload

torture_upload_bitmaps:
    ld de,torture_gate_args_buffer_id
    ld hl,torture_gate_args
    ld bc,torture_gate_args_size
    call vdu_buffer_upload

    call torture_upload_ship_bitmap

    ld de,torture_laser_buffer_id
    ld hl,torture_laser_pixels
    ld bc,torture_laser_size
    call vdu_buffer_upload
    ld de,torture_laser_buffer_id
    call vdu_bitmap_select
    ld bc,torture_laser_width
    ld de,torture_laser_height
    ld a,vdu_bitmap_format_rgba2222
    call vdu_bitmap_create

    ld de,torture_mask_buffer_id
    ld hl,torture_mask_pixels
    ld bc,torture_mask_size
    call vdu_buffer_upload
    xor a
    ld c,torture_mask_foreground_colour
    call vdu_gcol
    ld de,torture_mask_buffer_id
    call vdu_bitmap_select
    ld bc,torture_mask_width
    ld de,torture_mask_height
    ld a,vdu_bitmap_format_mask
    call vdu_bitmap_create

    ; 67584 bytes cannot be represented by one buffered-write u16. The first
    ; block is the exact maximum, the second is 2049 bytes, and consolidation
    ; occurs once after both appends.
    ld de,torture_panel_buffer_id
    call vdu_buffer_clear
    ld de,torture_panel_buffer_id
    ld hl,torture_panel_pixels
    ld bc,torture_panel_first_block_size
    call vdu_buffer_append
    ld de,torture_panel_buffer_id
    ld hl,torture_panel_tail
    ld bc,torture_panel_tail_size
    call vdu_buffer_append
    ld de,torture_panel_buffer_id
    call vdu_buffer_consolidate

    ld de,torture_panel_buffer_id
    call vdu_bitmap_select
    ld bc,torture_panel_width
    ld de,torture_panel_height
    ld a,vdu_bitmap_format_rgba8888
    jp vdu_bitmap_create

; This helper deliberately clears and recreates a live bitmap on later reset
; phases. The VDP must detach renderer users before releasing the old backing
; buffer, then accept the new bitmap generation without stale pointers.
torture_upload_ship_bitmap:
    ld de,torture_ship_buffer_id
    ld hl,torture_ship_pixels
    ld bc,torture_ship_size
    call vdu_buffer_upload
    ld de,torture_ship_buffer_id
    call vdu_bitmap_select
    ld bc,torture_ship_width
    ld de,torture_ship_height
    ld a,vdu_bitmap_format_rgba2222
    jp vdu_bitmap_create

torture_prepare_secondary_matrices:
    call torture_affine_alternate_identity
    call torture_affine_alternate_rotate_90
    call torture_affine_panel_identity
    jp torture_affine_panel_scale_8

; Sprites 2 and 3 keep stable source frames while the animated pair is
; repeatedly torn down and rebuilt. Sprite 2 requests hardware with a Mask
; source and therefore must publish through software fallback. Sprite 3 is
; hidden and active but normally unbound; phase P binds its scale-8 panel
; transform just long enough for a cold resource rejection.
torture_create_static_sprites:
    ld a,torture_mask_sprite_id
    call vdu_sprite_select
    call vdu_sprite_clear_frames
    ld de,torture_mask_buffer_id
    call vdu_sprite_add_buffer_frame
    call vdu_sprite_make_software
    ld bc,torture_mask_x
    ld de,torture_sprite_y
    call vdu_sprite_move_absolute
    call vdu_sprite_show
    ld de,torture_primary_transform_id
    call vdu_sprite_bind_transform

    ld a,torture_panel_sprite_id
    call vdu_sprite_select
    call vdu_sprite_clear_frames
    ld de,torture_panel_buffer_id
    call vdu_sprite_add_buffer_frame
    call vdu_sprite_make_software
    ld bc,0
    ld de,0
    call vdu_sprite_move_absolute
    call vdu_sprite_hide
    jp vdu_sprite_clear_transform

; Deterministic baseline used by every destructive phase: original ship bytes,
; primary scale 2, both animation frames rebuilt, bindings restored, and all
; four sprites activated as software before backend requests are re-applied.
torture_restore_good_state:
    call vdu_affine_matrices_enable
    call vdu_sprite_affine_enable
    call torture_upload_ship_bitmap
    call vdu_affine_identity
    call vdu_affine_scale_2

    ld a,torture_software_sprite_id
    call vdu_sprite_select
    call vdu_sprite_clear_frames
    ld de,torture_ship_buffer_id
    call vdu_sprite_add_buffer_frame
    ld de,torture_laser_buffer_id
    call vdu_sprite_add_buffer_frame
    call vdu_sprite_make_software
    ld bc,torture_ship_x
    ld de,torture_sprite_y
    call vdu_sprite_move_absolute
    call vdu_sprite_show
    ld de,torture_primary_transform_id
    call vdu_sprite_bind_transform

    ld a,torture_hardware_sprite_id
    call vdu_sprite_select
    call vdu_sprite_clear_frames
    ld de,torture_ship_buffer_id
    call vdu_sprite_add_buffer_frame
    ld de,torture_laser_buffer_id
    call vdu_sprite_add_buffer_frame
    call vdu_sprite_make_software
    ld bc,torture_laser_x
    ld de,torture_sprite_y
    call vdu_sprite_move_absolute
    call vdu_sprite_show
    ld de,torture_primary_transform_id
    call vdu_sprite_bind_transform

    ld a,torture_mask_sprite_id
    call vdu_sprite_select
    call vdu_sprite_hide
    call vdu_sprite_refresh
    call vdu_sprite_make_software
    call vdu_sprite_show
    ld de,torture_primary_transform_id
    call vdu_sprite_bind_transform

    ld a,torture_panel_sprite_id
    call vdu_sprite_select
    call vdu_sprite_make_software
    call vdu_sprite_hide
    call vdu_sprite_clear_transform

    ld a,torture_sprite_count
    call vdu_sprite_activate

    ld a,torture_hardware_sprite_id
    call torture_request_visible_hardware
    ld a,torture_mask_sprite_id
    call torture_request_visible_hardware
    ld a,torture_panel_sprite_id
    call vdu_sprite_select
    call vdu_sprite_make_hardware
    call vdu_sprite_hide

    xor a
    call torture_select_animated_frame
    call torture_plot_ship_raw
    call vdu_sprite_refresh
    call torture_wait_vblank
    jp torture_wait_vblank

; Input: A = sprite ID. It was just activated as software, so hiding and
; refreshing first safely discards its saved framebuffer image.
torture_request_visible_hardware:
    call vdu_sprite_select
    call vdu_sprite_hide
    call vdu_sprite_refresh
    call vdu_sprite_make_hardware
    call vdu_sprite_show
    jp vdu_sprite_refresh

torture_plot_raw_bitmaps:
    call torture_plot_ship_raw
    ld de,torture_laser_buffer_id
    call vdu_bitmap_select
    ld bc,torture_laser_x
    ld de,torture_raw_y
    call vdu_bitmap_plot
    ld de,torture_mask_buffer_id
    call vdu_bitmap_select
    ld bc,torture_mask_x
    ld de,torture_raw_y
    jp vdu_bitmap_plot

torture_plot_ship_raw:
    ld de,torture_ship_buffer_id
    call vdu_bitmap_select
    ld bc,torture_ship_x
    ld de,torture_raw_y
    jp vdu_bitmap_plot

torture_poll_key:
    ld a,mos_sysvars
    rst.lil 08h

    ld a,(ix+sysvar_vkeydown)
    or a
    jp z,torture_key_released

    ld a,(ix+sysvar_keyascii)
    ld b,a
    ld a,(torture_previous_key)
    cp b
    ret z

    ld a,b
    ld (torture_previous_key),a
    or a
    ret z

    cp 27
    jp z,torture_request_exit
    cp '0'
    jp z,torture_request_reset
    cp '1'
    jp z,torture_request_ship_frame
    cp '2'
    jp z,torture_request_laser_frame
    cp '3'
    jp z,torture_request_source_mutation
    cp '4'
    jp z,torture_request_alternate_binding
    cp '5'
    jp z,torture_request_primary_binding
    cp '6'
    jp z,torture_request_singular
    cp '7'
    jp z,torture_request_nan
    cp '8'
    jp z,torture_request_extreme
    cp '9'
    jp z,torture_request_matrix_clear

    or 20h
    cp 'q'
    jp z,torture_request_exit
    cp 'd'
    jp z,torture_request_disable
    cp 'e'
    jp z,torture_request_reenable
    cp 'c'
    jp z,torture_request_capture_sync
    cp 'k'
    jp z,torture_request_source_clear
    cp 'r'
    jp z,torture_request_reset
    cp 'm'
    jp z,torture_request_mask_status
    cp 'p'
    jp z,torture_request_panel_status
    cp 't'
    jp z,torture_request_stream_sync
    cp 'u'
    jp z,torture_request_queued_plot_lifetime
    ret

torture_key_released:
    xor a
    ld (torture_previous_key),a
    ret

torture_request_exit:
    xor a
    ld (torture_running),a
    ret

torture_request_reset:
    call torture_restore_good_state
    ld hl,torture_phase_reset
    call torture_show_phase
    ld a,torture_hardware_sprite_id
    jp torture_show_status_for_sprite

torture_request_ship_frame:
    call torture_restore_good_state
    xor a
    call torture_select_animated_frame
    call vdu_sprite_refresh
    ld hl,torture_phase_ship_frame
    call torture_show_phase
    ld a,torture_hardware_sprite_id
    jp torture_show_status_for_sprite

torture_request_laser_frame:
    call torture_restore_good_state
    ld a,1
    call torture_select_animated_frame
    call vdu_sprite_refresh
    ld hl,torture_phase_laser_frame
    call torture_show_phase
    ld a,torture_hardware_sprite_id
    jp torture_show_status_for_sprite

; Mutate all 256 ship bytes in place. No bitmap recreation and no transform
; rebind occurs after the mutation; the source generation alone must rebuild
; both transformed frame-0 caches.
torture_request_source_mutation:
    call torture_restore_good_state
    call torture_buffer_adjust_ship
    xor a
    call torture_select_animated_frame
    call torture_plot_ship_raw
    call vdu_sprite_refresh
    ld hl,torture_phase_source_mutation
    call torture_show_phase
    ld a,torture_hardware_sprite_id
    jp torture_show_status_for_sprite

; Only sprite 1 changes IDs. Sprite 0 remains scale-2 on the primary matrix,
; while sprite 1 must become the alternate top-left rotation. Reusing sprite
; 1's primary cache would expose buffer-ID cache contamination immediately.
torture_request_alternate_binding:
    call torture_restore_good_state
    ld a,torture_hardware_sprite_id
    call vdu_sprite_select
    ld de,torture_alternate_transform_id
    call vdu_sprite_bind_transform
    call vdu_sprite_refresh
    ld hl,torture_phase_alternate_binding
    call torture_show_phase
    ld a,torture_hardware_sprite_id
    jp torture_show_status_for_sprite

torture_request_primary_binding:
    call torture_restore_good_state
    ld hl,torture_phase_primary_binding
    call torture_show_phase
    ld a,torture_hardware_sprite_id
    jp torture_show_status_for_sprite

; Each rejection phase first waits for a coherent scale-2 cache, then replaces
; the same live matrix ID without rebinding. Singular and non-finite matrices
; are invalid; the extreme finite matrix fails output admission. All three must
; retain the last-good scale-2 cache.
torture_request_singular:
    call torture_restore_good_state
    call vdu_affine_scale_singular
    call vdu_sprite_refresh
    ld hl,torture_phase_singular
    call torture_show_phase
    ld a,torture_hardware_sprite_id
    call torture_show_status_for_sprite
    jp torture_repair_primary_after_rejection

torture_request_nan:
    call torture_restore_good_state
    call torture_affine_primary_scale_nan
    call vdu_sprite_refresh
    ld hl,torture_phase_nan
    call torture_show_phase
    ld a,torture_software_sprite_id
    call torture_show_status_for_sprite
    jp torture_repair_primary_after_rejection

torture_request_extreme:
    call torture_restore_good_state
    call torture_affine_primary_scale_extreme
    call vdu_sprite_refresh
    ld hl,torture_phase_extreme
    call torture_show_phase
    ld a,torture_hardware_sprite_id
    call torture_show_status_for_sprite
    jp torture_repair_primary_after_rejection

; The stale status text and last-good pixels remain visible, but repair the
; live ID after the one-shot observation so rejected candidates do not retry
; allocation/admission on every later VSYNC. No sprite is rebound.
torture_repair_primary_after_rejection:
    call vdu_affine_identity
    call vdu_affine_scale_2
    jp vdu_sprite_refresh

; An explicit public clear of the matrix buffer is different from internal
; matrix replacement: it unbinds every sprite using that ID.
torture_request_matrix_clear:
    call torture_restore_good_state
    call torture_force_mask_software
    ld de,torture_primary_transform_id
    call vdu_buffer_clear
    call vdu_sprite_refresh
    ld hl,torture_phase_matrix_clear
    call torture_show_phase
    ld a,torture_hardware_sprite_id
    jp torture_show_status_for_sprite

torture_request_disable:
    call torture_restore_good_state
    call torture_force_mask_software
    call vdu_sprite_affine_disable
    call vdu_sprite_refresh
    ld hl,torture_phase_disable
    call torture_show_phase
    ld a,torture_hardware_sprite_id
    jp torture_show_status_for_sprite

; Disable and re-enable within one phase without rebinding. This stays
; deterministic even if the user did not press D first.
torture_request_reenable:
    call torture_restore_good_state
    call torture_force_mask_software
    call vdu_sprite_affine_disable
    call vdu_sprite_refresh
    call torture_wait_vblank
    call torture_wait_vblank
    call vdu_sprite_affine_enable
    call vdu_sprite_refresh
    ld a,torture_mask_sprite_id
    call torture_request_visible_hardware
    ld hl,torture_phase_reenable
    call torture_show_phase
    ld a,torture_hardware_sprite_id
    jp torture_show_status_for_sprite

; Clear a bitmap's backing buffer while two active sprites reference it. The
; VDP must detach safely, clear both sprites' complete frame lists, report
; source missing, and continue rendering the unrelated mask/panel sprites.
torture_request_source_clear:
    call torture_restore_good_state
    ld de,torture_ship_buffer_id
    call vdu_buffer_clear
    call vdu_sprite_refresh
    ld hl,torture_phase_source_clear
    call torture_show_phase
    ld a,torture_hardware_sprite_id
    jp torture_show_status_for_sprite

; A single VDP input block queues raw and transformed RGBA8888 plots, then
; replaces the selected bitmap ID before each old primitive is consumed. Four
; blocks must remain visible left-to-right as red, cyan, scale-2 red, and
; scale-2 cyan. The BEL is a liveness marker after the final explicit flush.
torture_request_queued_plot_lifetime:
    call torture_restore_good_state
    call torture_queue_plot_lifetime
    ld hl,torture_phase_queued_plot_lifetime
    call torture_show_phase
    ld a,torture_hardware_sprite_id
    jp torture_show_status_for_sprite

; Screen-capture a flushed red|cyan source into a fresh ID. Sprite 4 is already
; active with a placeholder frame, so replacing that frame and refreshing does
; not pass through activateSprites()'s unrelated plot barrier. The capture,
; raw plot, frame replacement, and cache refresh are one uninterrupted VDP
; input block. The raw copy must match the source and the S3 sprite must be its
; exact scale-2 image.
torture_request_capture_sync:
    call torture_restore_good_state
    ld de,torture_capture_buffer_id
    call vdu_buffer_clear
    call torture_capture_source

    ld a,torture_capture_sprite_id
    call vdu_sprite_select
    call vdu_sprite_clear_frames
    ld de,torture_lifetime_buffer_id
    call vdu_sprite_add_buffer_frame
    call vdu_sprite_make_software
    ld bc,torture_capture_sprite_x
    ld de,torture_probe_y
    call vdu_sprite_move_absolute
    call vdu_sprite_show
    ld de,torture_primary_transform_id
    call vdu_sprite_bind_transform
    ld a,torture_capture_sprite_count
    call vdu_sprite_activate
    call vdu_sprite_refresh
    call torture_wait_vblank
    call torture_wait_vblank

    call torture_capture_consume
    ld hl,torture_phase_capture_sync
    call torture_show_phase
    ld a,torture_capture_sprite_id
    jp torture_show_status_for_sprite

torture_request_mask_status:
    call torture_restore_good_state
    ld hl,torture_phase_mask_status
    call torture_show_phase
    ld a,torture_mask_sprite_id
    jp torture_show_status_for_sprite

torture_request_panel_status:
    call torture_restore_good_state
    ld a,torture_panel_sprite_id
    call vdu_sprite_select
    ld de,torture_panel_transform_id
    call vdu_sprite_bind_transform
    call vdu_sprite_refresh
    ld hl,torture_phase_panel_status
    call torture_show_phase
    ld a,torture_panel_sprite_id
    call torture_show_status_for_sprite
    ; Leave the rendered S8 oracle on screen, but stop retrying the rejected
    ; allocation every VSYNC once the one-shot phase has observed it.
    ld a,torture_panel_sprite_id
    call vdu_sprite_select
    call vdu_sprite_clear_transform
    jp vdu_sprite_refresh

; With test flag 1 absent, send every gated affine-family opcode and their
; longest materially distinct optional tails. The next independent VDU send
; moves the cursor and emits BEL plus a fixed marker. A full marker and beep
; demonstrate that no disabled command under- or over-consumed the stream.
torture_request_stream_sync:
    call torture_restore_good_state
    call vdu_affine_matrices_disable
    call torture_gate_affine_2d
    call torture_gate_affine_3d
    call torture_gate_matrix
    call torture_gate_transform_bitmap
    call torture_gate_transform_data_inline
    call torture_gate_transform_data_buffer

    ld b,0
    ld c,torture_phase_status_row
    call vdu_text_cursor_move
    ld hl,torture_status_blank
    call vdu_print_cstr
    ld b,0
    ld c,torture_phase_status_row
    call vdu_text_cursor_move
    call torture_stream_sync_marker

    call vdu_affine_matrices_enable
    call vdu_sprite_refresh
    ld a,torture_hardware_sprite_id
    jp torture_show_status_for_sprite

; Input: A = 0 ship or 1 laser. The same frame is selected on both animated
; sprites, proving that all frames were cached transactionally for both paths.
torture_select_animated_frame:
    ld (torture_requested_frame),a
    ld a,torture_software_sprite_id
    call vdu_sprite_select
    ld a,(torture_requested_frame)
    call vdu_sprite_select_frame
    ld a,torture_hardware_sprite_id
    call vdu_sprite_select
    ld a,(torture_requested_frame)
    jp vdu_sprite_select_frame

; A raw Mask cannot use the hardware backend. Phases that deliberately disable
; or remove its transform first return the logical Mask sprite to software so
; the unrelated lifecycle test cannot publish an unsupported raw HW request.
torture_force_mask_software:
    ld a,torture_mask_sprite_id
    call vdu_sprite_select
    call vdu_sprite_hide
    call vdu_sprite_refresh
    call vdu_sprite_make_software
    call vdu_sprite_show
    jp vdu_sprite_refresh

torture_print_ui:
    ld b,0
    ld c,0
    call vdu_text_cursor_move
    ld hl,torture_help
    call vdu_print_cstr

    ld b,0
    ld c,torture_raw_label_row
    call vdu_text_cursor_move
    ld hl,torture_raw_labels
    call vdu_print_cstr

    ld b,0
    ld c,torture_sprite_label_row
    call vdu_text_cursor_move
    ld hl,torture_sprite_labels
    jp vdu_print_cstr

; Input: HL = zero-terminated phase text.
torture_show_phase:
    push hl
    ld b,0
    ld c,torture_phase_status_row
    call vdu_text_cursor_move
    ld hl,torture_status_blank
    call vdu_print_cstr
    ld b,0
    ld c,torture_phase_status_row
    call vdu_text_cursor_move
    pop hl
    jp vdu_print_cstr

; Input: A = sprite ID. Wait for publication, select that sprite for &1413,
; clear the status row, then issue one conditional call per enum value. Exactly
; one uploaded status string should execute.
torture_show_status_for_sprite:
    call vdu_sprite_select
    call vdu_sprite_refresh
    call torture_wait_vblank
    call torture_wait_vblank

    ld b,0
    ld c,torture_vdp_status_row
    call vdu_text_cursor_move
    ld hl,torture_status_blank
    call vdu_print_cstr
    ld b,0
    ld c,torture_vdp_status_row
    call vdu_text_cursor_move

    ld de,torture_status_unbound_buffer
    ld bc,0
    call torture_status_cond_call
    ld de,torture_status_disabled_buffer
    ld bc,1
    call torture_status_cond_call
    ld de,torture_status_pending_buffer
    ld bc,2
    call torture_status_cond_call
    ld de,torture_status_cached_sw_buffer
    ld bc,3
    call torture_status_cond_call
    ld de,torture_status_cached_hw_buffer
    ld bc,4
    call torture_status_cond_call
    ld de,torture_status_stale_sw_buffer
    ld bc,5
    call torture_status_cond_call
    ld de,torture_status_stale_hw_buffer
    ld bc,6
    call torture_status_cond_call
    ld de,torture_status_invalid_buffer
    ld bc,7
    call torture_status_cond_call
    ld de,torture_status_resource_buffer
    ld bc,8
    call torture_status_cond_call
    ld de,torture_status_missing_buffer
    ld bc,9
    jp torture_status_cond_call

torture_wait_vblank:
    ld a,mos_sysvars
    rst.lil 08h
    ld a,(ix+sysvar_time)
torture_wait_vblank_loop:
    cp a,(ix+sysvar_time)
    jr z,torture_wait_vblank_loop
    ret

torture_clear_transform_bindings:
    ld a,torture_software_sprite_id
    call vdu_sprite_select
    call vdu_sprite_clear_transform
    ld a,torture_hardware_sprite_id
    call vdu_sprite_select
    call vdu_sprite_clear_transform
    ld a,torture_mask_sprite_id
    call vdu_sprite_select
    call vdu_sprite_clear_transform
    ld a,torture_panel_sprite_id
    call vdu_sprite_select
    call vdu_sprite_clear_transform
    ld a,torture_capture_sprite_id
    call vdu_sprite_select
    jp vdu_sprite_clear_transform

torture_release_vdp:
    xor a
    call vdu_sprite_activate
    call torture_clear_transform_bindings
    call vdu_sprite_reset
    call vdu_buffer_clear_all
    call vdu_sprite_affine_disable
    call vdu_affine_matrices_disable
    call vdu_hardware_sprites_disable
    call vdu_hardware_sprite_preference_clear

    ld a,(torture_saved_screen_mode)
    call vdu_set_screen_mode
    call vdu_logical_coordinates_on
    call vdu_cursor_show
    ret

torture_help:
    db "Sprite affine lifecycle torture",13,10
    db "0/R reset  1 ship  2 laser  3 mutate",13,10
    db "4 alt-ID  5 primary  6 singular  7 NaN",13,10
    db "8 extreme  9 matrix-clear  D/E flag",13,10
    db "K clear  C capture  U queue  T sync",13,10
    db "M mask  P panel  Q exit",0

torture_raw_labels:
    db "    raw ship      raw laser    raw mask",0

torture_sprite_labels:
    db "    SW anim       HW anim    mask HW>SW",0

torture_phase_initial:
    db "READY scale2/frame0; HW status expected",0
torture_phase_reset:
    db "P0 reset/recreated: scale2 ship",0
torture_phase_ship_frame:
    db "P1 frame0: both transformed ships",0
torture_phase_laser_frame:
    db "P2 frame1: both transformed lasers",0
torture_phase_source_mutation:
    db "P3 live XOR: source generation rebuilt",0
torture_phase_alternate_binding:
    db "P4 only HW binds alt-ID rotation",0
torture_phase_primary_binding:
    db "P5 HW returns to primary scale2",0
torture_phase_singular:
    db "P6 singular rejected; scale2 remains",0
torture_phase_nan:
    db "P7 NaN rejected; scale2 remains",0
torture_phase_extreme:
    db "P8 extreme rejected; scale2 remains",0
torture_phase_matrix_clear:
    db "P9 matrix clear unbinds; raw sprites",0
torture_phase_disable:
    db "PD flag disabled; raw binding retained",0
torture_phase_reenable:
    db "PE reenabled without rebind; cache back",0
torture_phase_source_clear:
    db "PK source clear; anim sprites hidden",0
torture_phase_queued_plot_lifetime:
    db "PU expect red cyan red2x cyan2x; S4",0
torture_phase_capture_sync:
    db "PC red|cyan source=raw=sprite2x; S3",0
torture_phase_mask_status:
    db "PM mask HW request uses SW fallback",0
torture_phase_panel_status:
    db "PP 67584-byte panel cold resource reject",0

torture_status_blank:
    db "                                        ",0

; These are raw buffered VDU text payloads and therefore have no terminators.
torture_status_unbound_text:
    db "S0 unbound"
torture_status_unbound_text_end:
torture_status_disabled_text:
    db "S1 disabled; raw, binding retained"
torture_status_disabled_text_end:
torture_status_pending_text:
    db "S2 pending; matrix missing"
torture_status_pending_text_end:
torture_status_cached_sw_text:
    db "S3 cached software/fallback"
torture_status_cached_sw_text_end:
torture_status_cached_hw_text:
    db "S4 cached hardware"
torture_status_cached_hw_text_end:
torture_status_stale_sw_text:
    db "S5 stale SW; last-good retained"
torture_status_stale_sw_text_end:
torture_status_stale_hw_text:
    db "S6 stale HW; last-good retained"
torture_status_stale_hw_text_end:
torture_status_invalid_text:
    db "S7 invalid; raw/no last-good"
torture_status_invalid_text_end:
torture_status_resource_text:
    db "S8 resource limit; raw/no cache"
torture_status_resource_text_end:
torture_status_missing_text:
    db "S9 source missing; sprite hidden"
torture_status_missing_text_end:

torture_saved_screen_mode:
    db 0
torture_running:
    db 0
torture_previous_key:
    db 0
torture_requested_frame:
    db 0

    include "vdu_system.inc"
    include "vdu_buffer.inc"
    include "vdu_bitmap.inc"
    include "vdu_sprite.inc"
    include "vdu_affine.inc"
    include "torture_vdu.inc"
    include "torture_assets.inc"
