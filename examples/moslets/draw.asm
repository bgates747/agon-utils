;
; Title:	test
; Author:	Brandon Gates
; Created:	29/10/2024

    ASSUME	ADL = 1			
    INCLUDE "mos_api.inc"
    ORG 0x0B0000 ; Is a moslet

    MACRO PROGNAME
    ASCIZ "draw.bin"
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

; APPLICATION INCLUDES
str_usage: ASCIZ "Usage: draw <args>\r\n"
str_error: ASCIZ "Error!\r\n"
str_success: ASCIZ "Success!\r\n"

; This is a toy program for basic graphics drawing from the the MOS CLI.
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
    ld hl,str_success   ; print success message
    call printString
    ld hl,0             ; return 0 for success
    ret

; ========= BEGIN CUSTOM MAIN LOOP =========
main:
    dec c               ; decrement the argument count to skip the program name

; get the first argument, which determines the drawing operation to perform
    ld iy,arg1          ; pointer to first argument dispatch table
    call match_next      ; look for a matching argument
    jp nz,_main_end_error; if no match, return error
    callIY              ; if match, call the function at IY
    ret                 ; return to MOS with success or error code

; ========= BEGIN ARGUMENT-SPECIFIC FUNCTIONS =========
; --------- arg1 is the drawing operation to perform ---------
arg1:
    dl move
    dl line
    dl 0x000000 ; list terminator

; --------- move the graphics cursor to the specified coordinates ---------
move:
    jr @start
    asciz "move"
@start:
    call get_move_type ; get the move type from arg2
    push af ; save it
    call get_plot_coords ; get the move coordinates from arg3 and arg4
    pop af ; restore the move type
    call vdu_plot ; move the gfx curor to the specified coordinates
    jp _main_end_ok

move_type:
    dl abs
    dl rel
    dl 0x000000 ; list terminator
abs:
    jr @start
    asciz "abs"
@start:
    ld a,mv_abs
    ret
rel:
    jr @start
    asciz "rel"
@start:
    ld a,mv_rel
    ret

get_move_type:
    ld iy,move_type
    call match_next
    jp nz,_main_end_error
    callIY ; a comes back with move type
    ret

; --------- draw a line from the current cursor position to the specified coordinates ---------
line:
    jr @start
    asciz "line"
@start:
    call get_move_type ; get the move type from arg2
    inc a ; TEMPORARY: sets draw effect to foreground color
    push af ; save it
    call get_plot_coords ; get the move coordinates from arg3 and arg4
    pop af ; restore the move type
    call vdu_plot ; move the gfx curor to the specified coordinates
    jp _main_end_ok

get_plot_coords:
; get the move coordinates
    lea ix,ix+3 ; pointer to next argument address
    ld hl,(ix)  ; pointer to the x coordinate string
    call ASC_TO_NUMBER ; de = x coordinate
    push de
    pop bc ; bc = x coordinate
    lea ix,ix+3 ; pointer to next argument address
    ld hl,(ix)  ; pointer to the y coordinate string
    call ASC_TO_NUMBER ; de = y coordinate
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