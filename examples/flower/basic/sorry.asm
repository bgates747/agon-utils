;
; Title:	BBC Basic Interpreter - Z80 version
;		Catch-all for unimplemented functionality
; Author:	Dean Belfield
; Created:	12/05/2023
; Last Updated:	12/05/2023
;
; Modinfo:

			.ASSUME	ADL = 1

			INCLUDE "mos_api.inc"
			INCLUDE "macros.inc"
			INCLUDE "ram.asm"
			INCLUDE	"equs.inc"

			; SEGMENT CODE
			
			; XDEF	ENVEL
			; XDEF	ADVAL
			; XDEF	PUTIMS
			
			; XREF	EXTERR
			
ENVEL:
ADVAL:
PUTIMS:
			XOR     A
			CALL    EXTERR
			DEFB    "Sorry"
			DEFB    0

; ===== STUB FUNCTIONS =====
printInline:
    ret

EXTERR:
	call printInline
	asciz "sorry.asm called EXTERR!"
	ret