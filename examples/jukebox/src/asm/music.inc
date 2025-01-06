; This file is created by build_98_asm_sfx.py, do not edit it!

SFX_num_buffers: equ 10

sample_rate: equ 16384
; SFX buffer ids:
BUF_AFRICA: equ 0x3000
BUF_ANYTIME: equ 0x3001
BUF_BARRACUDA: equ 0x3002
BUF_COME_UNDONE: equ 0x3003
BUF_EVERY_BREATH_YOU_TAKE: equ 0x3004
BUF_JUKE_BOX_HERO: equ 0x3005
BUF_RHIANNON: equ 0x3006
BUF_TAKE_A_RIDE: equ 0x3007
BUF_WILD_FLOWER: equ 0x3008
BUF_WONT_GET_FOOLED_AGAIN: equ 0x3009

; SFX buffer id reverse lookup:
SFX_buffer_id_lut:
	dl BUF_AFRICA
	dl BUF_ANYTIME
	dl BUF_BARRACUDA
	dl BUF_COME_UNDONE
	dl BUF_EVERY_BREATH_YOU_TAKE
	dl BUF_JUKE_BOX_HERO
	dl BUF_RHIANNON
	dl BUF_TAKE_A_RIDE
	dl BUF_WILD_FLOWER
	dl BUF_WONT_GET_FOOLED_AGAIN

; SFX duration lookup:
SFX_duration_lut:
	dl 288749 ; AFRICA
	dl 204924 ; ANYTIME
	dl 257116 ; BARRACUDA
	dl 250840 ; COME_UNDONE
	dl 246579 ; EVERY_BREATH_YOU_TAKE
	dl 253486 ; JUKE_BOX_HERO
	dl 246649 ; RHIANNON
	dl 280273 ; TAKE_A_RIDE
	dl 213939 ; WILD_FLOWER
	dl 501869 ; WONT_GET_FOOLED_AGAIN

; SFX load routines jump table:
SFX_load_routines_table:
	dl load_sfx_AFRICA
	dl load_sfx_ANYTIME
	dl load_sfx_BARRACUDA
	dl load_sfx_COME_UNDONE
	dl load_sfx_EVERY_BREATH_YOU_TAKE
	dl load_sfx_JUKE_BOX_HERO
	dl load_sfx_RHIANNON
	dl load_sfx_TAKE_A_RIDE
	dl load_sfx_WILD_FLOWER
	dl load_sfx_WONT_GET_FOOLED_AGAIN

; Import sfx .raw files and load them into VDP buffers

load_sfx_AFRICA:
	ld hl,BUF_AFRICA
	ld de,16384
	ld iy,FAFRICA
	call vdu_load_sfx
	ret

load_sfx_ANYTIME:
	ld hl,BUF_ANYTIME
	ld de,16384
	ld iy,FANYTIME
	call vdu_load_sfx
	ret

load_sfx_BARRACUDA:
	ld hl,BUF_BARRACUDA
	ld de,16384
	ld iy,FBARRACUDA
	call vdu_load_sfx
	ret

load_sfx_COME_UNDONE:
	ld hl,BUF_COME_UNDONE
	ld de,16384
	ld iy,FCOME_UNDONE
	call vdu_load_sfx
	ret

load_sfx_EVERY_BREATH_YOU_TAKE:
	ld hl,BUF_EVERY_BREATH_YOU_TAKE
	ld de,16384
	ld iy,FEVERY_BREATH_YOU_TAKE
	call vdu_load_sfx
	ret

load_sfx_JUKE_BOX_HERO:
	ld hl,BUF_JUKE_BOX_HERO
	ld de,16384
	ld iy,FJUKE_BOX_HERO
	call vdu_load_sfx
	ret

load_sfx_RHIANNON:
	ld hl,BUF_RHIANNON
	ld de,16384
	ld iy,FRHIANNON
	call vdu_load_sfx
	ret

load_sfx_TAKE_A_RIDE:
	ld hl,BUF_TAKE_A_RIDE
	ld de,16384
	ld iy,FTAKE_A_RIDE
	call vdu_load_sfx
	ret

load_sfx_WILD_FLOWER:
	ld hl,BUF_WILD_FLOWER
	ld de,16384
	ld iy,FWILD_FLOWER
	call vdu_load_sfx
	ret

load_sfx_WONT_GET_FOOLED_AGAIN:
	ld hl,BUF_WONT_GET_FOOLED_AGAIN
	ld de,16384
	ld iy,FWONT_GET_FOOLED_AGAIN
	call vdu_load_sfx
	ret

; File name lookup index:
SFX_filename_index:
	dl FAFRICA
	dl FANYTIME
	dl FBARRACUDA
	dl FCOME_UNDONE
	dl FEVERY_BREATH_YOU_TAKE
	dl FJUKE_BOX_HERO
	dl FRHIANNON
	dl FTAKE_A_RIDE
	dl FWILD_FLOWER
	dl FWONT_GET_FOOLED_AGAIN

; File name lookups:
FAFRICA: db "music/AFRICA.raw",0
FANYTIME: db "music/ANYTIME.raw",0
FBARRACUDA: db "music/BARRACUDA.raw",0
FCOME_UNDONE: db "music/COME_UNDONE.raw",0
FEVERY_BREATH_YOU_TAKE: db "music/EVERY_BREATH_YOU_TAKE.raw",0
FJUKE_BOX_HERO: db "music/JUKE_BOX_HERO.raw",0
FRHIANNON: db "music/RHIANNON.raw",0
FTAKE_A_RIDE: db "music/TAKE_A_RIDE.raw",0
FWILD_FLOWER: db "music/WILD_FLOWER.raw",0
FWONT_GET_FOOLED_AGAIN: db "music/WONT_GET_FOOLED_AGAIN.raw",0

; Play sfx routines

sfx_play_AFRICA:
	ld hl,BUF_AFRICA
	ld bc,0
	jp vdu_play_sfx

sfx_play_ANYTIME:
	ld hl,BUF_ANYTIME
	ld bc,0
	jp vdu_play_sfx

sfx_play_BARRACUDA:
	ld hl,BUF_BARRACUDA
	ld bc,0
	jp vdu_play_sfx

sfx_play_COME_UNDONE:
	ld hl,BUF_COME_UNDONE
	ld bc,0
	jp vdu_play_sfx

sfx_play_EVERY_BREATH_YOU_TAKE:
	ld hl,BUF_EVERY_BREATH_YOU_TAKE
	ld bc,0
	jp vdu_play_sfx

sfx_play_JUKE_BOX_HERO:
	ld hl,BUF_JUKE_BOX_HERO
	ld bc,0
	jp vdu_play_sfx

sfx_play_RHIANNON:
	ld hl,BUF_RHIANNON
	ld bc,0
	jp vdu_play_sfx

sfx_play_TAKE_A_RIDE:
	ld hl,BUF_TAKE_A_RIDE
	ld bc,0
	jp vdu_play_sfx

sfx_play_WILD_FLOWER:
	ld hl,BUF_WILD_FLOWER
	ld bc,0
	jp vdu_play_sfx

sfx_play_WONT_GET_FOOLED_AGAIN:
	ld hl,BUF_WONT_GET_FOOLED_AGAIN
	ld bc,0
	jp vdu_play_sfx
