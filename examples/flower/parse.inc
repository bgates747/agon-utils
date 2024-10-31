;
; Title:	Number Parsing Functions
; Author:	Dean Belfield
; Created:	15/11/2022
; Last Updated:	15/11/2022
; Last Updated: 29/12/2022 Lennart Benchop adapt for 24-bit mode.
; Modinfo:
; 2024/04/08    Adapt for ez80asm
				
; Read a number and convert to binary
; If prefixed with &, will read as hex, otherwise decimal
;   Inputs: HL: Pointer in string buffer
;  Outputs: HL: Updated text pointer
;           DE: Value
;            A: Terminator (spaces skipped)
;            F: Carry set if valid number, otherwise reset
; Destroys: A,D,E,H,L,F
;
ASC_TO_NUMBER:		LD		DE, 0			; Initialise DE
			CALL		_skip_spaces		; Skip whitespace
			LD		A, (HL)			; Read first character
			OR		A			; Check for end of string
			RET		Z			; Return with no carry if not
			PUSH		BC			; Preserve BC
			CP		'&'			; Is it prefixed with '&' (HEX number)?
			JR		NZ, ASC_TO_NUMBER3	; Jump to decimal parser if not
			INC		HL			; Otherwise fall through to ASC_TO_HEX
;
ASC_TO_NUMBER1:		LD		A, (HL)			; Fetch the character
			CALL   	 	UPPRC			; Convert to uppercase  
			SUB		'0'			; Normalise to 0
			JR 		C, ASC_TO_NUMBER4	; Return if < ASCII '0'
			CP 		10			; Check if >= 10
			JR 		C, ASC_TO_NUMBER2	; No, so skip next bit
			SUB 		7			; Adjust ASCII A-F to nibble
			CP 		16			; Check for > F
			JR 		NC, ASC_TO_NUMBER4	; Return if out of range
;
ASC_TO_NUMBER2:		PUSH		HL			; Stack HL
			PUSH		DE			; LD HL, DE
			POP		HL
			ADD		HL, HL	
			ADD		HL, HL	
			ADD		HL, HL	
			ADD		HL, HL	
			PUSH		HL			; LD DE, HL
			POP		DE
			POP		HL			; Restore HL			
			OR      	E			; OR the new digit in to the least significant nibble
			LD      	E, A
;			
			INC		HL			; Onto the next character
			JR      	ASC_TO_NUMBER1		; And loop
;
ASC_TO_NUMBER3:		LD		A, (HL)
			SUB		'0'			; Normalise to 0
			JR		C, ASC_TO_NUMBER4	; Return if < ASCII '0'
			CP		10			; Check if >= 10
			JR		NC, ASC_TO_NUMBER4	; Return if >= 10
;
			PUSH		HL			; Stack HL
			PUSH		DE			; LD HL, DE
			POP		HL
			PUSH		HL			; LD BC, HL
			POP		BC
			ADD		HL, HL 			; x 2 
			ADD		HL, HL 			; x 4
			ADD		HL, BC 			; x 5
			ADD		HL, HL 			; x 10
			LD		BC, 0
			LD 		C, A			; LD BCU, A
			ADD		HL, BC			; Add BCU to HL
			PUSH		HL			; LD DE, HL
			POP		DE
			POP		HL			; Restore HL
;						
			INC		HL
			JR		ASC_TO_NUMBER3
ASC_TO_NUMBER4:		POP		BC 			
			SCF					; We have a valid number so set carry
			RET


; Convert a character to upper case
;  A: Character to convert
;
UPPRC:  		AND     	7FH
			CP      	'`'
			RET     	C
			AND     	5FH			; Convert to upper case
			RET


;------------------------------------------------------------------------
; Read a number and convert to binary (decimal only)
; Inputs: hl: Pointer in string buffer
; Outputs: hl: Updated text pointer
;         de: Value
;         a: Terminator (spaces skipped)
;         f: Carry set if valid number, otherwise reset
; Destroys: a, d, e, h, l, f
;------------------------------------------------------------------------
signed_asc_to_int: 
    ld a,1 ; set sign flag
    ld (@sign),a ; store sign flag
    
    ld de, 0 ; initialise de
    call _skip_spaces ; skip whitespace
    
    ld a, (hl) ; read first character
    or a ; check for end of string
    ret z ; return with no carry if not

    push bc ; preserve bc

    cp '-' ; check for negative number
    jp nz,@loop ; number is positive, nothing more to do
    xor a ; sign flag to zero
    ld (@sign),a ; store sign flag
    inc hl ; skip '-'

@loop: 
    ld a, (hl)
    sub '0' ; normalise to 0
    jr c, @integer_end ; return if < ascii '0'
    cp 10 ; check if >= 10
    jr nc, @integer_end ; return if >= 10
    push hl ; stack hl
    push de ; ld hl, de
    pop hl
    push hl ; ld bc, hl
    pop bc
    add hl, hl ; x 2 
    add hl, hl ; x 4
    add hl, bc ; x 5
    add hl, hl ; x 10
    ld bc, 0
    ld c, a ; ld bcu, a
    add hl, bc ; add bcu to hl
    push hl ; ld de, hl
    pop de
    pop hl ; restore hl
    inc hl
    jr @loop

