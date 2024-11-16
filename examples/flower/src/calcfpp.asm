;
; Title:	test
; Author:	Brandon Gates
; Created:	29/10/2024

    ASSUME	ADL = 1			
    INCLUDE "mos_api.inc"
    ORG 0x0B0000 ; Is a moslet

    MACRO PROGNAME
    ASCIZ "calcfpp"
    ENDMACRO

; STANDARD MOSLET INCLUDES
    include "init.inc"
    include "parse.inc"

; API INCLUDES
    include "functions.inc"
    include "maths.inc"
	INCLUDE	"arith24.inc"
    include "fixed24.inc"
    include "trig24.inc"
    include "files.inc"
    include "timer.inc"
    include "vdu.inc"
    ; include "vdu_fonts.inc"
    include "vdu_plot.inc"

; SHAWN'S INCLUDES
	INCLUDE	"strings24.asm"

; BASIC FLOATING POINT FUNCTIONS
    include "mathfpp.inc"

; APPLICATION INCLUDES
str_usage: ASCIZ "Usage: scratch <args>\r\n"
str_error: ASCIZ "Error!\r\n"
str_success: ASCIZ "Success!\r\n"

; ========= MAIN LOOP ========= 
; The main routine
; IXU: argv - pointer to array of parameters
;   C: argc - number of parameters
; Returns:
;  HL: Error code, or 0 if OK

min_args: equ 3

arg1: ASCIZ "65535.275"
arg2: ASCIZ "32767.667"

_main:
; TEMP DEBUG CODE

    call printInline
    ASCIZ "Hello, world!\r\n"

    ; call printNewLine
    ; ld hl,arg1
    ; call dumpRegistersHex
    ; call printString
    ; call printNewLine
    ; call dumpRegistersHex


; ; this works
;     call printNewLine

;     ld iy,arg1
;     call EXPR
;     call dumpRegistersHexAll
;     call print_float_dec
;     call printNewLine
;     CALL PUSH5

;     ld iy,arg2
;     call EXPR
;     call dumpRegistersHexAll
;     call print_float_dec
;     call printNewLine

;     CALL POP5
;     call dumpRegistersHexAll
;     call FADD
;     call dumpRegistersHexAll
;     call print_float_dec
;     call printNewLine
    
    jp _main_end_ok

; END TEMP DEBUG CODE
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
    ld hl,str_success   ; print success message
    call printString
    ld hl,0             ; return 0 for success
    ret

; ========= BEGIN CUSTOM MAIN LOOP =========
main:
    dec c               ; decrement the argument count to skip the program name
    ; call debug_print

; match on BASIC functions
    ld iy,BASIC
    call match_next_and_print ; iy = function pointer, zero flag set if match
    jp z,BASIC_EXEC
@@:
    lea ix,ix-3

    ; call debug_print

    
; get first numeric argument
    call get_arg_float ; HLH'L'C = arg1
    call print_float_dec

    ; call debug_print

    ; call store1
    call PUSH5

    ; call debug_print


; match on single number functions
    ld iy,function
    call match_next_and_print ; iy = function pointer, zero flag set if match
    jp z,@execute

; match on two-number operators
    lea ix,ix-3
    ld iy,operator
    ; call debug_print
    call match_next_and_print ; iy = operator pointer, zero flag set if match
    ; call printNewLine
    ; call dumpFlags
    ; call debug_print
    jp nz,_main_end_error

; get second numeric argument if needed
    call get_arg_float ; HLH'L'C = arg2
    call print_float_dec
    ; call SWAP_FP ; DED'E'B = arg2
    ; call store2
    ; fall through to @execute

@execute:
    callIY ; call the function
    call printNewLine
    call printNewLine
    jp _main_end_ok

; ========== DISPATCH TABLES ==========
; BASIC FUNCTIONS
BASIC_EXEC:
    jp nz,_main_end_error

    callIY ; call the function
    call printNewLine
    jp _main_end_ok

BASIC:
    dl val
    dl 0x000000 ; list terminator
val:
    jr @start
    asciz "val"
@start:
    call get_arg_float 
    call print_float_dec
    call printNewLine
    ret

; TWO-NUMBER OPERATORS
operator:
    dl addition
    dl subtract
    dl multiply
    dl divide
    dl tan
    dl atan2
    dl polar2cart
    dl cart2polar
    dl shift
    dl 0x000000 ; list terminator
addition:
    jr @start
    asciz "+"
@start: 
    call POP5 ; DED'E'B = arg1
    call FADD ; HLH'L'C + DED'E'B --> HLH'L'C
    ld a,'='
    rst.lil $10
    call print_float_dec
    ret
subtract:
    jr @start
    asciz "-"
@start:
    call POP5 ; DED'E'B = arg1
    call SWAP ; HLH'L'C <--> DED'E'B
    call FSUB ; HLH'L'C - DED'E'B --> HLH'L'C
    ld a,'='
    rst.lil $10
    call print_float_dec
    ret
multiply:
    jr @start
    asciz "*"
@start:
    ld a,8 ; 8 fractional bits output
    ld b,8 ; 8 fractional bits input arg1
    ld c,8 ; 8 fractional bits input arg2
    call smulfx ; hl = hl * de
    call print_hex_hl
    call print_s168_hl
    ret
divide:
    jr @start
    asciz "/"
@start:
    call sdiv168
    call print_hex_de
    call print_s168_de
    call print_hex_hl ; remainder
    call print_s168_hl ; remainder
    ret
tan:
    jr @start
    asciz "tan"
@start:
    ; call tan168
    ret
atan2:
    jr @start
    asciz "atan2"
@start:
    ; call atan2_168
    ret
polar2cart:
    jr @start
    asciz "polar2cart"
@start:
    call deg_360_to_256
    call print_hex_hl
    call print_s168_hl
    call polar_to_cartesian
    call printNewLine
    call print_hex_bc
    call print_s168_bc
    call print_hex_de
    call print_s168_de
    ret
cart2polar:
    jr @start
    asciz "cart2polar"
@start:
    ; call cartesian_to_polar
    ret

function:
    dl sin
    dl cos
    dl sqrt
    dl deg256
    dl 0x000000 ; list terminator
sin:
    jr @start
    asciz "sin"
@start:
    call deg_360_to_256
    call print_hex_hl
    call print_s168_hl
    call sin168
    call print_hex_hl
    call print_s168_hl
    ret
cos:
    jr @start
    asciz "cos"
@start:
    call deg_360_to_256
    call print_hex_hl
    call print_s168_hl
    call cos168
    call print_hex_hl
    call print_s168_hl
    ret
sqrt:
    jr @start
    asciz "sqrt"
@start:
    call sqrt168
    call print_s168_hl
    ret
deg256:
    jr @start
    asciz "deg256"
@start:
    call deg_360_to_256
    call print_hex_hl
    call print_s168_hl
    ret
shift:
    jr @start
    asciz "shift"
@start:
    ld ix,arith24uhl ; pointer to output buffer
    ld a,d ; integer portion of ude is number of bits to shift
    call shift_hlu
    call print_hex_hl
    call print_s168_hl
    ret

; ========== HELPER FUNCTIONS ==========
; get the next argument after ix as a floating point number
; inputs: ix = pointer to the argument string
; outputs: HLH'L'C = floating point number, ix points to the next argument
; destroys: everything except iy, including prime registers
get_arg_float:
    lea ix,ix+3 ; point to the next argument
    push ix ; preserve
    ld ix,(ix)  ; point to argument string
    call VAL ; convert the string to a float
    pop ix ; restore
    ret ; return with the value in HLH'L'C

; get the next argument after ix as a string
; inputs: ix = pointer to the argument string
; outputs: HL = pointer to the argument string, ix points to the next argument
; destroys: a, h, l, f
get_arg_text:
    lea ix,ix+3 ; point to the next argument
    ld hl,(ix)  ; get the argument string
    ret

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
;          ON MATCH: iy=dispatch address, a=0 and zero flag set
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
    call printNewLine
    call dumpRegistersHexAll
    call printNewLine
    ret

