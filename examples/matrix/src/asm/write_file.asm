    assume adl=1 
    org 0x040000 
    jp start 
    align 64 
    db "MOS" 
    db 00h 
    db 01h 

start: 
    push af
    push bc
    push de
    push ix
    push iy

    call main
exit:
    pop iy
    pop ix
    pop de
    pop bc
    pop af
    ld hl,0

    ret

; Indexes into FIL structure
fil_obj:		EQU 0	; 15: Object identifier
fil_flag:		EQU	15 	;  1: File status flags
fil_err:		EQU	16	;  1: Abort flag (error code)
fil_fptr:		EQU	17	;  4: File read/write pointer (Zeroed on file open)
fil_clust:		EQU	21	;  4: Current cluster of fpter (invalid when fptr is 0)
fil_sect:		EQU	25	;  4: Sector number appearing in buf[] (0:invalid)
fil_dir_sect:	EQU	29	;  4: Sector number containing the directory entry
fil_dir_ptr:	EQU	33	;  3: Pointer to the directory entry in the win[]
fil_struct_size: EQU fil_dir_ptr+3 ; size of the FIL structure

; Indexes into FILINFO structure
filinfo_fsize:		EQU 0	;   4: File size
filinfo_fdate:		EQU	4	;   2: Modified date
filinfo_ftime:		EQU	6	;   2: Modified time
filinfo_fattrib:	EQU	8	;   1: File attribute
filinfo_altname:	EQU	9	;  13: Alternative file name
filinfo_fname:		EQU	22	; 256: Primary file name
filinfo_struct_size: EQU filinfo_fname+256 ; size of the FILINFO structure

; file access modes
fa_read:			EQU	01h
fa_write:			EQU	02h
fa_open_existing:	EQU	00h
fa_create_always:	EQU	08h

; ffs file access functions
ffs_fopen:			EQU	80h
ffs_fclose:			EQU	81h
ffs_fread:			EQU	82h
ffs_fwrite:			EQU	83h

; macro to call FFS functions
	MACRO	FFSCALL	function
			PUSH IY
			LD	A, function
			RST.LIL	08h
			POP IY
	ENDMACRO

; put the value in HLU into A
; destroys: af
    MACRO HLU_TO_A
    dec sp ; 1 cycle
    push hl ; 4 cycles
    inc sp ; 1 cycle
    pop af ; 4 cycles
    ; 10 cycles total
    ENDMACRO

main:
    call printInline
    asciz "\r\nWRITE FILE TEST\r\n"

    call read_infile
    ret nz
    call write_outfile
    ret nz

; read data from file
    ld hl,f16_fil
    ld de,filedata
    ld bc,3 ; bytes to read
    FFSCALL ffs_fread

; output bytes read
    push bc
    pop hl
    call printDec
    call printInline
    asciz " bytes read\r\n"

; process data
    ld ix,filedata
    ld hl,(ix)
    call printHexUHL
    inc hl
    ld (ix),hl
    call printInline
    asciz " value read from file\r\n"

; write data to file
    ld hl,f16_fil_out
    ld de,filedata
    ld bc,3 ; bytes to write
    FFSCALL ffs_fwrite

; output bytes written
    push bc
    pop hl
    call printDec
    call printInline
    asciz " bytes written\r\n"

; close files
    call close_infile
    call close_outfile

; read outfile to confirm correct data read
    call read_outfile
    ret nz
    ld hl,f16_fil_out
    ld de,filedata
    ld bc,3 ; bytes to read
    FFSCALL ffs_fread
    push bc
    pop hl
    call printDec
    call printInline
    asciz " bytes read from outfile\r\n"
    ld ix,filedata
    ld hl,(ix)
    call printHexUHL
    inc hl
    ld (ix),hl
    call printInline
    asciz " value read from outfile\r\n"
    call close_outfile

    ret

read_infile:
; open file for reading
    ld hl,f16_fil
    ld de,test_filename
    ld c,fa_read
    FFSCALL ffs_fopen
    or a
    ret z
    call printInline
    asciz "Error opening file for reading\r\n"
    ret

read_outfile:
; open file for writing
    ld hl,f16_fil_out
    ld de,test_filename_out
    ld c,fa_read
    FFSCALL ffs_fopen
    or a
    ret z
    call printInline
    asciz "Error opening file for writing\r\n"
    ret

write_outfile:
; open file for writing
    ld hl,f16_fil_out
    ld de,test_filename_out
    ld c,fa_write | fa_open_existing
    ; ld c,fa_write | fa_create_always
    FFSCALL ffs_fopen
    or a
    ret z
    call printInline
    asciz "Error opening file for writing\r\n"
    ret

close_infile:
    ld hl,f16_fil
    FFSCALL ffs_fclose
    ret

close_outfile:
    ld hl,f16_fil_out
    FFSCALL ffs_fclose
    ret

printInline:
    pop hl ; get the return address = pointer to start of string
    call printString ; HL advances to end of string
    push hl ; restore the return address = pointer to end of string
    ret

; Prints the right justified decimal value in UHL without leading zeroes
; UHL : Value to print
; preserves all registers and flags
printDec:
; back up all the things
    push af
    push bc
    push de
    push hl
    LD DE, _printDecBuffer
    CALL u24_to_ascii
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
    DJNZ @loop
@done:
    LD HL, _printDecBuffer
    CALL printString
; restore all the things
    pop hl
    pop de
    pop bc
    pop af
    RET
_printDecBuffer: blkb 16,0 ; a few bytes extra just to be sure
_printDec168Buffer: blkb 16,0 ; a few bytes extra just to be sure

printHexUHL:
    push af
    push bc
    call printHex24
    ld a,' '
    rst.lil 10h
    pop bc
    pop af
    ret

; Print a zero-terminated string
; HL: Pointer to string
; returns: hl pointed to character after string terminator
; destroys: af, hl
printString:
    PUSH BC
    LD BC,0
    LD A,0
    RST.LIL 18h
    POP BC
    RET

; This routine converts the unsigned 24-bit value in HLU into its ASCII representation, 
; starting to memory location pointing by DE, in decimal form and with leading zeroes 
; so it will allways be 8 characters length
; HL : Value to convert to string
; DE : pointer to buffer, at least 8 byte + 0
u24_to_ascii:
    LD BC,-10000000
    CALL one_digit
    LD BC,-1000000
    CALL one_digit
    LD BC,-100000
    CALL one_digit
    LD BC,-10000
    CALL one_digit
u8_to_ascii: ; same arguments but hl <= 255, uhl and h = 0
    LD BC,-1000
    CALL one_digit
    LD BC,-100
    CALL one_digit
    LD C,-10
    CALL one_digit
    LD C,B
one_digit:
    LD A,'0'-1
@divide_me:
    INC A
    ADD HL,BC
    JR C,@divide_me
    SBC HL,BC
    LD (DE),A
    INC DE
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

test_filename: asciz "test_write_file.bin"
test_filename_out: asciz "test_write_file.bin"

f16_fil: equ $
f16_filinfo: equ f16_fil + fil_struct_size

f16_fil_out: equ f16_filinfo + filinfo_struct_size
f16_filinfo_out: equ f16_fil_out + fil_struct_size

    align 256

filedata: equ $