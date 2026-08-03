; Torture-suite-only buffered commands. Every packet field wider than one byte
; that is filled at runtime is written bytewise for ADL safety.

; Replace the alternate matrix with identity.
torture_affine_alternate_identity:
    ld hl,torture_affine_alternate_identity_packet
    ld bc,torture_affine_alternate_identity_packet_end-torture_affine_alternate_identity_packet
    jp vdu_send_block

torture_affine_alternate_identity_packet:
    db 23,0,0a0h
    dw torture_alternate_transform_id
    db 20h,0
torture_affine_alternate_identity_packet_end:

; Compose a top-left 90-degree rotation into the alternate matrix.
torture_affine_alternate_rotate_90:
    ld hl,torture_affine_alternate_rotate_90_packet
    ld bc,torture_affine_alternate_rotate_90_packet_end-torture_affine_alternate_rotate_90_packet
    jp vdu_send_block

torture_affine_alternate_rotate_90_packet:
    db 23,0,0a0h
    dw torture_alternate_transform_id
    db 20h,2,0c0h
    dw 90
torture_affine_alternate_rotate_90_packet_end:

; The hidden 352x48 panel becomes 2816x384. Its 1,081,344 output pixels
; exceed the firmware's conservative per-frame admission limit.
torture_affine_panel_identity:
    ld hl,torture_affine_panel_identity_packet
    ld bc,torture_affine_panel_identity_packet_end-torture_affine_panel_identity_packet
    jp vdu_send_block

torture_affine_panel_identity_packet:
    db 23,0,0a0h
    dw torture_panel_transform_id
    db 20h,0
torture_affine_panel_identity_packet_end:

torture_affine_panel_scale_8:
    ld hl,torture_affine_panel_scale_8_packet
    ld bc,torture_affine_panel_scale_8_packet_end-torture_affine_panel_scale_8_packet
    jp vdu_send_block

torture_affine_panel_scale_8_packet:
    db 23,0,0a0h
    dw torture_panel_transform_id
    db 20h,5,0c0h
    dw 8,8
torture_affine_panel_scale_8_packet_end:

; Compose an IEEE-754 quiet NaN X scale and 1.0 Y scale into the primary
; matrix. Format 00h means two 32-bit floating-point operands.
torture_affine_primary_scale_nan:
    ld hl,torture_affine_primary_scale_nan_packet
    ld bc,torture_affine_primary_scale_nan_packet_end-torture_affine_primary_scale_nan_packet
    jp vdu_send_block

torture_affine_primary_scale_nan_packet:
    db 23,0,0a0h
    dw torture_primary_transform_id
    db 20h,5,00h
    db 00h,00h,0c0h,07fh
    db 00h,00h,080h,03fh
torture_affine_primary_scale_nan_packet_end:

; A finite but hostile scale. A 16x16 frame would be 524272 pixels wide, so
; bounds/resource validation must reject it before allocation or publication.
torture_affine_primary_scale_extreme:
    ld hl,torture_affine_primary_scale_extreme_packet
    ld bc,torture_affine_primary_scale_extreme_packet_end-torture_affine_primary_scale_extreme_packet
    jp vdu_send_block

torture_affine_primary_scale_extreme_packet:
    db 23,0,0a0h
    dw torture_primary_transform_id
    db 20h,5,0c0h
    dw 32767,32767
torture_affine_primary_scale_extreme_packet_end:

; XOR every RGBA2222 source byte's colour bits in place while preserving its
; top two alpha bits. Repeating the command restores the original payload.
torture_buffer_adjust_ship:
    ld hl,torture_buffer_adjust_ship_packet
    ld bc,torture_buffer_adjust_ship_packet_end-torture_buffer_adjust_ship_packet
    jp vdu_send_block

torture_buffer_adjust_ship_packet:
    db 23,0,0a0h
    dw torture_ship_buffer_id
    db 5,047h
    dw 0
    dw torture_ship_size
    db 03fh
torture_buffer_adjust_ship_packet_end:

; Queue a regular bitmap plot and replace its Bitmap/backing owner before the
; renderer can consume the raw pointer. Repeat through the transformed bitmap
; primitive. Every same-ID replacement uses the single-colour RGBA8888 bitmap
; command, so it exercises bufferReplacePrepared rather than an in-place write.
; The final screen order is red, cyan, scale-2 red, scale-2 cyan.
torture_queue_plot_lifetime:
    ld hl,torture_queue_plot_lifetime_packet
    ld bc,torture_queue_plot_lifetime_packet_end-torture_queue_plot_lifetime_packet
    jp vdu_send_block

