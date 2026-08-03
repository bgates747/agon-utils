; Regular buffered-bitmap hooks.

; Input: DE[15:0] = buffer/bitmap ID.
vdu_bitmap_select:
    ld a,e
    ld (vdu_bitmap_select_id),a
    ld a,d
    ld (vdu_bitmap_select_id+1),a
    ld hl,vdu_bitmap_select_packet
    ld bc,vdu_bitmap_select_packet_end-vdu_bitmap_select_packet
    jp vdu_send_block

vdu_bitmap_select_packet:
    db 23,27,20h
vdu_bitmap_select_id:
    dw 0
vdu_bitmap_select_packet_end:

; Input: BC[15:0] = width, DE[15:0] = height, A = bitmap format.
vdu_bitmap_create:
    ld (vdu_bitmap_create_format),a
    ld a,c
    ld (vdu_bitmap_create_width),a
    ld a,b
    ld (vdu_bitmap_create_width+1),a
    ld a,e
    ld (vdu_bitmap_create_height),a
    ld a,d
    ld (vdu_bitmap_create_height+1),a
    ld hl,vdu_bitmap_create_packet
    ld bc,vdu_bitmap_create_packet_end-vdu_bitmap_create_packet
    jp vdu_send_block

vdu_bitmap_create_packet:
    db 23,27,21h
vdu_bitmap_create_width:
    dw 0
vdu_bitmap_create_height:
    dw 0
vdu_bitmap_create_format:
    db 0
vdu_bitmap_create_packet_end:

; Direct bitmap draw in pixel coordinates.
; Input: BC[15:0] = x, DE[15:0] = y. Select the bitmap first.
vdu_bitmap_plot:
    ld a,c
    ld (vdu_bitmap_plot_x),a
    ld a,b
    ld (vdu_bitmap_plot_x+1),a
    ld a,e
    ld (vdu_bitmap_plot_y),a
    ld a,d
    ld (vdu_bitmap_plot_y+1),a
    ld hl,vdu_bitmap_plot_packet
    ld bc,vdu_bitmap_plot_packet_end-vdu_bitmap_plot_packet
    jp vdu_send_block

vdu_bitmap_plot_packet:
    db 23,27,3
vdu_bitmap_plot_x:
    dw 0
vdu_bitmap_plot_y:
    dw 0
vdu_bitmap_plot_packet_end:
