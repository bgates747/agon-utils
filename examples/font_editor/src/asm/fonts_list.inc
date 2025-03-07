; Generated by asm_config_editor.py
font_list_record_size: equ 12
font_list_width: equ 0
font_list_height: equ 3
font_list_bufferId: equ 6
font_list_filename: equ 9

num_fonts: equ 29

; Index list:
amiga_forever_16x16: equ 64000
amiga_forever_16x24: equ 64001
amiga_forever_8x16: equ 64002
amiga_forever_8x8: equ 64003
computer_pixel_7_10x15: equ 64004
computer_pixel_7_10x24: equ 64005
computer_pixel_7_8x12: equ 64006
computer_pixel_7_8x14: equ 64007
computer_pixel_7_8x16: equ 64008
dopecre_8x8: equ 64009
gamer_2_8x8: equ 64010
Lat15_VGA8_8x8: equ 64011
Lat2_Terminus12x6_6x12: equ 64012
Lat2_TerminusBold14_8x14: equ 64013
Lat2_VGA14_8x14: equ 64014
Lat2_VGA16_8x16: equ 64015
Lat2_VGA8_8x8: equ 64016
Lat38_VGA8_8x8: equ 64017
Lat7_Fixed13_8x13: equ 64018
Lat7_Terminus12x6_6x12: equ 64019
Lat7_TerminusBold16_8x16: equ 64020
Lat7_VGA14_8x14: equ 64021
Lat7_VGA16_8x16: equ 64022
Lat7_VGA8_8x8: equ 64023
planetary_contact_8x8: equ 64024
scriptorium_12x14: equ 64025
Squarewave_Bold_8x12: equ 64026
super_mario_bros_2_8x8: equ 64027
wendy_neue_6x6: equ 64028

font_list: ; width; height; bufferId; filename;:
	dl 16, 16, 64000, fn_amiga_forever_16x16
	dl 16, 24, 64001, fn_amiga_forever_16x24
	dl 8, 16, 64002, fn_amiga_forever_8x16
	dl 8, 8, 64003, fn_amiga_forever_8x8
	dl 10, 15, 64004, fn_computer_pixel_7_10x15
	dl 10, 24, 64005, fn_computer_pixel_7_10x24
	dl 8, 12, 64006, fn_computer_pixel_7_8x12
	dl 8, 14, 64007, fn_computer_pixel_7_8x14
	dl 8, 16, 64008, fn_computer_pixel_7_8x16
	dl 8, 8, 64009, fn_dopecre_8x8
	dl 8, 8, 64010, fn_gamer_2_8x8
	dl 8, 8, 64011, fn_Lat15_VGA8_8x8
	dl 6, 12, 64012, fn_Lat2_Terminus12x6_6x12
	dl 8, 14, 64013, fn_Lat2_TerminusBold14_8x14
	dl 8, 14, 64014, fn_Lat2_VGA14_8x14
	dl 8, 16, 64015, fn_Lat2_VGA16_8x16
	dl 8, 8, 64016, fn_Lat2_VGA8_8x8
	dl 8, 8, 64017, fn_Lat38_VGA8_8x8
	dl 8, 13, 64018, fn_Lat7_Fixed13_8x13
	dl 6, 12, 64019, fn_Lat7_Terminus12x6_6x12
	dl 8, 16, 64020, fn_Lat7_TerminusBold16_8x16
	dl 8, 14, 64021, fn_Lat7_VGA14_8x14
	dl 8, 16, 64022, fn_Lat7_VGA16_8x16
	dl 8, 8, 64023, fn_Lat7_VGA8_8x8
	dl 8, 8, 64024, fn_planetary_contact_8x8
	dl 12, 14, 64025, fn_scriptorium_12x14
	dl 8, 12, 64026, fn_Squarewave_Bold_8x12
	dl 8, 8, 64027, fn_super_mario_bros_2_8x8
	dl 6, 6, 64028, fn_wendy_neue_6x6

; files_list: ; filename:
fn_amiga_forever_16x16: db "fontsamiga_forever_16x16.font",0
fn_amiga_forever_16x24: db "fontsamiga_forever_16x24.font",0
fn_amiga_forever_8x16: db "fontsamiga_forever_8x16.font",0
fn_amiga_forever_8x8: db "fontsamiga_forever_8x8.font",0
fn_computer_pixel_7_10x15: db "fontscomputer_pixel_7_10x15.font",0
fn_computer_pixel_7_10x24: db "fontscomputer_pixel_7_10x24.font",0
fn_computer_pixel_7_8x12: db "fontscomputer_pixel_7_8x12.font",0
fn_computer_pixel_7_8x14: db "fontscomputer_pixel_7_8x14.font",0
fn_computer_pixel_7_8x16: db "fontscomputer_pixel_7_8x16.font",0
fn_dopecre_8x8: db "fontsdopecre_8x8.font",0
fn_gamer_2_8x8: db "fontsgamer_2_8x8.font",0
fn_Lat15_VGA8_8x8: db "fontsLat15-VGA8_8x8.font",0
fn_Lat2_Terminus12x6_6x12: db "fontsLat2-Terminus12x6_6x12.font",0
fn_Lat2_TerminusBold14_8x14: db "fontsLat2-TerminusBold14_8x14.font",0
fn_Lat2_VGA14_8x14: db "fontsLat2-VGA14_8x14.font",0
fn_Lat2_VGA16_8x16: db "fontsLat2-VGA16_8x16.font",0
fn_Lat2_VGA8_8x8: db "fontsLat2-VGA8_8x8.font",0
fn_Lat38_VGA8_8x8: db "fontsLat38-VGA8_8x8.font",0
fn_Lat7_Fixed13_8x13: db "fontsLat7-Fixed13_8x13.font",0
fn_Lat7_Terminus12x6_6x12: db "fontsLat7-Terminus12x6_6x12.font",0
fn_Lat7_TerminusBold16_8x16: db "fontsLat7-TerminusBold16_8x16.font",0
fn_Lat7_VGA14_8x14: db "fontsLat7-VGA14_8x14.font",0
fn_Lat7_VGA16_8x16: db "fontsLat7-VGA16_8x16.font",0
fn_Lat7_VGA8_8x8: db "fontsLat7-VGA8_8x8.font",0
fn_planetary_contact_8x8: db "fontsplanetary_contact_8x8.font",0
fn_scriptorium_12x14: db "fontsscriptorium_12x14.font",0
fn_Squarewave_Bold_8x12: db "fontsSquarewave_Bold_8x12.font",0
fn_super_mario_bros_2_8x8: db "fontssuper_mario_bros_2_8x8.font",0
fn_wendy_neue_6x6: db "fontswendy_neue_6x6.font",0