torture_queue_plot_lifetime_packet:
    db 23,27,20h
    dw torture_lifetime_buffer_id

    db 23,27,2
    dw torture_probe_width,torture_probe_height
    db 0ffh,0,0,0ffh
    db 23,0,096h,1
    dw 0ffffh
    db 23,27,3
    dw torture_queue_raw_old_x,torture_probe_y

    db 23,27,2
    dw torture_probe_width,torture_probe_height
    db 0,0ffh,0ffh,0ffh
    db 23,27,3
    dw torture_queue_raw_new_x,torture_probe_y

    db 23,27,2
    dw torture_probe_width,torture_probe_height
    db 0ffh,0,0,0ffh
    db 23,0,096h,1
    dw torture_primary_transform_id
    db 23,27,3
    dw torture_queue_transform_old_x,torture_probe_y

    db 23,27,2
    dw torture_probe_width,torture_probe_height
    db 0,0ffh,0ffh,0ffh
    db 23,27,3
    dw torture_queue_transform_new_x,torture_probe_y

    db 23,0,096h,1
    dw 0ffffh
    db 23,0,0cah
    db 7
torture_queue_plot_lifetime_packet_end:

; Paint the screen-capture source as adjacent opaque red and cyan 8x8 blocks.
; The explicit queue flush belongs before the capture and is not the barrier
; under test.
torture_capture_source:
    ld hl,torture_capture_source_packet
    ld bc,torture_capture_source_packet_end-torture_capture_source_packet
    jp vdu_send_block

torture_capture_source_packet:
    db 23,27,20h
    dw torture_lifetime_buffer_id
    db 23,27,2
    dw torture_probe_width,torture_probe_height
    db 0ffh,0,0,0ffh
    db 23,0,096h,1
    dw 0ffffh
    db 23,27,3
    dw torture_capture_source_old_x,torture_probe_y
    db 23,27,2
    dw torture_probe_width,torture_probe_height
    db 0,0ffh,0ffh,0ffh
    db 23,27,3
    dw torture_capture_source_new_x,torture_probe_y
    db 23,0,0cah
torture_capture_source_packet_end:

; Capture the two source blocks into a fresh 16x8 RGBA2222 bitmap, queue one
; raw plot, and immediately replace active sprite 4's placeholder frame with
; the capture before refreshing its scale-2 cache. There is deliberately no
; queue flush between CopyToBitmap and sprite publication.
torture_capture_consume:
    ld hl,torture_capture_consume_packet
    ld bc,torture_capture_consume_packet_end-torture_capture_consume_packet
    jp vdu_send_block

torture_capture_consume_packet:
    db 25,4
    dw torture_capture_source_old_x,torture_probe_y
    db 25,4
    dw torture_capture_source_new_x+torture_probe_width-1
    dw torture_probe_y+torture_probe_height-1
    db 23,27,21h
    dw torture_capture_buffer_id,0
    db 23,0,096h,1
    dw 0ffffh
    db 23,27,20h
    dw torture_capture_buffer_id
    db 23,27,3
    dw torture_capture_raw_x,torture_probe_y
    db 23,27,4,torture_capture_sprite_id
    db 23,27,35h
    dw torture_capture_buffer_id
    db 23,27,15
torture_capture_consume_packet_end:

; Conditionally call one status-text buffer if selected-sprite VDP variable
; &1413 equals the supplied 16-bit value.
; Input: DE[15:0] = status text buffer, BC[15:0] = expected status.
torture_status_cond_call:
    ld a,e
    ld (torture_status_cond_call_target),a
    ld a,d
    ld (torture_status_cond_call_target+1),a
    ld a,c
    ld (torture_status_cond_call_operand),a
    ld a,b
    ld (torture_status_cond_call_operand+1),a
    ld hl,torture_status_cond_call_packet
    ld bc,torture_status_cond_call_packet_end-torture_status_cond_call_packet
    jp vdu_send_block

torture_status_cond_call_packet:
    db 23,0,0a0h
torture_status_cond_call_target:
    dw 0
    db 6,0c2h
    dw torture_sprite_transform_status_var
torture_status_cond_call_operand:
    dw 0
torture_status_cond_call_packet_end:

; Stream-synchronization probes. These are sent only while test flag 1 is
; absent, so none may execute or alter its target. The disabled handlers must
; nevertheless consume every descriptor and optional argument before the next
; top-level VDU byte is parsed.

; &20: 2D scale, inline operands, per-operand formats (C0 integer 2 and C8
; Q8.8 1.0).
torture_gate_affine_2d:
    ld hl,torture_gate_affine_2d_packet
    ld bc,torture_gate_affine_2d_packet_end-torture_gate_affine_2d_packet
    jp vdu_send_block

torture_gate_affine_2d_packet:
    db 23,0,0a0h
    dw torture_gate_affine_2d_target_id
    db 20h,045h
    db 0c0h
    dw 2
    db 0c8h
    dw 0100h
torture_gate_affine_2d_packet_end:

; &21: 3D scale with buffer-fetched values, advanced 24-bit offsets, and one
; format/descriptor for each of X, Y, and Z.
torture_gate_affine_3d:
    ld hl,torture_gate_affine_3d_packet
    ld bc,torture_gate_affine_3d_packet_end-torture_gate_affine_3d_packet
    jp vdu_send_block

torture_gate_affine_3d_packet:
    db 23,0,0a0h
    dw torture_gate_affine_3d_target_id
    db 21h,075h
    db 0c0h
    dw torture_gate_args_buffer_id
    db 16,0,0
    db 0c8h
    dw torture_gate_args_buffer_id
    db 18,0,0
    db 00h
    dw torture_gate_args_buffer_id
    db 20,0,0
torture_gate_affine_3d_packet_end:

; &22: generic 2x2 MATRIX_SET using one buffer-value/advanced-offset
; descriptor for four contiguous values.
torture_gate_matrix:
    ld hl,torture_gate_matrix_packet
    ld bc,torture_gate_matrix_packet_end-torture_gate_matrix_packet
    jp vdu_send_block

torture_gate_matrix_packet:
    db 23,0,0a0h
    dw torture_gate_matrix_target_id
    db 22h,030h,2,2
    db 0c0h
    dw torture_gate_args_buffer_id
    db 8,0,0
torture_gate_matrix_packet_end:

; &28: resize + explicit width/height + auto-translate. The explicit u16 tail
; must still be consumed while execution is disabled.
torture_gate_transform_bitmap:
    ld hl,torture_gate_transform_bitmap_packet
    ld bc,torture_gate_transform_bitmap_packet_end-torture_gate_transform_bitmap_packet
    jp vdu_send_block

torture_gate_transform_bitmap_packet:
    db 23,0,0a0h
    dw torture_gate_bitmap_target_id
    db 28h,07h
    dw torture_primary_transform_id
    dw torture_ship_buffer_id
    dw torture_ship_width,torture_ship_height
torture_gate_transform_bitmap_packet_end:

; &29 inline form: size byte, advanced source offset, stride word, and limit
; word are all present.
torture_gate_transform_data_inline:
    ld hl,torture_gate_transform_data_inline_packet
    ld bc,torture_gate_transform_data_inline_packet_end-torture_gate_transform_data_inline_packet
    jp vdu_send_block

torture_gate_transform_data_inline_packet:
    db 23,0,0a0h
    dw torture_gate_data_inline_target_id
    db 29h,01fh,0c0h
    dw torture_primary_transform_id
    dw torture_ship_buffer_id
    db 2
    db 0,0,0
    dw 4
    dw 1
torture_gate_transform_data_inline_packet_end:

; &29 buffer-argument form: all optional arguments plus per-block are set;
; size, source offset, stride, and limit each use a buffer ID plus advanced
; 24-bit descriptor.
torture_gate_transform_data_buffer:
    ld hl,torture_gate_transform_data_buffer_packet
    ld bc,torture_gate_transform_data_buffer_packet_end-torture_gate_transform_data_buffer_packet
    jp vdu_send_block

torture_gate_transform_data_buffer_packet:
    db 23,0,0a0h
    dw torture_gate_data_buffer_target_id
    db 29h,07fh,0c0h
    dw torture_primary_transform_id
    dw torture_ship_buffer_id
    dw torture_gate_args_buffer_id
    db 0,0,0
    dw torture_gate_args_buffer_id
    db 1,0,0
    dw torture_gate_args_buffer_id
    db 4,0,0
    dw torture_gate_args_buffer_id
    db 6,0,0
torture_gate_transform_data_buffer_packet_end:

; BEL followed by printable text. It is deliberately a separate top-level VDU
; send after every gated command; hearing the beep and seeing the entire marker
; proves no optional tail captured the following stream bytes.
torture_stream_sync_marker:
    ld hl,torture_stream_sync_marker_packet
    ld bc,torture_stream_sync_marker_packet_end-torture_stream_sync_marker_packet
    jp vdu_send_block

torture_stream_sync_marker_packet:
    db 7
    db "PT SYNC PASS: gated tails consumed"
torture_stream_sync_marker_packet_end:
