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
    include "files.inc"
    include "timer.inc"
    include "vdu.inc"
    ; include "vdu_fonts.inc"
    include "vdu_plot.inc"

; SHAWN'S INCLUDES
	INCLUDE	"strings24.asm"
	INCLUDE	"arith24.asm"

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

_main:
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

test_udiv24:
; get dividend
    call get_arg_s24 
    push de
; get divisor
    call get_arg_s24 
    pop hl ; dividend (was de)
    call dumpRegistersHex
; do the division
    call udiv24 ; ude = uhl / ude rem uhl
    ex de,hl    ; uhl = uhl / ude rem de
    call dumpRegistersHex
    call print_u24
    call printNewLine
    jp _main_end_ok

test_div_24:
; get dividend
    call get_arg_s24 
    push de
; get divisor
    call get_arg_s24 
    pop bc ; dividend to bc (was de)
    call dumpRegistersHex
; do the division
    call div_24 ; uh.l = ub.c / ud.e
    call dumpRegistersHex
    call print_u24
    call printNewLine
    jp _main_end_ok

; inputs: b.c is 8.8 dividend, ud.e is 16.8 divisor
; outputs: uh.l is the 16.8 quotient ub.c is the 16.8 remainder
; destroys: a,bc
test_sdiv168:
; get dividend
    call get_arg_s168 
    push de
; get divisor
    call get_arg_s168 
    pop bc ; dividend to bc (was de)
; do the division
    call sdiv168 ; uh.l = ub.c / ud.e
    call dumpRegistersHex
    call print_s168
    call printNewLine
    jp _main_end_ok

test_deg_360_to_255:
    call get_arg_s168 ; argument value to de
    ex de,hl             ; argument to hl for function call
    call deg_360_to_255
    call dumpRegistersHex
    call print_s168
    call printNewLine
    jp _main_end_ok

; ========== HELPER FUNCTIONS ==========
get_arg_s168:
    lea ix,ix+3 ; point to the next argument
    ld hl,(ix)  ; get the argument string
    call asc_to_s168 ; convert the string to a number
    ret ; return with the value in DE

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
    signHL              ; check for list terminator
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