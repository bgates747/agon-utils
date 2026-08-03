; Stable IDs and geometry for the all-format sprite-affine regression suite.

format_screen_mode:                  equ 8

format_rgba2222_buffer_id:           equ 0x5200
format_rgba8888_buffer_id:           equ 0x5201
format_mask_buffer_id:               equ 0x5202
format_transform_buffer_id:          equ 0x5203
vdu_affine_transform_buffer_id:      equ format_transform_buffer_id

format_rgba2222_width:               equ 16
format_rgba2222_height:              equ 16
format_rgba8888_width:               equ 12
format_rgba8888_height:              equ 8
format_mask_width:                   equ 9
format_mask_height:                  equ 5

format_raw_x:                        equ 88
format_software_x:                   equ 144
format_hardware_x:                   equ 232
format_rgba2222_y:                   equ 76
format_rgba8888_y:                   equ 128
format_mask_y:                       equ 180

format_rgba2222_software_sprite_id:  equ 0
format_rgba2222_hardware_sprite_id:  equ 1
format_rgba8888_software_sprite_id:  equ 2
format_rgba8888_hardware_sprite_id:  equ 3
format_mask_software_sprite_id:      equ 4
format_mask_hardware_sprite_id:      equ 5
format_sprite_count:                 equ 6

format_matrix_status_row:            equ 4
format_column_heading_row:           equ 6
format_rgba2222_label_row:           equ 9
format_rgba8888_label_row:           equ 15
format_mask_label_row:               equ 21
; Mode 8 default palette logical 14 is bright cyan, distinct from every
; RGBA8888 alpha-oracle band and easy to recognize after transform.
format_mask_foreground_colour:       equ 14

vdu_bitmap_format_rgba8888:          equ 0
vdu_bitmap_format_rgba2222:          equ 1
vdu_bitmap_format_mask:              equ 2
