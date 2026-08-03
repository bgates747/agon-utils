; Small, application-neutral VDU stream helpers.

; Input: HL = stream address, BC = byte count (zero-extended).
; Destroys: AF, BC, DE, HL.
vdu_send_block:
    xor a
    rst.lil 18h
    ret

; Input: HL = zero-terminated string.
; Destroys: AF, BC, DE, HL.
vdu_print_cstr:
    ld bc,0
    xor a
    rst.lil 18h
    ret

; Input: B = text column, C = text row.
vdu_text_cursor_move:
    ld a,b
    ld (vdu_text_cursor_move_x),a
    ld a,c
    ld (vdu_text_cursor_move_y),a
    ld hl,vdu_text_cursor_move_packet
    ld bc,vdu_text_cursor_move_packet_end-vdu_text_cursor_move_packet
    jp vdu_send_block

vdu_text_cursor_move_packet:
    db 31
vdu_text_cursor_move_x:
    db 0
vdu_text_cursor_move_y:
    db 0
vdu_text_cursor_move_packet_end:

; Input: A = screen mode.
vdu_set_screen_mode:
    ld (vdu_set_screen_mode_value),a
    ld hl,vdu_set_screen_mode_packet
    ld bc,vdu_set_screen_mode_packet_end-vdu_set_screen_mode_packet
    jp vdu_send_block

vdu_set_screen_mode_packet:
    db 22
vdu_set_screen_mode_value:
    db 0
vdu_set_screen_mode_packet_end:

vdu_clear_screen:
    ld hl,vdu_clear_screen_packet
    ld bc,vdu_clear_screen_packet_end-vdu_clear_screen_packet
    jp vdu_send_block

vdu_clear_screen_packet:
    db 12
vdu_clear_screen_packet_end:

vdu_cursor_hide:
    ld hl,vdu_cursor_hide_packet
    ld bc,vdu_cursor_hide_packet_end-vdu_cursor_hide_packet
    jp vdu_send_block

vdu_cursor_hide_packet:
    db 23,1,0
vdu_cursor_hide_packet_end:

vdu_cursor_show:
    ld hl,vdu_cursor_show_packet
    ld bc,vdu_cursor_show_packet_end-vdu_cursor_show_packet
    jp vdu_send_block

vdu_cursor_show_packet:
    db 23,1,1
vdu_cursor_show_packet_end:

vdu_logical_coordinates_off:
    ld hl,vdu_logical_coordinates_off_packet
    ld bc,vdu_logical_coordinates_off_packet_end-vdu_logical_coordinates_off_packet
    jp vdu_send_block

vdu_logical_coordinates_off_packet:
    db 23,0,0c0h,0
vdu_logical_coordinates_off_packet_end:

vdu_logical_coordinates_on:
    ld hl,vdu_logical_coordinates_on_packet
    ld bc,vdu_logical_coordinates_on_packet_end-vdu_logical_coordinates_on_packet
    jp vdu_send_block

vdu_logical_coordinates_on_packet:
    db 23,0,0c0h,1
vdu_logical_coordinates_on_packet_end:

; Input: A = graphics paint mode, C = logical foreground colour.
vdu_gcol:
    ld (vdu_gcol_mode),a
    ld a,c
    ld (vdu_gcol_colour),a
    ld hl,vdu_gcol_packet
    ld bc,vdu_gcol_packet_end-vdu_gcol_packet
    jp vdu_send_block

vdu_gcol_packet:
    db 18
vdu_gcol_mode:
    db 0
vdu_gcol_colour:
    db 0
vdu_gcol_packet_end:
