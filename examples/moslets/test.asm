;
; Title:	test
; Author:	Brandon Gates
; Created:	29/10/2024

    ASSUME	ADL = 1			
    INCLUDE "mos_api.inc"
    ORG 0x0B0000 ; Is a moslet

    MACRO PROGNAME
    ASCIZ "test.bin"
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


; This is a test program that may do nothing useful.
; Parameters:
;

; ========= BOILERPLATE MAIN LOOP ========= 
str_usage: ASCIZ "Usage: test <args>\r\n"
str_error: ASCIZ "Error: Args don't match\r\n"
str_success: ASCIZ "Success: Argument found\r\n"

; The main routine
; IXU: argv - pointer to array of parameters
;   C: argc - number of parameters
; Returns:
;  HL: Error code, or 0 if OK
;
min_args: equ 2

_main:
    push bc             ; save the count
    ld a,c              ; how many arguments?
    cp min_args         ; not enough?
    jr nc,main          ; if enough, go to main loop
    ld hl,str_usage     ; if not enough, print usage
    call printString
    pop bc              ; dummy pop to balance stack
    ld hl,19            ; return error code 19
    ret
    
_main_end:
; End with no error
    ld hl,0
    ret

main:
    pop bc              ; restore the count
    ld b,C              ; b is the loop counter
    dec b               ; skip the program name and ..
    lea ix,ix+3         ; .. point to the real first argument
; --------- BEGIN CUSTOM MAIN LOOP ---------
    ld iy,print_success ; pointer to a subroutine
    callIY
; --------- END CUSTOM MAIN LOOP ---------
    JP _main_end         ; end of program
; ========= END BOILERPLATE MAIN LOOP ========= 

print_success:
    ld hl,str_success
    call printString
    call printNewLine
    ret

; read the numeric value in arg1, print it to decimal, and determine its sign
    ld hl,(ix)
    call ASC_TO_NUMBER
    ex de,hl
    call printDec
    call printNewLine
    signHL
    call dumpFlags
    call printNewLine
