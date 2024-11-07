;
; Title:	BBC Basic Interpreter - Z80 version
;		Statement Execution & Assembler Module - "EXEC"
; Author:	(C) Copyright  R.T.Russell  1984
; Modified By:	Dean Belfield
; Created:	12/05/2023
; Last Updated:	26/06/2023
;
; Modinfo:
; 27/01/1984:	Version 2.1
; 02/03/1987:	Version 3.0
; 11/06/1987:	Version 3.1
; 12/05/2023:	Modified by Dean Belfield
; 07/06/2023:	Modified to run in ADL mode
; 26/06/2023:	Fixed DIM, USR, and address output of inline assembler

			.ASSUME	ADL = 1

; Check whether the stack is full
;
CHECK:			PUSH    HL
			PUSH	BC
			LD      HL,(FREE)		; HL: Address of first free space byte
			LD	BC,100h			; BC: One page of memory
			ADD	HL,BC			; Add a page to FREE
			SBC     HL,SP			; And subtract the current SP
			POP	BC
			POP     HL
			RET     C			; The SP is not in the same page, so just return
			XOR     A			; Otherwise
			JP      ERROR_			; Throw error "No room"
;
STORS3:			LD	BC,0
			LD      C,E			; BC: String length
			PUSH    IX
			POP     DE			; DE: Destination
			XOR     A			; Check if string length is 0
			CP      C
			JR      Z,STORS5		; Yes, so don't copy
			LDIR
STORS5:			LD      A,CR			; Finally add the terminator
			LD      (DE),A
			RET


; Multiply by 4 or 5
; This function is used to allocate space for dimensioned variables
; This is a 24-bit operation
; - DE: Number to multiple
; -  A: 04h (Integer) - takes up 4 bytes
;       05h (Float)   - takes up 5 bytes
;       81h (String)  - takes up 5 bytes - this is different from BBC BASIC for Z80 where strings only take up 4 bytes
; Returns:
; - DE: Multiplied by 4 if A = 4, otherwise multiplies by 5
; -  F: Carry if overflow
; Corrupts:
; - HL
X4OR5:			CP      4			; Check A = 4 (Z flag is used later)
			; LD	HL,DE  ; HOW!?
			push de
			pop hl
			ADD     HL,HL			; Multiply by 2 (note this operation preserves the zero flag)
			RET     C			; Exit if overflow
			ADD     HL,HL			; Multiply by 2 again
			RET     C			; Exit if overflow
			EX      DE,HL			; DE: Product
			RET     Z			; Exit if A = 4
			ADD     HL,DE			; Add original value to HL (effectively multiplying by 5)
			EX      DE,HL			; DE: Product
			RET

; 16-bit unsigned multiply
; - HL: Operand 1
; - BC: Operand 2
; Returns:
; - HL: Result
; -  F: C if overflow
;
MUL16:			PUSH	BC
			LD	D, C			; Set up the registers for the multiplies
			LD	E, L		
			LD	L, C
			LD	C, E
			MLT	HL			; HL = H * C (*256)
			MLT	DE			; DE = L * C
			MLT	BC			; BC = B * L (*256)
			ADD	HL, BC			; HL = The sum of the two most significant multiplications
			POP	BC
			XOR	A
			SBC	H			; If H is not zero then it's an overflow
			RET	C
			LD	H, L			; HL = ((H * C) + (B * L) * 256) + (L * C)
			LD	L, A
			ADD	HL, DE
			RET
;
CHANEL:			CALL    NXT			; Skip whitespace
			CP      '#'			; Check for the '#' symbol
			LD      A,45	
			JP      NZ,ERROR_        	; If it is missing, then throw a "Missing #" error
CHNL:			INC     IY             		; Bump past the '#'
			CALL    ITEMI			; Get the channel number
			EXX
			EX      DE,HL			; DE: The channel number
			RET


XEQ:			LD      (ERRLIN),IY     	; Error pointer
			CALL    TRAP           		; Check keyboard
XEQ1:			CALL    NXT
			INC     IY
			CP      ':'             	; Seperator
			JR      Z,XEQ1
			CP      CR
			JR      Z,XEQ0          	; New program line
			SUB     TCMD
			JP      C,LET0          	; Implied "LET"
			
			LD	BC, 3
			LD	B, A 
			MLT	BC 
			LD	HL,CMDTAB
			ADD	HL, BC 
			LD	HL, (HL)		; Table entry

;			ADD     A,A
;			LD      C,A
;			LD      B,0
;			LD      HL,CMDTAB
;			ADD     HL,BC
;			LD      A,(HL)          	; Table entry
;			INC     HL
;			LD      H,(HL)
;			LD      L,A

			CALL    NXT
			JP      (HL)            	; Execute the statement