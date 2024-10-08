; Generated by build_91b_asm_cfont.py
num_fonts: equ 11

; Index list:
8_bit_fortress_Regular_9x8: equ 0
computerfont_Regular_18x25: equ 1
computerfont_Regular_21x30: equ 2
planetary_contact_Regular_8x11: equ 3
computer_pixel_7_Regular_8x17: equ 4
super_mario_bros_2_Regular_8x9: equ 5
wendy_neue_Regular_6x8: equ 6
wendy_neue_Regular_5x7: equ 7
wendy_neue_Regular_6x7: equ 8
neutrino_Regular_5x10: equ 9
neutrino_Regular_5x5: equ 10

font_list: ; width; height; filesize; filename;:
	dl 6, 8, 0, fn_8_bit_fortress_Regular_9x8
	dl 18, 25, 0, fn_computerfont_Regular_18x25
	dl 20, 28, 0, fn_computerfont_Regular_21x30
	dl 8, 11, 0, fn_planetary_contact_Regular_8x11
	dl 8, 17, 0, fn_computer_pixel_7_Regular_8x17
	dl 8, 9, 0, fn_super_mario_bros_2_Regular_8x9
	dl 6, 8, 0, fn_wendy_neue_Regular_6x8
	dl 5, 7, 0, fn_wendy_neue_Regular_5x7
	dl 6, 7, 0, fn_wendy_neue_Regular_6x7
	dl 5, 10, 0, fn_neutrino_Regular_5x10
	dl 5, 5, 0, fn_neutrino_Regular_5x5

; files_list: ; filename:
fn_8_bit_fortress_Regular_9x8: db "ttf/8_bit_fortress_Regular_9x8.font",0
fn_computerfont_Regular_18x25: db "ttf/computerfont_Regular_18x25.font",0
fn_computerfont_Regular_21x30: db "ttf/computerfont_Regular_21x30.font",0
fn_planetary_contact_Regular_8x11: db "ttf/planetary_contact_Regular_8x11.font",0
fn_computer_pixel_7_Regular_8x17: db "ttf/computer_pixel_7_Regular_8x17.font",0
fn_super_mario_bros_2_Regular_8x9: db "ttf/super_mario_bros_2_Regular_8x9.font",0
fn_wendy_neue_Regular_6x8: db "ttf/wendy_neue_Regular_6x8.font",0
fn_wendy_neue_Regular_5x7: db "ttf/wendy_neue_Regular_5x7.font",0
fn_wendy_neue_Regular_6x7: db "ttf/wendy_neue_Regular_6x7.font",0
fn_neutrino_Regular_5x10: db "ttf/neutrino_Regular_5x10.font",0
fn_neutrino_Regular_5x5: db "ttf/neutrino_Regular_5x5.font",0