    include "basic/ram.asm"
    include "basic/eval.asm"
    INCLUDE	"basic/equs.inc"
    INCLUDE "basic/macros.inc"
    include "basic/fpp.asm"
    include "basic/snippets.asm"
    include "basic/sorry.asm"

; -------------------- from basic/fpp.asm --------------------
;
;VAL - Return numeric value of string.
;Input: ASCII string at IX
;Result is variable type numeric.
;
;Function STR - convert numeric value to ASCII string.
;   Inputs: HLH'L'C = integer or floating-point number
;           DE = address at which to store string
;           IX = address of @% format control
;  Outputs: String stored, with NUL terminator


;NUMBER: Get unsigned integer from string.
;    Inputs: string at (IX)
;            C = truncated digit count
;                (initially zero)
;            B = total digit count
;            HLH'L' = initial value
;   Outputs: HLH'L' = number (binary integer)
;            A = delimiter.
;            B, C & IX updated
;  Destroys: A,B,C,D,E,H,L,B',C',D',E',H',L',IX,F
;

; -------------------- from basic/eval.asm --------------------
;
;Function STR - convert numeric value to ASCII string.
;   Inputs: HLH'L'C = integer or floating-point number.
;  Outputs: String in string accumulator.
;           E = length, D = ACCS/256
;           A = 80H (type=string)


;HEXSTR - convert numeric value to HEX string.
;   Inputs: HLH'L'C = integer or floating-point number
;  Outputs: String in string accumulator.
;           E = string length.  D = ACCS/256

; print a floating point number in decimal format
; inputs: HL'H'L'C is the number to print
; outputs: number printed to screen
;          STROUT null-terminated string representation of the number
; destroys: nothing
print_float_dec:
    PUSH_ALL
    ld ix,NUMF ; point to the format code buffer
    ld e,10 ; fractional digits
    ld (ix+1),e ; store the format code
    ld d,%000000010
    ld (ix+2),d ; store the format code
    ld de,STROUT ; point to the output buffer
    call STRING ; convert the number back to a string
    ld hl,STROUT ; point to the string output buffer
    call printString
    POP_ALL
    ret

; output buffer for strings from BASIC
STROUT: blkb 256,0
; numeric string format code
; byte 1 is the number of significant digits:
; -- up to 10
; -- 0 or > 10 defaults to max decimal notation
; -- if less than number of integer digits, output will be in E notation
; byte 2 bit 1 is E notation flag when set
; -- trailing zeros are added to bring number of significant digits to the specified number
NUMF: dl 0