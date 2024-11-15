
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

; put the value in HLU into the accumulator
; destroys: af
    MACRO HLU_TO_A
        push hl ; 4 cycles
        inc sp ; 1 cycle
        pop af  ; 4 cycles
        dec sp ; 1 cycle
               ; 10 cycles total
    ENDMACRO

; Print a 24-bit HEX number
; HLU: Number to print
printHex24:
    HLU_TO_A
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
	; LD		C,A
    ld (uaf+1),a
	RRA 
	RRA 
	RRA 
	RRA 
	CALL	@F
	; LD		A,C
    ld a,(uaf+1)
@@:
	AND		0Fh
	ADD		A,90h
	DAA
	ADC		A,40h
	DAA
	RST.LIL	10h
	RET

; print the binary representation of the 8-bit value in a
; destroys a, hl, bc
printBin8:
    ld b,8      ; loop counter for 8 bits
    ld hl,@cmd  ; set hl to the low byte of the output string
                ; (which will be the high bit of the value in a)
@loop:
    rlca ; put the next highest bit into carry
    jr c,@one
    ld (hl),'0'
    jr @next_bit
@one:
    ld (hl),'1'
@next_bit:
    inc hl
    djnz @loop
; print it
	ld hl,@cmd         
	ld bc,@end-@cmd    
	rst.lil $18         
	ret
@cmd: ds 8 ; eight bytes for eight bits
@end:

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

; Print a zero-terminated string inline with code, e.g.:
;
;    call printInline
;    ASCIZ "Hello, world!\r\n"
;
; Destroys: HL,AF
printInline:
    pop hl ; get the return address = pointer to start of string
    call printString ; HL advances to end of string
    push hl ; restore the return address = pointer to end of string
    ret

; inputs: whatever is in the flags register
; outputs: binary representation of flags
;          with a header so we know which is what
; destroys: nothing
; preserves: everything
dumpFlags:
; first we curse zilog for not giving direct access to flags
    push af ; this is so we can send it back unharmed
    push af ; this is so we can pop it to hl
; store everything in scratch
    ld (uhl),hl
    ld (ubc),bc
    ld (ude),de
    ld (uix),ix
    ld (uiy),iy
; next we print the header 
    ld hl,@header
    call printString
    pop hl ; flags are now in l
    ld a,l ; flags are now in a
    call printBin8
	call printNewLine
; restore everything
    ld hl, (uhl)
    ld bc, (ubc)
    ld de, (ude)
    ld ix, (uix)
    ld iy, (uiy)
    pop af ; send her home the way she came
    ret
; Bit 7 (S): Sign flag
; Bit 6 (Z): Zero flag
; Bit 5 (5): Reserved (copy of bit 5 of the result)
; Bit 4 (H): Half Carry flag
; Bit 3 (3): Reserved (copy of bit 3 of the result)
; Bit 2 (PV): Parity/Overflow flag
; Bit 1 (N): Subtract flag
; Bit 0 (C): Carry flag
@header: db "SZxHxPNC\r\n",0 ; cr/lf and 0 terminator

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

; store HLH'L'C floating point number in a 40-bit buffer
; inputs: HLH'L'C = floating point number
;         ix = buffer address
; outputs: buffer filled with floating point number
; destroys: nothing
store_float_pri:
    ld (ix+0),c
    ld (ix+3),l
    ld (ix+4),h
    exx
    ld (ix+1),l
    ld (ix+2),h
    exx
    ret

; store DED'E'B floating point number in a 40-bit buffer
; inputs: DED'E'B = floating point number
;         ix = buffer address
; outputs: buffer filled with floating point number
; destroys: nothing
store_float_sec:
    ld (ix+0),b
    ld (ix+3),e
    ld (ix+4),d
    exx
    ld (ix+1),e
    ld (ix+2),d
    exx
    ret

; fetch HLH'L'C floating point number from a 40-bit buffer
; inputs: ix = buffer address
; outputs: HLH'L'C = floating point number
; destroys: HLH'L'C
fetch_float_nor:
    ld c,(ix+0)
    ld l,(ix+3)
    ld h,(ix+4)
    exx
    ld l,(ix+1)
    ld h,(ix+2)
    exx
    ret

; fetch DED'E'B floating point number from a 40-bit buffer
; inputs: ix = buffer address
; outputs: DED'E'B = floating point number
; destroys: DED'E'B
fetch_float_alt:
    ld b,(ix+0)
    ld e,(ix+3)
    ld d,(ix+4)
    exx
    ld e,(ix+1)
    ld d,(ix+2)
    exx
    ret

; print HLH'L'C floating point number in hex format
; inputs: HLH'L'C = floating point number
print_float_hex_nor:
    call printHex16
    ld a,'.'
    rst.lil 10h
    exx 
    call printHex16
    exx
    ld a,'^'
    rst.lil 10h
    ld a,c
    call printHex8
    ret

; print DED'E'B floating point number in hex format
; inputs: DED'E'B = floating point number
print_float_hex_alt:
    ex de,hl
    call printHex16
    ex de,hl
    ld a,'.'
    rst.lil 10h
    exx 
    ex de,hl
    call printHex16
    ex de,hl
    exx
    ld a,'^'
    rst.lil 10h
    ld a,b
    call printHex8
    ret

print_floats_hex:
    call print_float_hex_nor
    ld a,' '
    rst.lil 10h
    call print_float_hex_alt
    ret

; print a floating point number in decimal format
; inputs: HL'H'L'C is the number to print
; outputs: number printed to screen
;          ACCS null-terminated string representation of the number
; destroys: everything except ix
print_float_dec:
print_float_dec_nor:
    push ix             ; save the pointer to the parameters
    ld de,ACCS          ; point to the string accumulator
    ld ix,@G9-1         ; get the format code for the number
    call STR ; convert the number to a string
    ld hl,ACCS ; point to the string accumulator
    call printString
    pop ix              ; restore the pointer to the parameters
    ret
@G9:			DW    9