@integer_end: 
    pop bc ; send bc back how she came in
    ld a, (@sign) ; get sign flag
    dec a ; check if negative    
    jp p,@pos ; positive number

; Negate de
    push hl ; save text pointer
    ld hl, 0
    xor a ; clear carry
    sbc hl, de ; subtract DE from HL
    ex de, hl ; DE = 0-HL
    pop hl ; restore text pointer

@pos:
    scf ; we have a valid number so set carry
    ret

@sign: db 0 ; sign flag buffer


;------------------------------------------------------------------------
; Read a number and convert to binary (decimal only)
; Inputs: hl: Pointer in string buffer
; Outputs: hl: Updated text pointer
;         de: Value
;         a: Terminator (spaces skipped)
;         f: Carry set if valid number, otherwise reset
; Destroys: a, d, e, h, l, f
;------------------------------------------------------------------------
signed_asc_to_168: 
    ld a,1 ; set sign flag
    ld (@sign),a ; store sign flag
    
    ld de, 0 ; initialise de
    ld (@result), de ; clear low bytes of result buffer
    ld (@scratch), de ; clear low bytes of scratch buffer

    call _skip_spaces ; skip whitespace
    
    ld a, (hl) ; read first character
    or a ; check for end of string
    ret z ; return with no carry if not

    push bc ; preserve bc

    cp '-' ; check for negative number
    jp nz,@loop ; number is positive, nothing more to do
    xor a ; sign flag to zero
    ld (@sign),a ; store sign flag
    inc hl ; skip '-'

@loop: 
    ld a, (hl)

; chcek for decimal point
    cp '.' ; check for decimal point
    jp z,@fractional_start ; jump to fractional part

; process integer part
    sub '0' ; normalise to 0
    jr c, @integer_end ; return if < ascii '0'
    cp 10 ; check if >= 10
    jr nc, @integer_end ; return if >= 10
    push hl ; stack hl
    push de ; ld hl, de
    pop hl
    push hl ; ld bc, hl
    pop bc
    add hl, hl ; x 2 
    add hl, hl ; x 4
    add hl, bc ; x 5
    add hl, hl ; x 10
    ld bc, 0
    ld c, a ; ld bcu, a
    add hl, bc ; add bcu to hl
    push hl ; ld de, hl
    pop de
    pop hl ; restore hl
    inc hl
    jr @loop

@integer_end:
    ld (@result+1), de      ; Store integer part in result buffer (shifted up one byte)

@end: 
    pop bc ; send bc back how she came in
    ld de,(@result) ; will contain shifted integer part combined with any fractional value
    ld a, (@sign) ; get sign flag
    dec a ; check if negative    
    jp p,@pos ; positive number

; Negate de
    push hl ; save text pointer
    ld hl, 0
    xor a ; clear carry
    sbc hl, de ; subtract DE from HL
    ex de, hl ; DE = 0-HL
    pop hl ; restore text pointer

@pos:
    scf ; we have a valid number so set carry
    ret

@fractional_start:
    ld (@result+1), de         ; Store integer part in result buffer (shifted up one byte)
    ld b, 3                    ; Set loop counter to 3 for up to three fractional digits
    ld de, 0                   ; Initialize DE as the fractional accumulator
    ld ix, powers_of_10        ; Point IX to the lookup table for the scaling factor based on digits
    inc hl                     ; Skip decimal point

@fractional_loop:
    ld a, (hl)                 ; Load next character
    sub '0'                    ; Normalize ASCII to decimal
    jr c, @end_fraction        ; Exit if < '0'
    cp 10
    jr nc, @end_fraction       ; Exit if >= 10

    ; Multiply the current fractional accumulator by 10
    push hl                    ; Save HL (used as pointer)
    push af                    ; Save the digit
    ld hl, 10                  ; Prepare to multiply by 10
    call umul24                ; hl = de * 10
    ld de, 0                   ; Clear DEU
    pop af                     ; Restore the current digit
    ld e, a                    ; Load the digit into E
    add hl, de                 ; Add the digit to the accumulator
    ex de, hl                  ; Result back to DE
    lea ix,ix+3                ; Advance IX to the next scaling factor
    pop hl                     ; Restore char pointer
    inc hl                     ; Move to the next character
    djnz @fractional_loop      ; Loop if more digits to process

@end_fraction:
; Final scaling based on number of fractional digits processed
    ld (@scratch+1), de          ; Shift fractional part up a byte
    ld hl,(@scratch)             ; Load the shifted fractional part into HL

    ld de, (ix)                ; Load final scaling factor from IX based on digit count
    call udiv24                ; Perform 24-bit division to scale down
    ld a, e                    ; Load the low byte (8-bit fractional part) into A
    ld (@result), a            ; Store fractional part in result buffer
    jp @end                    ; Final sign check and flag setup

@result: ds 4                  ; 32-bit result buffer to shift integer part up one byte
@scratch: ds 4                 ; 32-bit scratch buffer for intermediate calculations
@sign: db 0                    ; Sign flag buffer

powers_of_10:
    dl 1                       ; 10^0
    dl 10                      ; 10^1
    dl 100                     ; 10^2
    dl 1000                    ; 10^3
    dl 10000                   ; 10^4
