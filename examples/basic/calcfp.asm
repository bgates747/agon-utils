;
; Title:	test
; Author:	Brandon Gates
; Created:	29/10/2024

    ASSUME	ADL = 1			
    INCLUDE "mos_api.inc"
    ORG 0x0B0000 ; Is a moslet

    MACRO PROGNAME
    ASCIZ "calcfp.bin"
    ENDMACRO

; STANDARD MOSLET INCLUDES
    include "init.inc"
    include "parse.inc"

; APPLICATION INCLUDES
    include "calcfp.inc"

; APPLICATION INCLUDES
str_usage: ASCIZ "Usage: scratch <args>\r\n"
str_error: ASCIZ "Error!\r\n"
str_success: ASCIZ "Success!\r\n"

; This is a scratch moslet for testing new features
; Parameters:
;

; The main routine
; IXU: argv - pointer to array of parameters
;   C: argc - number of parameters
; Returns:
;  HL: Error code, or 0 if OK

min_args: equ 3

_main:
    ld a,c              ; how many arguments?
    cp min_args         ; not enough?
    jr nc,main          ; if enough, go to main loop

_main_end_error:
    ld hl,19            ; return error code 19
    ret

_main_end_ok:
    ld hl,0             ; return 0 for success
    ret

; ========= BEGIN CUSTOM MAIN LOOP =========
main:
    dec c               ; decrement the argument count to skip the program name

    jp _main_end_ok     ; return success