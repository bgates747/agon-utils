    align 256

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
    
; https://github.com/envenomator/Agon/blob/master/ez80asm%20examples%20(annotated)/functions.s
; Print a zero-terminated string
; HL: Pointer to string
printString:
    PUSH BC
    LD BC,0
    LD A,0
    RST.LIL 18h
    POP BC
    RET
; print a VDU sequence
; HL: Pointer to VDU sequence - <1 byte length> <data>
sendVDUsequence:
    PUSH BC
    LD BC, 0
    LD C, (HL)
    RST.LIL 18h
    POP BC
    RET
; Print Newline sequence to VDP
; destroys bc
printNewLine:
    push af ; for some reason rst.lil 10h sets carry flag
    LD A, '\r'
    RST.LIL 10h
    LD A, '\n'
    RST.LIL 10h
    pop af
    RET

; Print a 24-bit HEX number
; HLU: Number to print
printHex24:
    HLU_TO_A
    CALL printHex8
; Print a 16-bit HEX number
; HL: Number to print
printHex16:
    LD A,H
    CALL printHex8
    LD A,L
; Print an 8-bit HEX number
; A: Number to print
printHex8:
    LD C,A
    RRA 
    RRA 
    RRA 
    RRA 
    CALL @F
    LD A,C
@@:
    AND 0Fh
    ADD A,90h
    DAA
    ADC A,40h
    DAA
    RST.LIL 10h
    RET

; Print a 0x HEX prefix
DisplayHexPrefix:
    LD A, '0'
    RST.LIL 10h
    LD A, 'x'
    RST.LIL 10h
    RET

    MACRO printDecBC
    push hl
    push bc
    pop hl
    call printDec
    pop hl
    ENDMACRO

    MACRO printDecDE
    push hl
    push de
    pop hl
    call printDec
    pop hl
    ENDMACRO

    MACRO printDecHL
    call printDec
    ENDMACRO

    MACRO printDecIX
    push hl
    push ix
    pop hl
    call printDec
    pop hl
    ENDMACRO

    MACRO printDecIY
    push hl
    push iy
    pop hl
    call printDec
    pop hl
    ENDMACRO


; Prints the right justified decimal value in HL without leading zeroes
; HL : Value to print
; preserves all registers and flags
printDec:
; BEGIN MY CODE
; back up all the things
    push af
    push bc
    push de
    push hl
; END MY CODE
    LD DE, _printDecBuffer
    CALL u24_to_ascii
; BEGIN MY CODE
; replace leading zeroes with spaces
    LD HL, _printDecBuffer
    ld B, 7 ; if HL was 0, we want to keep the final zero 
@loop:
    LD A, (HL)
    CP '0'
    JP NZ, @done
    LD A, ' '
    LD (HL), A
    INC HL
    ; CALL vdu_cursor_forward
    DJNZ @loop
@done:
; END MY CODE
    LD HL, _printDecBuffer
    CALL printString
; BEGIN MY CODE
; restore all the things
    pop hl
    pop de
    pop bc
    pop af
; END MY CODE
    RET
_printDecBuffer: blkb 16,0 ; a few bytes extra just to be sure

; This routine converts the unsigned 24-bit value in HLU into its ASCII representation, 
; starting to memory location pointing by DE, in decimal form and with leading zeroes 
; so it will allways be 8 characters length
; HL : Value to convert to string
; DE : pointer to buffer, at least 8 byte + 0
u24_to_ascii:
    LD BC,-10000000
    CALL @one_digit
    LD BC,-1000000
    CALL @one_digit
    LD BC,-100000
    CALL @one_digit
    LD BC,-10000
    CALL @one_digit
    LD BC,-1000
    CALL @one_digit
    LD BC,-100
    CALL @one_digit
    LD C,-10
    CALL @one_digit
    LD C,B
@one_digit:
    LD A,'0'-1
@divide_me:
    INC A
    ADD HL,BC
    JR C,@divide_me
    SBC HL,BC
    LD (DE),A
    INC DE
    RET

print_u24:
    push de
    push hl
    ld de,_printDecBuffer
    call u24_to_ascii
    ld hl,_printDecBuffer
    call printString
    ld a,' '
    rst.lil 10h
    pop hl
    pop de
    ret

; u168_to_ascii: Converts an unsigned 16.8 fixed-point value in HL to an ASCII string.
; HL : Value to convert to string (integer part in H, fractional part in L)
; DE : Pointer to buffer, requires at least 11 bytes (8 digits, sign, decimal point, and null terminator)
u168_to_ascii:
; add a leading space to make room for sign flag if needed
    ld a,' '
    ld (de),a
    inc de
; Convert integer part
    push hl ; Save HL (we’ll need the fractional part later)
    ; call hlu_udiv256 ; Shift to get integer portion in HL
    SRL_UHL ; Shift to get integer portion in HL
    ld bc, -10000
    call @one_int
    ld bc, -1000
    call @one_int
    ld bc, -100
    call @one_int
    ld c, -10
    call @one_int
    ld c, b
    call @one_int
    jp @frac ; Jump to fractional part conversion
@one_int:
    ld a, '0' - 1 ; Start ASCII character at '0'
@divide_me:
    inc a
    add hl, bc ; Accumulate until overflow
    jr c, @divide_me
    sbc hl, bc ; Remove excess after overflow
    ld (de), a ; Store ASCII digit
    inc de
    ret
; Convert fractional part
@frac:
    ld a, '.' ; Decimal point
    ld (de), a
    inc de
    pop hl ; Restore HL with original fraction
    ld b, 3 ; Loop counter for 3 fractional digits
@frac_loop:
    ld h, 10 ; Load multiplier for fractional part
    mlt hl ; Multiply by 10, result in HL (H holds the integer part)
    ld a, '0'
    add a, h ; Convert integer part to ASCII
    ld (de), a
    inc de
    djnz @frac_loop ; Repeat for each fractional digit
; Add null terminator
    xor a ; Null terminator
    ld (de), a
    ret

print_u168:
    push de
    push hl
    ld de,_printDecBuffer
    call u168_to_ascii
    ld hl,_printDecBuffer
    call printString
    pop hl
    pop de
    ret

; signed version of u168_to_ascii
s168_to_ascii:
    push de ; save starting address of buffer
    call hlu_abs
    push af ; save sign flag
    call u168_to_ascii
    pop af ; restore sign flag
    pop de ; restore starting address of buffer
    ret p ; hlu was positive so nothing to do
    ld a,'-'
    ld (de),a
    ret

print_s168:
    push de
    push hl
    ld de,_printDecBuffer
    call s168_to_ascii
    ld hl,_printDecBuffer
    call printString
    pop hl
    pop de
    ret

print_s168_hl:
    push af
    push hl
    call print_s168
    ld a,' '
    rst.lil 10h
    pop hl
    pop af
    ret

print_s168_bc:
    push af
    push bc
    push hl
    push bc
    pop hl
    call print_s168
    ld a,' '
    rst.lil 10h
    pop hl
    pop bc
    pop af
    ret

print_s168_de:
    push af
    push de
    push hl
    ex de,hl
    call print_s168
    ld a,' '
    rst.lil 10h
    pop hl
    pop de
    pop af
    ret

print_s168_hl_bc_de:
    push af
    push bc
    push de
    push hl
    call print_s168
    ld a,' '
    rst.lil 10h
    push bc
    pop hl
    call print_s168
    ld a,' '
    rst.lil 10h
    ex de,hl
    call print_s168
    ld a,' '
    rst.lil 10h
    pop hl
    pop de
    pop bc
    pop af
    ret

print_s168_bc_de:
    push af
    push bc
    push de
    push bc
    pop hl
    call print_s168
    ld a,' '
    rst.lil 10h
    ex de,hl
    call print_s168
    ld a,' '
    rst.lil 10h
    pop hl
    pop de
    pop bc
    pop af
    ret

print_s168_a:
    push af
    push bc
    push hl
    ld hl,0
    ld l,a
    call print_s168_hl
    pop hl
    pop bc
    pop af
    ret

; #### new functions added by Brandon R. Gates ####

; print the binary representation of the 8-bit value in a
; destroys a, hl, bc
printBin8:
    ld b,8 ; loop counter for 8 bits
    ld hl,@cmd ; set hl to the low byte of the output string
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

; print the binary representation of the 8-bit value in a
; in reverse order (lsb first)
; destroys a, hl, bc
printBin8Rev:
    ld b,8 ; loop counter for 8 bits
    ld hl,@cmd ; set hl to the low byte of the output string
    ; (which will be the high bit of the value in a)
@loop:
    rrca ; put the next lowest bit into carry
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

str_afu: db " af=",0
str_hlu: db " hl=",0
str_bcu: db " bc=",0
str_deu: db " de=",0
str_ixu: db " ix=",0
str_iyu: db " iy=",0

; print udeuhl to screen in hexidecimal format
; inputs: none
; outputs: concatenated hexidecimal udeuhl 
; destroys: nothing
dumpUDEUHLHex:
; store everything in scratch
    ld (uhl),hl
    ld (ubc),bc
    ld (ude),de
    ld (uix),ix
    ld (uiy),iy
    push af

; print each register

    ld hl,str_udeuhl
    call printString
    ld hl,(ude)
    call printHex24
    ld a,'.' ; print a dot to separate the values
    rst.lil 10h
    ld hl,(uhl)
    call printHex24
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

str_udeuhl: db "ude.uhl=",0

; global scratch memory for registers
uaf: dl 0
uhl: dl 0
ubc: dl 0
ude: dl 0
uix: dl 0
uiy: dl 0
usp: dl 0
upc: dl 0


; set all the bits in the flag register
; more of an academic exercise than anything useful
; inputs; none
; outputs; a=0,f=255
; destroys: flags, hl
; preserves: a, because why not
setAllFlags:
    ld hl,255
    ld h,a ; four cycles to preserve a is cheap
    push hl
    pop af
    ret

; reset all the bits in the flag register
; unlike its inverse counterpart, this may actually be useful
; inputs; none
; outputs; a=0,f=0
; destroys: flags, hl
; preserves: a, because why not
resetAllFlags:
    ld hl,0
    ld h,a ; four cycles to preserve a is cheap
    push hl
    pop af
    ret

; wait until user presses a key
; inputs: none
; outputs: ascii code of key pressed in a
; destroys: af,ix
waitKeypress:
    MOSCALL mos_getkey
    ret

; clear a block of memory by writing a prescribed value to each byte in the range
; inputs: a = value to write, hl = address of first byte, bc = number of bytes
; outputs: memory block is cleared
; destroys: hl, de
clear_mem:
    dec bc ; we do this because we will increment de before writing the first byte
    ld (hl),a
    push hl
    pop de
    inc de ; target address
    ldir
    ret