; This file is created by build_98_asm_sfx.py, do not edit it!

SFX_num_buffers: equ 9
; SFX buffer ids:
BUF_AFRICA: equ 0x3000
BUF_ANYTIME: equ 0x3001
BUF_BARRACUDA: equ 0x3002
BUF_COME_UNDONE: equ 0x3003
BUF_EVERY_BREATH_YOU_TAKE: equ 0x3004
BUF_RHIANNON: equ 0x3005
BUF_TAKE_A_RIDE: equ 0x3006
BUF_AMBIENT_BEAT70: equ 0x3007
BUF_SPACE_ADVENTURE: equ 0x3008

; SFX buffer id reverse lookup:
SFX_buffer_id_lut:
	dl BUF_AFRICA
	dl BUF_ANYTIME
	dl BUF_BARRACUDA
	dl BUF_COME_UNDONE
	dl BUF_EVERY_BREATH_YOU_TAKE
	dl BUF_RHIANNON
	dl BUF_TAKE_A_RIDE
	dl BUF_AMBIENT_BEAT70
	dl BUF_SPACE_ADVENTURE

; SFX duration lookup:
SFX_duration_lut:
	dl 29268 ; AFRICA
	dl 29268 ; ANYTIME
	dl 29268 ; BARRACUDA
	dl 29268 ; COME_UNDONE
	dl 29268 ; EVERY_BREATH_YOU_TAKE
	dl 29268 ; RHIANNON
	dl 29268 ; TAKE_A_RIDE
	dl 29268 ; AMBIENT_BEAT70
	dl 29304 ; SPACE_ADVENTURE

; SFX load routines jump table:
SFX_load_routines_table:
	dl load_sfx_AFRICA
	dl load_sfx_ANYTIME
	dl load_sfx_BARRACUDA
	dl load_sfx_COME_UNDONE
	dl load_sfx_EVERY_BREATH_YOU_TAKE
	dl load_sfx_RHIANNON
	dl load_sfx_TAKE_A_RIDE
	dl load_sfx_AMBIENT_BEAT70
	dl load_sfx_SPACE_ADVENTURE

; Import sfx .raw files and load them into VDP buffers

load_sfx_AFRICA:
	ld hl,FAFRICA
	ld de,filedata
	ld bc,65536
	ld a,mos_load
	RST.LIL 08h
	ld hl,BUF_AFRICA
	ld de,15360
	ld iy,FAFRICA
	call vdu_load_sfx
	ret

load_sfx_ANYTIME:
	ld hl,FANYTIME
	ld de,filedata
	ld bc,65536
	ld a,mos_load
	RST.LIL 08h
	ld hl,BUF_ANYTIME
	ld de,15360
	ld iy,FANYTIME
	call vdu_load_sfx
	ret

load_sfx_BARRACUDA:
	ld hl,FBARRACUDA
	ld de,filedata
	ld bc,65536
	ld a,mos_load
	RST.LIL 08h
	ld hl,BUF_BARRACUDA
	ld de,15360
	ld iy,FBARRACUDA
	call vdu_load_sfx
	ret

load_sfx_COME_UNDONE:
	ld hl,FCOME_UNDONE
	ld de,filedata
	ld bc,65536
	ld a,mos_load
	RST.LIL 08h
	ld hl,BUF_COME_UNDONE
	ld de,15360
	ld iy,FCOME_UNDONE
	call vdu_load_sfx
	ret

load_sfx_EVERY_BREATH_YOU_TAKE:
	ld hl,FEVERY_BREATH_YOU_TAKE
	ld de,filedata
	ld bc,65536
	ld a,mos_load
	RST.LIL 08h
	ld hl,BUF_EVERY_BREATH_YOU_TAKE
	ld de,15360
	ld iy,FEVERY_BREATH_YOU_TAKE
	call vdu_load_sfx
	ret

load_sfx_RHIANNON:
	ld hl,FRHIANNON
	ld de,filedata
	ld bc,65536
	ld a,mos_load
	RST.LIL 08h
	ld hl,BUF_RHIANNON
	ld de,15360
	ld iy,FRHIANNON
	call vdu_load_sfx
	ret

load_sfx_TAKE_A_RIDE:
	ld hl,FTAKE_A_RIDE
	ld de,filedata
	ld bc,65536
	ld a,mos_load
	RST.LIL 08h
	ld hl,BUF_TAKE_A_RIDE
	ld de,15360
	ld iy,FTAKE_A_RIDE
	call vdu_load_sfx
	ret

load_sfx_AMBIENT_BEAT70:
	ld hl,FAMBIENT_BEAT70
	ld de,filedata
	ld bc,65536
	ld a,mos_load
	RST.LIL 08h
	ld hl,BUF_AMBIENT_BEAT70
	ld de,15360
	ld iy,FAMBIENT_BEAT70
	call vdu_load_sfx
	ret

load_sfx_SPACE_ADVENTURE:
	ld hl,FSPACE_ADVENTURE
	ld de,filedata
	ld bc,65536
	ld a,mos_load
	RST.LIL 08h
	ld hl,BUF_SPACE_ADVENTURE
	ld de,15360
	ld iy,FSPACE_ADVENTURE
	call vdu_load_sfx
	ret

; File name lookups:
FAFRICA: db "music/AFRICA.raw",0
FANYTIME: db "music/ANYTIME.raw",0
FBARRACUDA: db "music/BARRACUDA.raw",0
FCOME_UNDONE: db "music/COME_UNDONE.raw",0
FEVERY_BREATH_YOU_TAKE: db "music/EVERY_BREATH_YOU_TAKE.raw",0
FRHIANNON: db "music/RHIANNON.raw",0
FTAKE_A_RIDE: db "music/TAKE_A_RIDE.raw",0
FAMBIENT_BEAT70: db "music/AMBIENT_BEAT70.raw",0
FSPACE_ADVENTURE: db "music/SPACE_ADVENTURE.raw",0

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

sfx_play_RHIANNON:
	ld hl,BUF_RHIANNON
	ld bc,0
	jp vdu_play_sfx

sfx_play_TAKE_A_RIDE:
	ld hl,BUF_TAKE_A_RIDE
	ld bc,0
	jp vdu_play_sfx

sfx_play_AMBIENT_BEAT70:
	ld hl,BUF_AMBIENT_BEAT70
	ld bc,0
	jp vdu_play_sfx

sfx_play_SPACE_ADVENTURE:
	ld hl,BUF_SPACE_ADVENTURE
	ld bc,0
	jp vdu_play_sfx
