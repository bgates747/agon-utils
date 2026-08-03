; Experimental 2D affine-matrix packets used by the regression fixture.
;
; The affine matrix API (test flag 1) and sprite affine renderer (provisional
; test flag 3) are enabled by presence. The recommended flag value is zero.
; All matrix operands below are signed little-endian fixed-point values:
; format C0h is a 16-bit integer and C8h is signed Q8.8.

vdu_affine_matrices_enable:
    ld hl,vdu_affine_matrices_enable_packet
    ld bc,vdu_affine_matrices_enable_packet_end-vdu_affine_matrices_enable_packet
    jp vdu_send_block

vdu_affine_matrices_enable_packet:
    db 23,0,0f8h,01h,00h,00h,00h
vdu_affine_matrices_enable_packet_end:

vdu_affine_matrices_disable:
    ld hl,vdu_affine_matrices_disable_packet
    ld bc,vdu_affine_matrices_disable_packet_end-vdu_affine_matrices_disable_packet
    jp vdu_send_block

vdu_affine_matrices_disable_packet:
    db 23,0,0f9h,01h,00h
vdu_affine_matrices_disable_packet_end:

vdu_sprite_affine_enable:
    ld hl,vdu_sprite_affine_enable_packet
    ld bc,vdu_sprite_affine_enable_packet_end-vdu_sprite_affine_enable_packet
    jp vdu_send_block

vdu_sprite_affine_enable_packet:
    db 23,0,0f8h,03h,00h,00h,00h
vdu_sprite_affine_enable_packet_end:

vdu_sprite_affine_disable:
    ld hl,vdu_sprite_affine_disable_packet
    ld bc,vdu_sprite_affine_disable_packet_end-vdu_sprite_affine_disable_packet
    jp vdu_send_block

vdu_sprite_affine_disable_packet:
    db 23,0,0f9h,03h,00h
vdu_sprite_affine_disable_packet_end:

; Reset matrix 5101h to identity. Operation 0 has no format or operands.
vdu_affine_identity:
    ld hl,vdu_affine_identity_packet
    ld bc,vdu_affine_identity_packet_end-vdu_affine_identity_packet
    jp vdu_send_block

vdu_affine_identity_packet:
    db 23,0,0a0h
    dw vdu_affine_transform_buffer_id
    db 20h,0
vdu_affine_identity_packet_end:

; Compose a translation of (+8,+4) pixels.
vdu_affine_translate_8_4:
    ld hl,vdu_affine_translate_8_4_packet
    ld bc,vdu_affine_translate_8_4_packet_end-vdu_affine_translate_8_4_packet
    jp vdu_send_block

vdu_affine_translate_8_4_packet:
    db 23,0,0a0h
    dw vdu_affine_transform_buffer_id
    db 20h,6,0c0h
    dw 8,4
vdu_affine_translate_8_4_packet_end:

; Compose a 2x scale in both dimensions.
vdu_affine_scale_2:
    ld hl,vdu_affine_scale_2_packet
    ld bc,vdu_affine_scale_2_packet_end-vdu_affine_scale_2_packet
    jp vdu_send_block

vdu_affine_scale_2_packet:
    db 23,0,0a0h
    dw vdu_affine_transform_buffer_id
    db 20h,5,0c0h
    dw 2,2
vdu_affine_scale_2_packet_end:

; Compose a visually anticlockwise 90-degree rotation in screen coordinates.
vdu_affine_rotate_90:
    ld hl,vdu_affine_rotate_90_packet
    ld bc,vdu_affine_rotate_90_packet_end-vdu_affine_rotate_90_packet
    jp vdu_send_block

vdu_affine_rotate_90_packet:
    db 23,0,0a0h
    dw vdu_affine_transform_buffer_id
    db 20h,2,0c0h
    dw 90
vdu_affine_rotate_90_packet_end:

; Compose X shear -0.5, Y shear 0. The resulting local X bounds are negative.
vdu_affine_shear_negative_half_x:
    ld hl,vdu_affine_shear_negative_half_x_packet
    ld bc,vdu_affine_shear_negative_half_x_packet_end-vdu_affine_shear_negative_half_x_packet
    jp vdu_send_block

vdu_affine_shear_negative_half_x_packet:
    db 23,0,0a0h
    dw vdu_affine_transform_buffer_id
    db 20h,8,0c8h
    dw -128,0
vdu_affine_shear_negative_half_x_packet_end:

; Compose an X reflection with Q8.8 scale values -1 and +1.
vdu_affine_reflect_x:
    ld hl,vdu_affine_reflect_x_packet
    ld bc,vdu_affine_reflect_x_packet_end-vdu_affine_reflect_x_packet
    jp vdu_send_block

vdu_affine_reflect_x_packet:
    db 23,0,0a0h
    dw vdu_affine_transform_buffer_id
    db 20h,5,0c8h
    dw -256,256
vdu_affine_reflect_x_packet_end:

; These translations bracket rotate 90 to rotate the 16x16 frame around its
; centre. Matrix operations left-multiply, so send -pivot, rotate, +pivot.
vdu_affine_translate_negative_pivot:
    ld hl,vdu_affine_translate_negative_pivot_packet
    ld bc,vdu_affine_translate_negative_pivot_packet_end-vdu_affine_translate_negative_pivot_packet
    jp vdu_send_block

vdu_affine_translate_negative_pivot_packet:
    db 23,0,0a0h
    dw vdu_affine_transform_buffer_id
    db 20h,6,0c0h
    dw -8,-8
vdu_affine_translate_negative_pivot_packet_end:

vdu_affine_translate_positive_pivot:
    ld hl,vdu_affine_translate_positive_pivot_packet
    ld bc,vdu_affine_translate_positive_pivot_packet_end-vdu_affine_translate_positive_pivot_packet
    jp vdu_send_block

vdu_affine_translate_positive_pivot_packet:
    db 23,0,0a0h
    dw vdu_affine_transform_buffer_id
    db 20h,6,0c0h
    dw 8,8
vdu_affine_translate_positive_pivot_packet_end:

; Compose a singular X scale of zero. A valid implementation must reject this
; candidate and retain its last coherently published transform.
vdu_affine_scale_singular:
    ld hl,vdu_affine_scale_singular_packet
    ld bc,vdu_affine_scale_singular_packet_end-vdu_affine_scale_singular_packet
    jp vdu_send_block

vdu_affine_scale_singular_packet:
    db 23,0,0a0h
    dw vdu_affine_transform_buffer_id
    db 20h,5,0c0h
    dw 0,1
vdu_affine_scale_singular_packet_end:
