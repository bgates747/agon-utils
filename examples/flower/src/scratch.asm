;
; Title:	test
; Author:	Brandon Gates
; Created:	29/10/2024

    ASSUME	ADL = 1			
    INCLUDE "mos_api.inc"
    ORG 0x0B0000 ; Is a moslet

    MACRO PROGNAME
    ASCIZ "scratch.bin"
    ENDMACRO

; STANDARD MOSLET INCLUDES
    include "init.inc"
    include "parse.inc"

; API INCLUDES
    include "functions.inc"
    include "maths.inc"
	INCLUDE	"arith24.inc"
    include "trig24.inc"
    include "files.inc"
    include "timer.inc"
    include "vdu.inc"
    ; include "vdu_fonts.inc"
    include "vdu_plot.inc"

; SHAWN'S INCLUDES
	INCLUDE	"strings24.asm"

; APPLICATION INCLUDES
str_usage: ASCIZ "Usage: scratch <args>\r\n"
str_error: ASCIZ "Error!\r\n"
str_success: ASCIZ "Success!\r\n"

; This is a scratch moslet for testing new features
; Parameters:
;

; ========= BOILERPLATE MAIN LOOP ========= 
; The main routine
; IXU: argv - pointer to array of parameters
;   C: argc - number of parameters
; Returns:
;  HL: Error code, or 0 if OK

min_args: equ 2

_main_init:
    ld a,c              ; how many arguments?
    cp min_args         ; not enough?
    jr nc,main          ; if enough, go to main loop
    ld hl,str_usage     ; if not enough, print usage
    call printString
                        ; fall through to _main_end_error

_main_end_error:
    ld hl,str_error     ; print error message
    call printString
    ld hl,19            ; return error code 19
    ret

_main_end_ok:
    ; ld hl,str_success   ; print success message
    ; call printString
    ld hl,0             ; return 0 for success
    ret

; ========= BEGIN CUSTOM MAIN LOOP =========
main:
    dec c               ; decrement the argument count to skip the program name

    jp test_smul168

test_sdiv168:
    call get_arg_s168 ; get the dividend
    push de
    ex de,hl
    call print_s168

    call get_arg_s168 ; get the divisor
    ex de,hl
    call print_s168
    call printNewLine
    ex de,hl ; de = divisor
    pop hl ; hl = dividend

    call sdiv168 ; de = quotient, hl = remainder
    ex de,hl ; hl = quotient, de = remainder
    call print_s168
    ex de,hl ; de = quotient, hl = remainder
    call print_s168
    call printNewLine
    call printNewLine

    jp _main_end_ok

test_smul168:
    call get_arg_s168 ; get the dividend
    push de
    ex de,hl
    call print_s168

    call get_arg_s168 ; get the divisor
    ex de,hl
    call print_s168
    call printNewLine
    ex de,hl ; de = divisor
    pop hl ; hl = dividend

    call smul168 ; hl = product
    call print_s168
    call printNewLine
    call printNewLine

    jp _main_end_ok

test_udiv168:
    call get_arg_s168 ; get the dividend
    push de
    ex de,hl
    call print_s168

    call get_arg_s168 ; get the divisor
    ex de,hl
    call print_s168
    call printNewLine
    ex de,hl ; de = divisor
    pop hl ; hl = dividend

    call udiv168 ; de = quotient, hl = remainder
    ex de,hl ; hl = quotient, de = remainder
    call print_s168
    ex de,hl ; de = quotient, hl = remainder
    call print_s168
    call printNewLine

    jp _main_end_ok

test_udiv24:
; get dividend
    call get_arg_s24
    push de
    ex de,hl
    call print_u24
; get divisor
    call get_arg_s24
    ex de,hl
    call print_u24
    ex de,hl
    call printNewLine
    pop hl

; do the division
    call udiv24 ; de = quotient, hl = remainder
    ex de,hl ; hl = quotient, de = remainder
    call dumpRegistersHex
    call print_u24
    ex de,hl ; de = quotient, hl = remainder
    call print_u24

    jp _main_end_ok
@scratch: ds 4

test_umul168:
    call get_arg_s168
    push de
    ex de,hl
    call print_s168

    call get_arg_s168
    push de
    ex de,hl
    call print_s168

    pop hl
    pop de
    call umul168
    call print_s168
    call printNewLine
    call printNewLine

    jp _main_end_ok

test_umul24x24:
    call get_arg_s24
    push de
    call get_arg_s24
    pop hl

    ; call dumpRegistersHex
    call umul24x24

    ld hl,(umulfxout+3)
    call printHexUHL

    ld hl,(umulfxout+0)
    call printHexUHL
    call printNewLine

    jp _main_end_ok

