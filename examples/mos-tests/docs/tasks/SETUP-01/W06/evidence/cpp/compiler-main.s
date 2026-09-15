	.section	.text,"ax",@progbits
	.assume	ADL = 1
	.file	"main.cpp"
	.globl	_main
	.type	_main,@function
_main:
	ld	hl, -40
	call	__frameset
	ld	hl, ___const.main.message
	ld	bc, 34
	ld	de, 1
	ld	(ix - 37), de
	ld	a, 87
	lea	de, ix - 34
	ld	(ix - 40), de
	ldir
	ld	c, a
	.local	.LBB0_1
.LBB0_1:
	ld	a, c
	or	a, a
	jr	z, .LBB0_3
	or	a, a
	sbc	hl, hl
	ld	l, c
	push	hl
	call	_putch
	pop	hl
	ld	hl, (ix - 40)
	ld	de, (ix - 37)
	add	hl, de
	ld	c, (hl)
	inc	de
	ld	(ix - 37), de
	jr	.LBB0_1
	.local	.LBB0_3
.LBB0_3:
	ld	hl, 1193046
	ld	sp, ix
	pop	ix
	ret
	.local	.Lfunc_end0
.Lfunc_end0:
	.size	_main, .Lfunc_end0-_main

	.section	.rodata,"a",@progbits
	.local	___const.main.message
___const.main.message:
	db	"W04: MOS ABI 0123456789 AaZz !?", 13, 10, 0

	.ident	"clang version 15.0.7 (https://github.com/AgonPlatform/agon-llvm-project.git c76386c0083e6a6236ff774275227e2389f85538)"
	.extern	__Unwind_SjLj_Register
	.extern	__frameset
	.extern	__Unwind_SjLj_Unregister
	.extern	_putch
