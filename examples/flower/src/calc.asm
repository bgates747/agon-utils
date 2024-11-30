 ASSUME ADL = 1 
    ORG 0x0B0000 ; Is a moslet
    JP _start

_exec_name: ASCIZ "fixed168"
    ALIGN 64
    DB "MOS" ; Flag for MOS - to confirm this is a valid MOS command
    DB 00h ; MOS header version 0
    DB 01h ; Flag for run mode (0: Z80, 1: ADL)
_start: 
    PUSH AF ; Preserve the registers
    PUSH BC
    PUSH DE
    PUSH IX
    PUSH IY
    LD A, MB ; Save MB
    PUSH AF
    XOR A
    LD MB, A ; Clear to zero so MOS API calls know how to use 24-bit addresses.

    LD IX, argv_ptrs ; The argv array pointer address
    PUSH IX
    CALL _parse_params ; Parse the parameters
    POP IX ; IX: argv 
    LD B, 0 ; C: argc
    CALL _main_init ; Start user code
    
    POP AF
    LD MB, A
    POP IY ; Restore registers
    POP IX
    POP DE
    POP BC
    POP AF
    RET
    
; Parse the parameter string into a C array
; Parameters
; - HL: Address of parameter string
; - IX: Address for array pointer storage
; Returns:
; - C: Number of parameters parsed
;
_parse_params: LD BC, _exec_name
    LD (IX+0), BC ; ARGV[0] = the executable name
    LEA IX, IX+3
    CALL _skip_spaces ; Skip HL past any leading spaces
;
    LD BC, 1 ; C: ARGC = 1 - also clears out top 16 bits of BCU
    LD B, argv_ptrs_max - 1 ; B: Maximum number of argv_ptrs
;
_parse_params_1: 
    PUSH BC ; Stack ARGC 
    PUSH HL ; Stack start address of token
    CALL _get_token ; Get the next token
    LD A, C ; A: Length of the token in characters
    POP DE ; Start address of token (was in HL)
    POP BC ; ARGC
    OR A ; Check for A=0 (no token found) OR at end of string
    RET Z
;
    LD (IX+0), DE ; Store the pointer to the token
    PUSH HL ; DE=HL
    POP DE
    CALL _skip_spaces ; And skip HL past any spaces onto the next character
    XOR A
    LD (DE), A ; Zero-terminate the token
    LEA IX, IX+3 ; Advance to next pointer position
    INC C ; Increment ARGC
    LD A, C ; Check for C >= A
    CP B
    JR C, _parse_params_1 ; And loop
    RET

; Get the next token
; Parameters:
; - HL: Address of parameter string
; Returns:
; - HL: Address of first character after token
; - C: Length of token (in characters)
;
_get_token: LD C, 0 ; Initialise length
@@: LD A, (HL) ; Get the character from the parameter string
    OR A ; Exit if 0 (end of parameter string in MOS)
    RET Z
    CP 13 ; Exit if CR (end of parameter string in BBC BASIC)
    RET Z
    CP ' ' ; Exit if space (end of token)
    RET Z
    INC HL ; Advance to next character
    INC C ; Increment length
    JR @B
    
; Skip spaces in the parameter string
; Parameters:
; - HL: Address of parameter string
; Returns:
; - HL: Address of next none-space character
; F: Z if at end of string, otherwise NZ if there are more tokens to be parsed
;
_skip_spaces: LD A, (HL) ; Get the character from the parameter string 
    CP ' ' ; Exit if not space
    RET NZ
    INC HL ; Advance to next character
    JR _skip_spaces ; Increment length

; Storage for the argv array pointers
min_args: equ 1
argv_ptrs_max: EQU 16 ; Maximum number of arguments allowed in argv
argv_ptrs: BLKP argv_ptrs_max,0

; ========================================
; BEGIN APPLICATION CODE
; ========================================

; API INCLUDES
    include "fixed168.inc"

; APPLICATION INCLUDES
debug_print:
    call printDec
    ex de,hl
    call printDec
    ex de,hl
    call printNewLine
    ret

str_usage: ASCIZ "Usage: scratch <args>\r\n"
str_error: ASCIZ "Error!\r\n"
str_success: ASCIZ "Success!\r\n"

; ========= MAIN LOOP ========= 
; The main routine
; IXU: argv - pointer to array of parameters
; C: argc - number of parameters
; Returns:
; HL: Error code, or 0 if OK

; min_args: equ 3

_main_init:
    ld a,c ; how many arguments?
    cp min_args ; not enough?
    jr nc,main ; if enough, go to main loop
    ld hl,str_usage ; if not enough, print usage
    call printString
    ; fall through to _main_end_error

