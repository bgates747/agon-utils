; Software, hardware, and future affine-sprite hooks.
;
; Hardware sprites require VDP 2.12+ and RGBA2222/RGBA8888 frames. This fixture
; deliberately targets that API level and emits VDP-variable packets without a
; runtime capability probe. Gate those calls before reusing it on older VDPs.

; Input: A = sprite ID (0..255).
vdu_sprite_select:
    ld (vdu_sprite_select_id),a
    ld hl,vdu_sprite_select_packet
    ld bc,vdu_sprite_select_packet_end-vdu_sprite_select_packet
    jp vdu_send_block

vdu_sprite_select_packet:
    db 23,27,4
vdu_sprite_select_id:
    db 0
vdu_sprite_select_packet_end:

vdu_sprite_clear_frames:
    ld hl,vdu_sprite_clear_frames_packet
    ld bc,vdu_sprite_clear_frames_packet_end-vdu_sprite_clear_frames_packet
    jp vdu_send_block

vdu_sprite_clear_frames_packet:
    db 23,27,5
vdu_sprite_clear_frames_packet_end:

; Input: DE[15:0] = bitmap buffer ID.
vdu_sprite_add_buffer_frame:
    ld a,e
    ld (vdu_sprite_add_buffer_frame_id),a
    ld a,d
    ld (vdu_sprite_add_buffer_frame_id+1),a
    ld hl,vdu_sprite_add_buffer_frame_packet
    ld bc,vdu_sprite_add_buffer_frame_packet_end-vdu_sprite_add_buffer_frame_packet
    jp vdu_send_block

vdu_sprite_add_buffer_frame_packet:
    db 23,27,26h
vdu_sprite_add_buffer_frame_id:
    dw 0
vdu_sprite_add_buffer_frame_packet_end:

; Input: A = frame index.
vdu_sprite_select_frame:
    ld (vdu_sprite_select_frame_id),a
    ld hl,vdu_sprite_select_frame_packet
    ld bc,vdu_sprite_select_frame_packet_end-vdu_sprite_select_frame_packet
    jp vdu_send_block

vdu_sprite_select_frame_packet:
    db 23,27,10
vdu_sprite_select_frame_id:
    db 0
vdu_sprite_select_frame_packet_end:

; Input: A = number of contiguous sprites to activate, starting at sprite 0.
; The packet cannot encode 256; use at most 255 simultaneously active sprites.
vdu_sprite_activate:
    ld (vdu_sprite_activate_count),a
    ld hl,vdu_sprite_activate_packet
    ld bc,vdu_sprite_activate_packet_end-vdu_sprite_activate_packet
    jp vdu_send_block

vdu_sprite_activate_packet:
    db 23,27,7
vdu_sprite_activate_count:
    db 0
vdu_sprite_activate_packet_end:

; Input: BC[15:0] = x, DE[15:0] = y.
vdu_sprite_move_absolute:
    ld a,c
    ld (vdu_sprite_move_absolute_x),a
    ld a,b
    ld (vdu_sprite_move_absolute_x+1),a
    ld a,e
    ld (vdu_sprite_move_absolute_y),a
    ld a,d
    ld (vdu_sprite_move_absolute_y+1),a
    ld hl,vdu_sprite_move_absolute_packet
    ld bc,vdu_sprite_move_absolute_packet_end-vdu_sprite_move_absolute_packet
    jp vdu_send_block

vdu_sprite_move_absolute_packet:
    db 23,27,13
vdu_sprite_move_absolute_x:
    dw 0
vdu_sprite_move_absolute_y:
    dw 0
vdu_sprite_move_absolute_packet_end:

vdu_sprite_show:
    ld hl,vdu_sprite_show_packet
    ld bc,vdu_sprite_show_packet_end-vdu_sprite_show_packet
    jp vdu_send_block

vdu_sprite_show_packet:
    db 23,27,11
vdu_sprite_show_packet_end:

vdu_sprite_hide:
    ld hl,vdu_sprite_hide_packet
    ld bc,vdu_sprite_hide_packet_end-vdu_sprite_hide_packet
    jp vdu_send_block