test_umul24x8:
; 24-bit argument to BHL
    call get_arg_s24
    ex de,hl
    HLU_TO_A
    ld b,a ; b = high 8-bits
    push hl ; store low 16-bits, b will be fine

; 8-bit argument to A TODO: write an 8-bit argument parser for performance
    call get_arg_s24
    ld a,e ; 8-bit argument
    pop hl ; bhl is the 24-bit argument

; do the multiplication
    call umul24x8
    call printHexABHL
    call printNewLine
    jp _main_end_ok

test_scratch:
    call get_arg_s24
    ex de,hl
    HLU_TO_A
    ; call dumpRegistersHex
    call printNewLine
    jp _main_end_ok

test_deg_360_to_256:
    call get_arg_s168 ; argument value to de
    ex de,hl             ; argument to hl for function call
    call deg_360_to_256
    ; call dumpRegistersHex
    call print_s168
    call printNewLine
    jp _main_end_ok

; ========== HELPER FUNCTIONS ==========
; get the next argument after ix as a signed 16.8 fixed point number
; inputs: ix = pointer to the argument string
; outputs: ude = signed 16.8 fixed point number
; destroys: a, d, e, h, l, f
get_arg_s168:
    lea ix,ix+3 ; point to the next argument
    ld hl,(ix)  ; get the argument string
    call asc_to_s168 ; convert the string to a number
    ret ; return with the value in DE

; Inputs: ix = pointer to the argument string
; Outputs: ude = signed 24-bit integer
; Destroys: a, d, e, h, l, f
get_arg_s24:
    lea ix,ix+3 ; point to the next argument
    ld hl,(ix)  ; get the argument string
    call asc_to_s24 ; convert the string to a number
    ret ; return with the value in DE

get_plot_coords:
; get the move coordinates
    lea ix,ix+3 ; pointer to next argument address
    ld hl,(ix)  ; pointer to the x coordinate string
    call asc_to_s168 ; de = x coordinate
    push de
    pop bc ; bc = x coordinate
    lea ix,ix+3 ; pointer to next argument address
    ld hl,(ix)  ; pointer to the y coordinate string
    call asc_to_s168 ; de = y coordinate
    ret

; match the next argument after ix to the dispatch table at iy
;   - arguments and dispatch entries are zero-terminated, case-sensitive strings
;   - final entry of dispatch table must be a 3-byte zero or bad things will happen
; returns: NO MATCH: iy=dispatch list terminator a=1 and zero flag reset
;          ON MATCH: iy=dispatch address, a=0 and zero flag se
; destroys: a, hl, de, ix, iy, flags
match_next:
    lea ix,ix+3         ; point to the next argument
@loop:
    ld hl,(iy)          ; pointer argument dispatch record
    sign_hlu            ; check for list terminator
    jp z,@no_match      ; if a=0, return error
    inc hl              ; skip over jp instruction
    inc hl
    ld de,(ix)          ; pointer to the argument string
    call str_equal      ; compare the argument to the dispatch table entry
    jp z,@match         ; if equal, return success
    lea iy,iy+3         ; if not equal, bump iy to next dispatch table entry
    jp @loop            ; and loop 
@no_match:
    inc a               ; no match so return a=1 and zero flag reset
    ret
@match:
    ld iy,(iy)          ; get the function pointer
    ret                 ; return a=0 and zero flag set

; compare two zero-terminated strings for equality, case-sensitive
; hl: pointer to first string, de: pointer to second string
; returns: z if equal, nz if not equal
; destroys: a, hl, de
str_equal:
    ld a,(de)           ; get the first character
    cp (hl)             ; compare to the second character
    ret nz              ; if not equal, return
    or a
    ret z               ; if equal and zero, return
    inc hl              ; next character
    inc de
    jp str_equal        ; loop until end of string

; print the parameter string pointed to by ix
; destroys: a, hl
print_param:
    ld hl,(ix)          ; get the parameter pointer
    call printString    ; print the parameter string
    ld a,' '            ; print a space separator
    rst.lil $10         
    ret

; print the parameters
; inputs: b = number of parameters, ix = pointer to the parameters
; destroys: a, hl, bc
print_params:
    ld b,c              ; loop counter = number of parameters
    push ix             ; save the pointer to the parameters
@loop:
    push bc             ; save the loop counter
    call print_param    ; print the parameter
    lea ix,ix+3         ; next parameter pointer
    pop bc              ; get back the loop counter
    djnz @loop          ; loop until done
    pop ix              ; restore the pointer to the parameters
    ret

debug_print:
    call printNewLine   ; DEBUG
    call dumpFlags      ; DEBUG
    call print_param    ; DEBUG
    call printNewLine   ; DEBUG
    call printNewLine   ; DEBUG
    ret