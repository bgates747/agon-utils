; Parse the parameter string into a C array
; Parameters
; - HL: Address of parameter string
; - IX: Address for array pointer storage
; Returns:
; -  C: Number of parameters parsed
;
_parse_params:		LD	BC, _exec_name
			LD	(IX+0), BC		; ARGV[0] = the executable name
			LEA     IX, IX+3
			CALL	_skip_spaces		; Skip HL past any leading spaces
;
			LD	BC, 1			; C: ARGC = 1 - also clears out top 16 bits of BCU
			LD	B, argv_ptrs_max - 1	; B: Maximum number of argv_ptrs
;
_parse_params_1:	
			PUSH	BC			; Stack ARGC	
			PUSH	HL			; Stack start address of token
			CALL	_get_token		; Get the next token
			LD	A, C			; A: Length of the token in characters
			POP	DE			; Start address of token (was in HL)
			POP	BC			; ARGC
			OR	A			; Check for A=0 (no token found) OR at end of string
			RET	Z
;
			LD	(IX+0), DE		; Store the pointer to the token
			PUSH	HL			; DE=HL
			POP	DE
			CALL	_skip_spaces		; And skip HL past any spaces onto the next character
			XOR	A
			LD	(DE), A			; Zero-terminate the token
			LEA  	IX, IX+3			; Advance to next pointer position
			INC	C			; Increment ARGC
			LD	A, C			; Check for C >= A
			CP	B
			JR	C, _parse_params_1	; And loop
			RET

; Get the next token
; Parameters:
; - HL: Address of parameter string
; Returns:
; - HL: Address of first character after token
; -  C: Length of token (in characters)
;
_get_token:		LD	C, 0			; Initialise length
@@:			LD	A, (HL)			; Get the character from the parameter string
			OR	A			; Exit if 0 (end of parameter string in MOS)
			RET 	Z
			CP	13			; Exit if CR (end of parameter string in BBC BASIC)
			RET	Z
			CP	' '			; Exit if space (end of token)
			RET	Z
			INC	HL			; Advance to next character
			INC 	C			; Increment length
			JR	@B
	
; Skip spaces in the parameter string
; Parameters:
; - HL: Address of parameter string
; Returns:
; - HL: Address of next none-space character
;    F: Z if at end of string, otherwise NZ if there are more tokens to be parsed
;
_skip_spaces:		LD	A, (HL)			; Get the character from the parameter string	
			CP	' '			; Exit if not space
			RET	NZ
			INC	HL			; Advance to next character
			JR	_skip_spaces		; Increment length

; Storage for the argv array pointers
min_args: equ 1
argv_ptrs_max:		EQU	16			; Maximum number of arguments allowed in argv
argv_ptrs:		    BLKP	argv_ptrs_max, 0		
_sps:			DS	3			; Storage for the stack pointer (used by BASIC)

; begin BASIC-specific end code
; This bit of code is called from STAR_BYE and returns us safely to MOS
_end:			LD		SP, (_sps)		; Restore the stack pointer 
; fall through to _main_end_ok
; end BASIC-specific end code

; ========== HELPER FUNCTIONS ==========
;
; get the next argument after ix as a floating point number
; inputs: ix = pointer to the argument string
; outputs: HLH'L'C = floating point number, ix points to the next argument
; destroys: everything except iy, including prime registers
get_arg_float:
    lea ix,ix+3 ; point to the next argument
    push ix ; preserve
    ld ix,(ix)  ; point to argument string
    call val_fp ; convert the string to a float
    pop ix ; restore
    ret ; return with the value in HLH'L'C

; get the next argument after ix as a floating point number and store it in buffer pointed to by iy
; inputs: ix = pointer to the argument string
; outputs: HLH'L'C = floating point number, ix points to the next argument
; destroys: everything except iy, including prime registers
store_arg_iy_float:
    lea ix,ix+3 ; point to the next argument
    push ix ; preserve
    ld ix,(ix)  ; point to argument string
    call val_fp ; convert the string to a float
    call store_float_iy_nor ; save the float in buffer
    pop ix ; restore
    ret ; return with the value in HLH'L'C