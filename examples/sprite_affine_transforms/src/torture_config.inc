; Stable IDs and geometry for the lifecycle/generation/resource torture suite.

torture_screen_mode:                 equ 8

torture_ship_buffer_id:              equ 0x5300
torture_laser_buffer_id:             equ 0x5301
torture_mask_buffer_id:              equ 0x5302
torture_primary_transform_id:        equ 0x5303
torture_alternate_transform_id:      equ 0x5304
torture_panel_transform_id:          equ 0x5305
torture_panel_buffer_id:             equ 0x5306
torture_gate_args_buffer_id:         equ 0x5307
torture_lifetime_buffer_id:          equ 0x5308
torture_capture_buffer_id:           equ 0x5309
vdu_affine_transform_buffer_id:      equ torture_primary_transform_id

torture_gate_affine_2d_target_id:    equ 0x53c0
torture_gate_affine_3d_target_id:    equ 0x53c1
torture_gate_matrix_target_id:       equ 0x53c2
torture_gate_bitmap_target_id:       equ 0x53c3
torture_gate_data_inline_target_id:  equ 0x53c4
torture_gate_data_buffer_target_id:  equ 0x53c5

torture_status_buffer_base:          equ 0x53a0
torture_status_unbound_buffer:       equ torture_status_buffer_base+0
torture_status_disabled_buffer:      equ torture_status_buffer_base+1
torture_status_pending_buffer:       equ torture_status_buffer_base+2
torture_status_cached_sw_buffer:     equ torture_status_buffer_base+3
torture_status_cached_hw_buffer:     equ torture_status_buffer_base+4
torture_status_stale_sw_buffer:      equ torture_status_buffer_base+5
torture_status_stale_hw_buffer:      equ torture_status_buffer_base+6
torture_status_invalid_buffer:       equ torture_status_buffer_base+7
torture_status_resource_buffer:      equ torture_status_buffer_base+8
torture_status_missing_buffer:       equ torture_status_buffer_base+9

torture_ship_width:                  equ 16
torture_ship_height:                 equ 16
torture_laser_width:                 equ 5
torture_laser_height:                equ 13
torture_mask_width:                  equ 9
torture_mask_height:                 equ 5
torture_panel_width:                 equ 352
torture_panel_height:                equ 48
torture_probe_width:                 equ 8
torture_probe_height:                equ 8

torture_ship_x:                      equ 48
torture_laser_x:                     equ 144
torture_mask_x:                      equ 240
torture_raw_y:                       equ 112
torture_sprite_y:                    equ 168
torture_probe_y:                     equ 76
torture_queue_raw_old_x:             equ 8
torture_queue_raw_new_x:             equ 24
torture_queue_transform_old_x:       equ 48
torture_queue_transform_new_x:       equ 72
torture_capture_source_old_x:        equ 112
torture_capture_source_new_x:        equ 120
torture_capture_raw_x:               equ 144
torture_capture_sprite_x:            equ 176

torture_software_sprite_id:          equ 0
torture_hardware_sprite_id:          equ 1
torture_mask_sprite_id:              equ 2
torture_panel_sprite_id:             equ 3
torture_capture_sprite_id:           equ 4
torture_sprite_count:                equ 4
torture_capture_sprite_count:        equ 5

torture_phase_status_row:            equ 6
torture_vdp_status_row:              equ 7
torture_raw_label_row:               equ 12
torture_sprite_label_row:            equ 19
torture_mask_foreground_colour:      equ 14

torture_sprite_transform_status_var: equ 0x1413

torture_panel_first_block_size:      equ 65535
torture_panel_tail_size:             equ 2049

vdu_bitmap_format_rgba8888:          equ 0
vdu_bitmap_format_rgba2222:          equ 1
vdu_bitmap_format_mask:              equ 2
