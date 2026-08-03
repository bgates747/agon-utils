; Generated image inputs embedded without a container. The wide RGBA8888
; payload intentionally crosses the u16 VDU write boundary.

torture_ship_pixels:
    incbin "../assets/rgba2222/ship_1c.rgba2222"
torture_ship_pixels_end:
torture_ship_size: equ torture_ship_pixels_end-torture_ship_pixels

torture_laser_pixels:
    incbin "../assets/rgba2222/laser_a_5x13.rgba2222"
torture_laser_pixels_end:
torture_laser_size: equ torture_laser_pixels_end-torture_laser_pixels

torture_mask_pixels:
    incbin "../assets/mask/mask_9x5_msb.mask"
torture_mask_pixels_end:
torture_mask_size: equ torture_mask_pixels_end-torture_mask_pixels

torture_panel_pixels:
    incbin "../assets/rgba8888/ctl_panel_top_352x48.rgba8888"
torture_panel_pixels_end:
torture_panel_size: equ torture_panel_pixels_end-torture_panel_pixels

torture_panel_tail: equ torture_panel_pixels+torture_panel_first_block_size

; Safe values for the disabled-feature buffer-descriptor probes. If a broken
; gate accidentally executes instead of merely consuming its tail, these
; bounded arguments still cannot request a hostile offset, stride, or limit.
torture_gate_args:
    db 2                  ; 00: transform-data element size
    db 0,0,0              ; 01: transform-data source offset
    dw 4                  ; 04: transform-data stride
    dw 1                  ; 06: transform-data item limit
    dw 1,0,0,1            ; 08: 2x2 C0 identity values
    dw 1                  ; 16: 3D X scale, C0 integer
    dw 0100h              ; 18: 3D Y scale, C8 Q8.8
    db 00h,00h,080h,03fh  ; 20: 3D Z scale, float 1.0
torture_gate_args_end:
torture_gate_args_size: equ torture_gate_args_end-torture_gate_args
