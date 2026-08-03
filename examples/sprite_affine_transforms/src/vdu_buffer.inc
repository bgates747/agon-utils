; Buffered-command upload hooks.
;
; All VDU u16 fields are written bytewise. In ADL mode an unsuffixed store
; from BC/DE/HL would write three bytes and corrupt the next packet field.

; Input: DE[15:0] = buffer ID.
vdu_buffer_clear:
    ld a,e
    ld (vdu_buffer_clear_id),a
    ld a,d
    ld (vdu_buffer_clear_id+1),a
    ld hl,vdu_buffer_clear_packet
    ld bc,vdu_buffer_clear_packet_end-vdu_buffer_clear_packet
    jp vdu_send_block

vdu_buffer_clear_packet:
    db 23,0,0a0h
vdu_buffer_clear_id:
    dw 0
    db 2
vdu_buffer_clear_packet_end:

; Input: DE[15:0] = buffer ID, HL = payload, BC = payload bytes.
; BC must be zero-extended and in the range 1..65535.
vdu_buffer_append:
    call vdu_buffer_validate_block_length
    ret nc

    ld a,e
    ld (vdu_buffer_append_id),a
    ld a,d
    ld (vdu_buffer_append_id+1),a
    ld a,c
    ld (vdu_buffer_append_length),a
    ld a,b
    ld (vdu_buffer_append_length+1),a

    push hl
    push bc
    ld hl,vdu_buffer_append_packet
    ld bc,vdu_buffer_append_packet_end-vdu_buffer_append_packet
    call vdu_send_block
    pop bc
    pop hl
    jp vdu_send_block

vdu_buffer_append_packet:
    db 23,0,0a0h
vdu_buffer_append_id:
    dw 0
    db 0
vdu_buffer_append_length:
    dw 0
vdu_buffer_append_packet_end:

; Input: DE[15:0] = buffer ID.
vdu_buffer_consolidate:
    ld a,e
    ld (vdu_buffer_consolidate_id),a
    ld a,d
    ld (vdu_buffer_consolidate_id+1),a
    ld hl,vdu_buffer_consolidate_packet
    ld bc,vdu_buffer_consolidate_packet_end-vdu_buffer_consolidate_packet
    jp vdu_send_block

vdu_buffer_consolidate_packet:
    db 23,0,0a0h
vdu_buffer_consolidate_id:
    dw 0
    db 14
vdu_buffer_consolidate_packet_end:

; Convenience path for one block. Larger loaders can call append repeatedly,
; then consolidate once. Create the bitmap only after consolidation.
; Input: DE[15:0] = buffer ID, HL = payload, BC = payload bytes.
vdu_buffer_upload:
    call vdu_buffer_validate_block_length
    ret nc

    push hl
    push bc
    push de
    call vdu_buffer_clear
    pop de
    pop bc
    pop hl

    push de
    call vdu_buffer_append
    pop de
    jp vdu_buffer_consolidate

; Reject a zero length or a non-zero BCU. If the 24-bit count reached the RST
; stream while only its low word was advertised in the packet, excess bytes
; would be interpreted as new top-level VDU commands.
; Input: BC = proposed block length. Preserves BC, DE, HL.
; Output: carry set for 1..65535; carry clear otherwise.
vdu_buffer_validate_block_length:
    push hl
    push de
    ld hl,0
    add hl,bc
    ld de,010000h
    or a
    sbc hl,de
    jr nc,vdu_buffer_block_length_invalid

    ld a,b
    or c
    jr z,vdu_buffer_block_length_invalid
    scf
    jr vdu_buffer_block_length_done

vdu_buffer_block_length_invalid:
    or a

vdu_buffer_block_length_done:
    pop de
    pop hl
    ret

; Global clear. Call vdu_sprite_reset first so no sprite retains a bitmap
; pointer into a buffer that is about to disappear.
vdu_buffer_clear_all:
    ld hl,vdu_buffer_clear_all_packet
    ld bc,vdu_buffer_clear_all_packet_end-vdu_buffer_clear_all_packet
    jp vdu_send_block

vdu_buffer_clear_all_packet:
    db 23,0,0a0h,0ffh,0ffh,2
vdu_buffer_clear_all_packet_end:
