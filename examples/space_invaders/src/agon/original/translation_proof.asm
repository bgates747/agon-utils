; Address-bounded Intel 8080 -> GNU Z80 syntax translation proof.
;
; These routines are transcribed from src/invaders.asm without behavioral
; changes. Their addresses and complete emitted byte ranges are compared with
; the independent ASMX reference ROM by make translation-proof.

	.assume adl=0
	.section .text, "ax", @progbits

	.equ GetAlRefPtr, 0x0886
	.equ WrapRef, 0x1590

	.org 0x00b1, 0
	.global translated_InitRack
translated_InitRack:
	call GetAlRefPtr
	push hl
	ld a, (hl)
	inc hl
	ld h, (hl)
	ld l, a
	ld (0x2009), hl
	ld (0x200b), hl
	pop hl
	dec hl
	ld a, (hl)
	cp 0x03
	jp nz, translated_L_00c8
	dec a
translated_L_00c8:
	ld (0x2008), a
	cp 0xfe
	ld a, 0x00
	jp nz, translated_L_00d3
	inc a
translated_L_00d3:
	ld (0x200d), a
	ret

	.org 0x01c0, 0
	.global translated_InitAliens
translated_InitAliens:
	ld hl, 0x2100
translated_L_01c3:
	ld b, 0x37
translated_L_01c5:
	ld (hl), 0x01
	inc hl
	dec b
	jp nz, translated_L_01c5
	ret

	.org 0x01d9, 0
	.global translated_AddDelta
translated_AddDelta:
	inc hl
	ld b, (hl)
	inc hl
	ld a, c
	add a, (hl)
	ld (hl), a
	inc hl
	ld a, b
	add a, (hl)
	ld (hl), a
	ret

	.org 0x1554, 0
	.global translated_Cnt16s
translated_Cnt16s:
	ld c, 0x00
	cp h
	call nc, WrapRef
translated_L_155a:
	cp h
	ret nc
	add a, 0x10
	inc c
	jp translated_L_155a

	.org 0x1581, 0
	.global translated_GetAlienStatPtr
translated_GetAlienStatPtr:
	ld a, b
	rlca
	rlca
	rlca
	add a, b
	add a, b
	add a, b
	add a, c
	dec a
	ld l, a
	ld a, (0x2067)
	ld h, a
	ret

	.org 0x1a32, 0
	.global translated_BlockCopy
translated_BlockCopy:
	ld a, (de)
	ld (hl), a
	inc hl
	inc de
	dec b
	jp nz, translated_BlockCopy
	ret

	.org 0x1a47, 0
	.global translated_ConvToScr
translated_ConvToScr:
	push bc
	ld b, 0x03
translated_L_1a4a:
	ld a, h
	rra
	ld h, a
	ld a, l
	rra
	ld l, a
	dec b
	jp nz, translated_L_1a4a
	ld a, h
	and 0x3f
	or 0x20
	ld h, a
	pop bc
	ret
