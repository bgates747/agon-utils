;
; print a floating point number in decimal format
; inputs: HL'H'L'C is the number to print
; outputs: number printed to screen
;          STROUT null-terminated string representation of the number
; destroys: everything
print_float_dec:
    call STR ; convert the number to a string
    ld hl,ACCS ; point to the string accumulator
    call printString
    ret