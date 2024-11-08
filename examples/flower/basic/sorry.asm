;
; Title:	BBC Basic Interpreter - Z80 version
;		Catch-all for unimplemented functionality
; Author:	Dean Belfield
; Created:	12/05/2023
; Last Updated:	12/05/2023
;
; Modinfo:

			.ASSUME	ADL = 1

			; SEGMENT CODE
			
			; XDEF	ENVEL
			; XDEF	ADVAL
			; XDEF	PUTIMS
			
			; XREF	EXTERR
			
ENVEL:
ADVAL:
PUTIMS: 	ret ; hopefully we won't be needing this
			; XOR     A
			; CALL    EXTERR
			; DEFB    "Sorry"
			; DEFB    0