_main_end_error:
    ld hl,str_error ; print error message
    call printString
    ld hl,19 ; return error code 19
    ret

_main_end_ok:
    ; ld hl,str_success ; print success message
    ; call printString
    ld hl,0 ; return 0 for success
    ret

; ========= BEGIN CUSTOM MAIN LOOP =========
main:
    dec c ; decrement the argument count to skip the program name

; get first numeric argument
    call get_arg_s168 ; ud.e = x0
    ld (@arg1),de ; save x0
    call get_arg_s168 ; ud.e = y0
    ld (@arg2),de ; save y0

    ld hl,(@arg1) ; x0
    call print_s168
    ld hl,(@arg2) ; y0
    call print_s168

    ld bc,(@arg1) ; x0
    ld de,(@arg2) ; y0
    ld ix,0 ; x1
    ld iy,0 ; y1

    call distance168
    call printDec
    call printNewLine
    call printNewLine

    jp _main_end_ok ; return 0 for success
@arg1: dl 0
@arg2: dl 0

; ========== HELPER FUNCTIONS ==========
; get the next argument after ix as a signed 16.8 fixed point number
; inputs: ix = pointer to the argument string
; outputs: ude = signed 16.8 fixed point number
; destroys: a, d, e, h, l, f
get_arg_s168:
    lea ix,ix+3 ; point to the next argument
    ld hl,(ix) ; get the argument string
    call asc_to_s168 ; convert the string to a number
    ret ; return with the value in DE

; Inputs: ix = pointer to the argument string
; Outputs: ude = signed 24-bit integer
; Destroys: a, d, e, h, l, f
get_arg_s24:
    lea ix,ix+3 ; point to the next argument
    ld hl,(ix) ; get the argument string
    call asc_to_s24 ; convert the string to a number
    ret ; return with the value in DE

get_arg_text:
    lea ix,ix+3 ; point to the next argument
    ld hl,(ix) ; get the argument string
    ret

; match the next argument after ix to the dispatch table at iy
; - arguments and dispatch entries are zero-terminated, case-sensitive strings
; - final entry of dispatch table must be a 3-byte zero or bad things will happen
; returns: NO MATCH: iy=dispatch list terminator a=1 and zero flag reset
; ON MATCH: iy=dispatch address, a=0 and zero flag set
; destroys: a, hl, de, ix, iy, flags
match_next:
    lea ix,ix+3 ; point to the next argument
@loop:
    ld hl,(iy) ; pointer argument dispatch record
    sign_hlu ; check for list terminator
    jp z,@no_match ; if a=0, return error
    inc hl ; skip over jp instruction
    inc hl
    ld de,(ix) ; pointer to the argument string
    call str_equal ; compare the argument to the dispatch table entry
    jp z,@match ; if equal, return success
    lea iy,iy+3 ; if not equal, bump iy to next dispatch table entry
    jp @loop ; and loop 
@no_match:
    inc a ; no match so return a=1 and zero flag reset
    ret
@match:
    ld iy,(iy) ; get the function pointer
    ret ; return a=0 and zero flag set

; same as match_next, but prints the parameter if a match is found
match_next_and_print:
    call match_next
    ret nz ; no match found
    lea ix,ix-3 
    call get_arg_text ; hl points to the operator string
    call print_param
    ret

; compare two zero-terminated strings for equality, case-sensitive
; hl: pointer to first string, de: pointer to second string
; returns: z if equal, nz if not equal
; destroys: a, hl, de
str_equal:
    ld a,(de) ; get the first character
    cp (hl) ; compare to the second character
    ret nz ; if not equal, return
    or a
    ret z ; if equal and zero, return
    inc hl ; next character
    inc de
    jp str_equal ; loop until end of string

; print the parameter string pointed to by ix
; destroys: a, hl
print_param:
    ld hl,(ix) ; get the parameter pointer
    call printString ; print the parameter string
    ld a,' ' ; print a space separator
    rst.lil $10 
    ret

; print the parameters
; inputs: b = number of parameters, ix = pointer to the parameters
; destroys: a, hl, bc
print_params:
    ld b,c ; loop counter = number of parameters
    push ix ; save the pointer to the parameters
@loop:
    push bc ; save the loop counter
    call print_param ; print the parameter
    lea ix,ix+3 ; next parameter pointer
    pop bc ; get back the loop counter
    djnz @loop ; loop until done
    pop ix ; restore the pointer to the parameters
    ret