vdu_sprite_hide_packet:
    db 23,27,12
vdu_sprite_hide_packet_end:

vdu_sprite_refresh:
    ld hl,vdu_sprite_refresh_packet
    ld bc,vdu_sprite_refresh_packet_end-vdu_sprite_refresh_packet
    jp vdu_send_block

vdu_sprite_refresh_packet:
    db 23,27,15
vdu_sprite_refresh_packet_end:

; Reset sprites only. This must precede a global VDP buffer clear.
vdu_sprite_reset:
    ld hl,vdu_sprite_reset_packet
    ld bc,vdu_sprite_reset_packet_end-vdu_sprite_reset_packet
    jp vdu_send_block

vdu_sprite_reset_packet:
    db 23,27,17
vdu_sprite_reset_packet_end:

vdu_sprite_make_hardware:
    ld hl,vdu_sprite_make_hardware_packet
    ld bc,vdu_sprite_make_hardware_packet_end-vdu_sprite_make_hardware_packet
    jp vdu_send_block

vdu_sprite_make_hardware_packet:
    db 23,27,19
vdu_sprite_make_hardware_packet_end:

vdu_sprite_make_software:
    ld hl,vdu_sprite_make_software_packet
    ld bc,vdu_sprite_make_software_packet_end-vdu_sprite_make_software_packet
    jp vdu_send_block

vdu_sprite_make_software_packet:
    db 23,27,20
vdu_sprite_make_software_packet_end:

; Hardware-sprite test feature: set VDP variable 2. Current documentation
; recommends value zero; the variable's presence enables the feature.
vdu_hardware_sprites_enable:
    ld hl,vdu_hardware_sprites_enable_packet
    ld bc,vdu_hardware_sprites_enable_packet_end-vdu_hardware_sprites_enable_packet
    jp vdu_send_block

vdu_hardware_sprites_enable_packet:
    db 23,0,0f8h,02h,00h,00h,00h
vdu_hardware_sprites_enable_packet_end:

vdu_hardware_sprites_disable:
    ld hl,vdu_hardware_sprites_disable_packet
    ld bc,vdu_hardware_sprites_disable_packet_end-vdu_hardware_sprites_disable_packet
    jp vdu_send_block

vdu_hardware_sprites_disable_packet:
    db 23,0,0f9h,02h,00h
vdu_hardware_sprites_disable_packet_end:

; Prevent an inherited global "prefer hardware sprites" setting from changing
; the fixture. This scaffold always chooses each sprite explicitly.
vdu_hardware_sprite_preference_clear:
    ld hl,vdu_hardware_sprite_preference_clear_packet
    ld bc,vdu_hardware_sprite_preference_clear_packet_end-vdu_hardware_sprite_preference_clear_packet
    jp vdu_send_block

vdu_hardware_sprite_preference_clear_packet:
    db 23,0,0f9h,00h,04h
vdu_hardware_sprite_preference_clear_packet_end:

; Proposed sprite-affine firmware hook. Select a sprite first, then pass its
; matrix buffer ID in DE. Stock VDP v2.16 safely ignores unknown variable 1412h.
vdu_sprite_bind_transform:
    ld a,e
    ld (vdu_sprite_bind_transform_id),a
    ld a,d
    ld (vdu_sprite_bind_transform_id+1),a
    ld hl,vdu_sprite_bind_transform_packet
    ld bc,vdu_sprite_bind_transform_packet_end-vdu_sprite_bind_transform_packet
    jp vdu_send_block

vdu_sprite_bind_transform_packet:
    db 23,0,0f8h,12h,14h
vdu_sprite_bind_transform_id:
    dw 0
vdu_sprite_bind_transform_packet_end:

vdu_sprite_clear_transform:
    ld hl,vdu_sprite_clear_transform_packet
    ld bc,vdu_sprite_clear_transform_packet_end-vdu_sprite_clear_transform_packet
    jp vdu_send_block

vdu_sprite_clear_transform_packet:
    db 23,0,0f8h,12h,14h,0ffh,0ffh
vdu_sprite_clear_transform_packet_end:
