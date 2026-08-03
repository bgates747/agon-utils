; Stable IDs and geometry for the self-contained regression fixture.

fixture_screen_mode:              equ 8

fixture_bitmap_buffer_id:         equ 0x5100
fixture_sprite_transform_id:      equ 0x5101
vdu_affine_transform_buffer_id:   equ fixture_sprite_transform_id

fixture_bitmap_width:             equ 16
fixture_bitmap_height:            equ 16
fixture_bitmap_x:                 equ 152
fixture_bitmap_y:                 equ 64

fixture_software_sprite_id:       equ 0
fixture_hardware_sprite_id:       equ 1
fixture_sprite_count:             equ 2
fixture_software_sprite_x:        equ 72
fixture_hardware_sprite_x:        equ 232
fixture_sprite_y:                 equ 168

fixture_backend_status_row:       equ 6
fixture_matrix_status_row:        equ 7

vdu_bitmap_format_rgba8888:       equ 0
vdu_bitmap_format_rgba2222:       equ 1
vdu_bitmap_format_mask:           equ 2
