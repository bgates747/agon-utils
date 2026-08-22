; Emulator proof for address-preserving Space Invaders hardware adapters.
;
; The exact original ROM is installed at 0000-1fff. Every executable IN/OUT
; opcode is changed in place to RST 0 followed by a descriptor byte. RST 0
; exchanges the stacked return address past that descriptor and dispatches to
; high-memory emulation without relocating any later original instruction.

	.assume adl=0
	.section .boot, "ax", @progbits
	.global __image_start
	.global __mos_header
	.global __start
	.global __image_end

	.equ TRAP_OPCODE, 0xc7
	.equ JP_OPCODE, 0xc3
	.equ OUTPUT_BIT, 0x80
	.equ COMPLETION_DESCRIPTOR, 0x7f

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

	ld hl, __original_rom
	ld de, 0
	ld bc, __original_rom_end - __original_rom
	ldir

	; Patch each two-byte I/O instruction to RST 0 plus a typed port byte.
	ld ix, io_patch_table
	ld b, IO_PATCH_COUNT
patch_io_loop:
	ld l, (ix+0)
	ld h, (ix+1)
	ld (hl), TRAP_OPCODE
	inc hl
	ld a, (ix+2)
	ld (hl), a
	inc ix
	inc ix
	inc ix
	djnz patch_io_loop

	; Original EI instructions cannot claim Agon interrupt dispatch. Keep this
	; proof polled and deterministic until the scheduler owns phase entry.
	ld ix, ei_patch_table
	ld b, EI_PATCH_COUNT
patch_ei_loop:
	ld l, (ix+0)
	ld h, (ix+1)
	ld (hl), 0xf3
	inc ix
	inc ix
	djnz patch_ei_loop

	; Stop after the original initialization, first sound writes, and entry to
	; the splash main loop. This replaces CALL OneSecDelay at 0af3.
	ld a, TRAP_OPCODE
	ld (0x0af3), a
	ld a, COMPLETION_DESCRIPTOR
	ld (0x0af4), a
	xor a
	ld (0x0af5), a

	; RST 0 is disposable after reset. Redirect it to the high adapter.
	ld a, JP_OPCODE
	ld (0x0000), a
	ld hl, __io_trap
	ld a, l
	ld (0x0001), a
	ld a, h
	ld (0x0002), a

	; The original init establishes SP=2400 and never returns.
	jp 0x18d4

pass_message:
	.asciz "Space Invaders adapter/init proof: PASS\r\n"
fail_message:
	.asciz "Space Invaders adapter/init proof: FAIL\r\n"
fail_status_message:
	.asciz "Space Invaders adapter/init proof: FAIL status VRAM\r\n"
fail_shift_count_message:
	.asciz "Space Invaders adapter/init proof: FAIL shift traps\r\n"
fail_shift_value_message:
	.asciz "Space Invaders adapter/init proof: FAIL shift value\r\n"
fail_sound_message:
	.asciz "Space Invaders adapter/init proof: FAIL sound latch\r\n"

__image_end:

	.section .platform, "ax", @progbits
	.global __io_trap
	.global __platform_end

; Entry preserves the complete original AF/BC/DE/HL contract. EXX and EX AF
; make scratch banks available; the return address is advanced over the typed
; descriptor before any adapter work.
__io_trap:
	ex af, af'
	exx
	pop hl
	ld c, (hl)
	inc hl
	push hl
	bit 7, c
	jr nz, io_output

	ld a, c
	cp COMPLETION_DESCRIPTOR
	jp z, proof_reached_main_loop
	cp 0x01
	jr z, input_port_1
	cp 0x02
	jr z, input_port_2
	cp 0x03
	jr z, input_shift_register
	xor a
	jr input_complete

input_port_1:
	ld a, (adapter_input_1)
	jr input_complete

input_port_2:
	ld a, (adapter_input_2)
	jr input_complete

input_shift_register:
	ld hl, (adapter_shift_register)
	ld a, (adapter_shift_amount)
	and 0x07
	ld c, a
	ld a, 0x08
	sub c
	ld b, a
1:
	srl h
	rr l
	djnz 1b
	ld a, l
	ld hl, adapter_shift_reads
	inc (hl)

input_complete:
	; Save the new A, restore original AF and general registers, then copy the
	; new A over the restored accumulator without changing original flags.
	push af
	exx
	ex af, af'
	exx
	pop bc
	ld a, b
	exx
	ret

io_output:
	; Recover and save original AF before dispatch changes flags. B is scratch
	; and holds the original output accumulator throughout the adapter.
	ex af, af'
	push af
	ld b, a
	ld a, c
	and 0x7f
	cp 0x02
	jr z, output_shift_amount
	cp 0x03
	jr z, output_sound_1
	cp 0x04
	jr z, output_shift_data
	cp 0x05
	jr z, output_sound_2
	cp 0x06
	jr z, output_watchdog
	jr output_complete

output_shift_amount:
	ld a, b
	and 0x07
	ld (adapter_shift_amount), a
	jr output_complete

output_shift_data:
	ld a, (adapter_shift_register+1)
	ld (adapter_shift_register), a
	ld a, b
	ld (adapter_shift_register+1), a
	ld hl, adapter_shift_writes
	inc (hl)
	jr output_complete

output_sound_1:
	ld a, b
	ld (adapter_sound_1), a
	jr output_complete

output_sound_2:
	ld a, b
	ld (adapter_sound_2), a
	jr output_complete

output_watchdog:
	ld hl, adapter_watchdog_writes
	inc (hl)

output_complete:
	pop af
	exx
	ret

proof_reached_main_loop:
	; Restore the original register banks and discard the completion trap's
	; adjusted return address. Completion is terminal; it will not be resumed.
	exx
	ex af, af'
	pop hl

	ld a, (adapter_sound_1)
	or a
	jr nz, proof_failed_sound
	ld a, (adapter_sound_2)
	or a
	jr nz, proof_failed_sound

	; The original status renderer must have produced at least one set pixel in
	; its authoritative packed framebuffer before the explicit shifter test.
	ld hl, 0x2400
	ld bc, 0x1c00
	xor a
2:
	or (hl)
	inc hl
	dec bc
	ld d, a
	ld a, b
	or c
	ld a, d
	jr nz, 2b
	or a
	jr z, proof_failed_status

	; Byte-aligned status characters need not use the external shifter. Invoke
	; original DrawSprite deliberately at bit offset 3 with one 0x81 row.
	xor a
	ld (adapter_shift_amount), a
	ld (adapter_shift_register), a
	ld (adapter_shift_register+1), a
	ld (adapter_shift_writes), a
	ld (adapter_shift_reads), a
	ld (0x2400), a
	ld (0x2401), a
	ld hl, 0x2003
	ld de, adapter_test_sprite
	ld b, 0x01
	call 0x15d3

	ld a, (adapter_shift_writes)
	cp 0x02
	jr nz, proof_failed_shift_count
	ld a, (adapter_shift_reads)
	cp 0x02
	jr nz, proof_failed_shift_count
	ld a, (0x2400)
	cp 0x08
	jr nz, proof_failed_shift_value
	ld a, (0x2401)
	cp 0x04
	jr nz, proof_failed_shift_value

	ld hl, pass_message
	jr print_terminal_result

proof_failed_status:
	ld hl, fail_status_message
	jr print_terminal_result

proof_failed_shift_count:
	ld hl, fail_shift_count_message
	jr print_terminal_result

proof_failed_shift_value:
	ld hl, fail_shift_value_message
	jr print_terminal_result

proof_failed_sound:
	ld hl, fail_sound_message

print_terminal_result:
	ld bc, 0
	xor a
	rst.lis 0x18
	di
3:
	jr 3b

; Input defaults: no controls/coin asserted. DIP port bit 3 selects three
; ships; other DIP and cabinet bits remain clear for the inert proof.
adapter_input_1:
	.byte 0x00
adapter_input_2:
	.byte 0x08
adapter_shift_amount:
	.byte 0x00
adapter_shift_register:
	.word 0x0000
adapter_sound_1:
	.byte 0x00
adapter_sound_2:
	.byte 0x00
adapter_watchdog_writes:
	.byte 0x00
adapter_shift_writes:
	.byte 0x00
adapter_shift_reads:
	.byte 0x00
adapter_test_sprite:
	.byte 0x81

__platform_end:

	.section .loader, "ax", @progbits

	.macro IO_PATCH address, descriptor
	.word \address
	.byte \descriptor
	.endm

io_patch_table:
	; Typed Intel IN instructions.
	IO_PATCH 0x0020, 0x01
	IO_PATCH 0x0791, 0x01
	IO_PATCH 0x085f, 0x01
	IO_PATCH 0x08d1, 0x02
	IO_PATCH 0x093f, 0x02
	IO_PATCH 0x0bb7, 0x02
	IO_PATCH 0x140a, 0x03
	IO_PATCH 0x1413, 0x03
	IO_PATCH 0x145a, 0x03
	IO_PATCH 0x1464, 0x03
	IO_PATCH 0x149d, 0x03
	IO_PATCH 0x14b1, 0x03
	IO_PATCH 0x15dc, 0x03
	IO_PATCH 0x15e4, 0x03
	IO_PATCH 0x17c7, 0x01
	IO_PATCH 0x17ca, 0x02
	IO_PATCH 0x17cd, 0x02
	IO_PATCH 0x19a1, 0x01
	IO_PATCH 0x19ac, 0x01

	; Typed Intel OUT instructions (descriptor bit 7 set).
	IO_PATCH 0x031d, OUTPUT_BIT | 0x05
	IO_PATCH 0x06f4, OUTPUT_BIT | 0x05
	IO_PATCH 0x084c, OUTPUT_BIT | 0x06
	IO_PATCH 0x090e, OUTPUT_BIT | 0x06
	IO_PATCH 0x0a85, OUTPUT_BIT | 0x06
	IO_PATCH 0x0aeb, OUTPUT_BIT | 0x03
	IO_PATCH 0x0aed, OUTPUT_BIT | 0x05
	IO_PATCH 0x0b77, OUTPUT_BIT | 0x06
	IO_PATCH 0x1408, OUTPUT_BIT | 0x04
	IO_PATCH 0x1411, OUTPUT_BIT | 0x04
	IO_PATCH 0x1458, OUTPUT_BIT | 0x04
	IO_PATCH 0x1462, OUTPUT_BIT | 0x04
	IO_PATCH 0x1477, OUTPUT_BIT | 0x02
	IO_PATCH 0x149b, OUTPUT_BIT | 0x04
	IO_PATCH 0x14af, OUTPUT_BIT | 0x04
	IO_PATCH 0x15da, OUTPUT_BIT | 0x04
	IO_PATCH 0x15e2, OUTPUT_BIT | 0x04
	IO_PATCH 0x16de, OUTPUT_BIT | 0x05
	IO_PATCH 0x1757, OUTPUT_BIT | 0x05
	IO_PATCH 0x1772, OUTPUT_BIT | 0x05
	IO_PATCH 0x17bc, OUTPUT_BIT | 0x05
	IO_PATCH 0x1901, OUTPUT_BIT | 0x03
	IO_PATCH 0x19e3, OUTPUT_BIT | 0x03
io_patch_table_end:
	.equ IO_PATCH_COUNT, (io_patch_table_end - io_patch_table) / 3

ei_patch_table:
	.word 0x0086, 0x076d, 0x0af2, 0x16e9, 0x17eb
ei_patch_table_end:
	.equ EI_PATCH_COUNT, (ei_patch_table_end - ei_patch_table) / 2

	.section .original_rom, "a", @progbits
	.global __original_rom
	.global __original_rom_end
__original_rom:
	.incbin "build/reference/invaders.rom"
__original_rom_end:
