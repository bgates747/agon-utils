; Minimal agondev/MOS execution probe for the Space Invaders port.
;
; This file deliberately contains no game code. It proves the ADL=0 image
; boundary before PORT-001 translates the preserved Intel 8080 source.

	.assume adl=0
	.section .init, "ax", @progbits
	.global __image_start
	.global __mos_header
	.global __start
	.global __image_end

__image_start:
	jp __start
	.byte 0                 ; ADL=0 JP is three bytes; name starts at offset 4.
	.space 0x3c, 0          ; agondev-setname writes offsets 0x04-0x3f.

__mos_header:
	.ascii "MOS"
	.byte 0                 ; MOS executable-header version.
	.byte 0                 ; Z80-compatible execution mode (ADL=0).

__start:
	ld sp, 0xfffe           ; MOS leaves SPS undefined on ADL=0 entry.
	ld hl, 0                ; Return success to MOS.
	ret.lis                 ; Return from ADL=0 code to the ADL-mode caller.

__image_end:
