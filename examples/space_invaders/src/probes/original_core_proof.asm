; Emulator proof for the unmodified Space Invaders 8080 program image.
;
; The MOSlet starts its loader above 0x8000, copies the exact ASMX reference
; ROM over the disposable launch header at 0x0000, and calls an ADL=0 test
; trampoline at 0x4000. The trampoline invokes only original routines that do
; not touch hardware I/O. All original absolute ROM and RAM addresses retain
; their 0000-3fff meanings without changing MBASE or entering mixed mode.

	.assume adl=0
	.section .boot, "ax", @progbits
	.global __image_start
	.global __mos_header
	.global __start
	.global __image_end

__image_start:
	jp __start
	.byte 0
	.space 0x3c, 0

__mos_header:
	.ascii "MOS"
	.byte 0
	.byte 0

	.section .loader, "ax", @progbits
__start:
	di
	ld sp, 0xfffe

	; The source is above the original 0000-3fff machine image, so an ordinary
	; ADL=0 LDIR can install the reference without touching this loader.
	ld hl, __original_rom
	ld de, 0
	ld bc, __original_rom_end - __original_rom
	ldir

	call __core_test_start

	ld a, h
	or l
	jr nz, proof_failed
	ld hl, pass_message
	jr print_result

proof_failed:
	ld hl, fail_message

print_result:
	ld bc, 0
	xor a
	rst.lis 0x18
	di

	; SPS was deliberately replaced for the original ADL=0 call tree, so no
	; MOS return frame exists at this point. Keep the diagnostic stable until
	; the emulator is closed instead of returning through arbitrary memory.
	; Interrupts must remain disabled because low memory now contains the
	; original arcade vectors rather than the MOSlet's interrupt veneers.
proof_complete:
	jr proof_complete

pass_message:
	.asciz "Space Invaders original-core proof: PASS\r\n"
fail_message:
	.asciz "Space Invaders original-core proof: FAIL\r\n"

__image_end:

; This section executes at logical address 0x4000 in the MOSlet's ADL=0 bank.
	.section .core_test, "ax", @progbits
	.global __core_test_start
	.global __core_test_end

__core_test_start:
	; Test 1: original InitAliens (01c0) writes exactly 55 live flags.
	ld hl, 0x2100
	ld b, 0x38
	xor a
1:
	ld (hl), a
	inc hl
	djnz 1b
	ld a, 0x5a
	ld (0x2137), a
	call 0x01c0
	ld hl, 0x2100
	ld b, 0x37
2:
	ld a, (hl)
	cp 0x01
	jp nz, fail_test_1
	inc hl
	djnz 2b
	ld a, (0x2137)
	cp 0x5a
	jp nz, fail_test_1

	; Test 2: original AddDelta (01d9) performs wrapping 8-bit updates.
	ld a, 0x05
	ld (0x2300), a
	ld a, 0xfe
	ld (0x2301), a
	ld a, 0xfa
	ld (0x2302), a
	ld a, 0x01
	ld (0x2303), a
	ld c, 0x05
	ld hl, 0x2300
	call 0x01d9
	ld a, (0x2302)
	cp 0xff
	jp nz, fail_test_2
	ld a, (0x2303)
	cp 0xff
	jp nz, fail_test_2

	; Test 3: original GetAlienStatPtr (1581) computes row*11+column-1.
	ld a, 0x22
	ld (0x2067), a
	ld b, 0x04
	ld c, 0x0b
	call 0x1581
	ld a, h
	cp 0x22
	jp nz, fail_test_3
	ld a, l
	cp 0x36
	jp nz, fail_test_3

	; Test 4: original CountAliens (15f3) counts sparse live flags.
	ld a, 0x21
	ld (0x2067), a
	ld hl, 0x2100
	ld b, 0x37
	xor a
3:
	ld (hl), a
	inc hl
	djnz 3b
	inc a
	ld (0x2100), a
	ld (0x211b), a
	ld (0x2136), a
	xor a
	ld (0x206b), a
	call 0x15f3
	cp 0x03
	jp nz, fail_test_4
	ld a, (0x2082)
	cp 0x03
	jp nz, fail_test_4
	ld a, (0x206b)
	or a
	jp nz, fail_test_4

	; Test 5: the one-alien branch sets the original 206b flag.
	ld hl, 0x2100
	ld b, 0x37
	xor a
4:
	ld (hl), a
	inc hl
	djnz 4b
	inc a
	ld (0x212a), a
	xor a
	ld (0x206b), a
	call 0x15f3
	cp 0x01
	jp nz, fail_test_5
	ld a, (0x2082)
	cp 0x01
	jp nz, fail_test_5
	ld a, (0x206b)
	cp 0x01
	jp nz, fail_test_5

	ld hl, 0
	ret

fail_test_1:
	ld hl, 1
	ret
fail_test_2:
	ld hl, 2
	ret
fail_test_3:
	ld hl, 3
	ret
fail_test_4:
	ld hl, 4
	ret
fail_test_5:
	ld hl, 5
	ret

__core_test_end:

	.section .original_rom, "a", @progbits
	.global __original_rom
	.global __original_rom_end
__original_rom:
	.incbin "build/reference/invaders.rom"
__original_rom_end:
