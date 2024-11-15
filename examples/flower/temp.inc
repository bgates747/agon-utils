
; global scratch memory for registers
uaf: dl 0
uhl: dl 0
ubc: dl 0
ude: dl 0
uix: dl 0
uiy: dl 0
usp: dl 0
upc: dl 0

str_afu: db " af=",0
str_hlu: db " hl=",0
str_bcu: db " bc=",0
str_deu: db " de=",0
str_ixu: db " ix=",0
str_iyu: db " iy=",0

; test the sign of HL
; inputs: HL obviously
; outputs: sign flag set if HL is negative, zero flag set if HL is zero
; destroys: flags    
    MACRO sign_hlu
        add hl,de
        or a
        sbc hl,de
    ENDMACRO

    MACRO PUSH_ALL
        ex af,af'
        exx
        push af
        push hl
        push bc
        push de

        ex af,af'
        exx
        push af
        push hl
        push bc
        push de
        push ix
        push iy
    ENDMACRO

    MACRO POP_ALL
        pop iy
        pop ix
        pop de
        pop bc
        pop hl
        pop af
        ex af,af'
        exx

        pop de
        pop bc
        pop hl
        pop af
        ex af,af'
        exx
    ENDMACRO

; Print a 24-bit HEX number
; HLU: Number to print
printHex24:
	; PUSH	HL      ; 4 cycles
	; LD		HL, 2   ; 4 cycles
	; ADD		HL, SP  ; 1 cycle
	; LD		A, (HL) ; 2 cycles
	; POP		HL      ; 4 cycles
    ;                 ; 15 cycles total
    push hl ; 4 cycles
    inc sp ; 1 cycle
    pop af  ; 4 cycles
    dec sp ; 1 cycle
            ; 10 cycles total
	CALL	printHex8
; Print a 16-bit HEX number
; HL: Number to print
printHex16:
	LD		A,H
	CALL	printHex8
	LD		A,L
; Print an 8-bit HEX number
; A: Number to print
printHex8:
	LD		C,A
	RRA 
	RRA 
	RRA 
	RRA 
	CALL	@F
	LD		A,C
@@:
	AND		0Fh
	ADD		A,90h
	DAA
	ADC		A,40h
	DAA
	RST.LIL	10h
	RET

; https://github.com/envenomator/Agon/blob/master/ez80asm%20examples%20(annotated)/functions.s
; Print a zero-terminated string
; HL: Pointer to string
printString:
	PUSH	BC
	LD		BC,0
	LD 	 	A,0
	RST.LIL 18h
	POP		BC
	RET
; print a VDU sequence
; HL: Pointer to VDU sequence - <1 byte length> <data>
sendVDUsequence:
	PUSH	BC
	LD		BC, 0
	LD		C, (HL)
	RST.LIL	18h
	POP		BC
	RET
; Print Newline sequence to VDP
printNewLine:
    push af ; for some reason rst.lil 10h sets carry flag
	LD	A, '\r'
	RST.LIL 10h
	LD	A, '\n'
	RST.LIL 10h
    pop af
	RET

; print registers to screen in hexidecimal format
; inputs: none
; outputs: values of every register printed to screen
;    values of each register in global scratch memory
; destroys: nothing
dumpRegistersHex:
; store everything in scratch
    ld (uhl),hl
    ld (ubc),bc
    ld (ude),de
    ld (uix),ix
    ld (uiy),iy
    push af ; fml
    pop hl  ; thanks, zilog
    ld (uaf),hl
    push af ; dammit

; home the cursor
    ; call vdu_home_cursor
    ; call printNewLine

; print each register
    ld hl,str_afu
    call printString
    ld hl,(uaf)
    call printHex24
    ; call printNewLine

    ld hl,str_hlu
    call printString
    ld hl,(uhl)
    call printHex24
    ; call printNewLine

    ld hl,str_bcu
    call printString
    ld hl,(ubc)
    call printHex24
    ; call printNewLine

    ld hl,str_deu
    call printString
    ld hl,(ude)
    call printHex24
    ; call printNewLine

    ld hl,str_ixu
    call printString
    ld hl,(uix)
    call printHex24
    ; call printNewLine

    ld hl,str_iyu
    call printString
    ld hl,(uiy)
    call printHex24
    ; call printNewLine

    ; call vdu_vblank

    call printNewLine
; restore everything
    ld hl, (uhl)
    ld bc, (ubc)
    ld de, (ude)
    ld ix, (uix)
    ld iy, (uiy)
    pop af
; all done
    ret

dumpRegistersHexPrime:
    exx
    ex af,af'
    call dumpRegistersHex
    ex af,af'
    exx
    ret

; additionally dump prime registers
; inputs: none
; outputs: values of every register printed to screen
; destroys: nothing
dumpRegistersHexAll:
    call dumpRegistersHex
    ex af,af'
    exx
    call dumpRegistersHex
    ex af,af'
    exx
    ret

; print bytes from an address to the screen in hexidecimal format
; inputs: hl = address of first byte to print, a = number of bytes to print
; outputs: values of each byte printed to screen separated by spaces
; destroys: nothing
dumpMemoryHex:
; save registers to the stack
    push bc
    push hl
    push af

; print the address and separator
    call printHex24
    ld a,':'
    rst.lil 10h
    ld a,' '
    rst.lil 10h

; set b to be our loop counter
    pop af
    ld b,a
    pop hl
    push hl
    push af
@loop:
; print the byte
    ld a,(hl)
    call printHex8
; print a space
    ld a,' '
    rst.lil 10h
    inc hl
    djnz @loop
    call printNewLine

; restore everything
    pop af
    pop hl
    pop bc

; all done
    ret