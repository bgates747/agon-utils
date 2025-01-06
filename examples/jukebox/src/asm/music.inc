; This file is created by build_98_asm_sfx.py, do not edit it!

SFX_num_buffers: equ 1

sample_rate: equ 15360
; SFX buffer ids:
BUF_AMBIENT_BEAT70: equ 0x3000

; SFX buffer id reverse lookup:
SFX_buffer_id_lut:
	dl BUF_AMBIENT_BEAT70

; SFX duration lookup:
SFX_duration_lut:
	dl 30121 ; AMBIENT_BEAT70

; SFX load routines jump table:
SFX_load_routines_table:
	dl load_sfx_AMBIENT_BEAT70

; Import sfx .raw files and load them into VDP buffers

load_sfx_AMBIENT_BEAT70:
	ld hl,BUF_AMBIENT_BEAT70
	ld de,15360
	ld iy,FAMBIENT_BEAT70
	call vdu_load_sfx
	ret

; File name lookups:
FAMBIENT_BEAT70: db "music/AMBIENT_BEAT70.raw",0

; Play sfx routines

sfx_play_AMBIENT_BEAT70:
	ld hl,BUF_AMBIENT_BEAT70
	ld bc,0
	jp vdu_play_sfx
