iand: equ 0
ibdiv: equ 1
ieor: equ 2
imod: equ 3
ior: equ 4
ile: equ 5
ine: equ 6
ige: equ 7
ilt: equ 8
ieq: equ 9
imul: equ 10
iadd: equ 11
igt: equ 12
isub: equ 13
ipow: equ 14
idiv: equ 15
absv: equ 16
acs: equ 17
asn: equ 18
atn: equ 19
cos: equ 20
deg: equ 21
exp: equ 22
int_: equ 23
ln: equ 24
log: equ 25
notk: equ 26
rad: equ 27
sgn: equ 28
sin: equ 29
sqr: equ 30
tan: equ 31
fpzero: equ 32
fone: equ 33
true: equ 34
pi: equ 35
val: equ 36
string: equ 37
sfix_fp: equ 38
sfloat: equ 39
ftest: equ 40
fcomp: equ 41
fand: equ 42
fbdiv: equ 43
feor: equ 44
fmod: equ 45
ffor: equ 46
fle: equ 47
fne: equ 48
fge: equ 49
flt: equ 50
feq: equ 51
fmul: equ 52
fadd: equ 53
fgt: equ 54
fsub: equ 55
fpow: equ 56
fdiv: equ 57

; -------------------- from basic/fpp.asm --------------------


;Function STRING - convert numeric value to ASCII string.
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

;VAL - Return numeric value of string.
;Input: ASCII string at IX
;Result is variable type numeric.

;SWAP_FP - Swap arguments.
;    Exchanges DE,HL D'E',H'L' and B,C
;    Destroys: A,B,C,D,E,H,L,D',E',H',L'
;SWAP1 - Swap DEHL with D'E'H'L'
;    Destroys: D,E,H,L,D',E',H',L'


;
;IADD - Integer addition.
;FADD - Floating point addition with rounding.
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



; ==================== CONVENIENCE FUNCTIONS ====================
;
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

; num1: blkb 6,0
; num2: blkb 6,0
; ; store HLH'L'C in num1
; store1:
;     push ix
;     ld ix,num1
;     exx
;     ld (ix+0),c
;     ld (ix+1),l
;     ld (ix+2),h
;     exx
;     ld (ix+3),l
;     ld (ix+4),h

;     call debug_print
;     push hl
;     ld hl,num1
;     ld a,6
;     call dumpMemoryHex
;     pop hl

;     pop ix
;     ret

; get1:
;     push ix
;     ld ix,num1
;     exx
;     ld c,(ix+0)
;     ld l,(ix+1)
;     ld h,(ix+2)
;     exx
;     ld l,(ix+3)
;     ld h,(ix+4)
;     pop ix
;     ret

; ; store DED'E'B in num2
; store2:
;     push ix
;     ld ix,num2
;     exx
;     ld (ix+0),b
;     ld (ix+1),e
;     ld (ix+2),d
;     exx
;     ld (ix+3),e
;     ld (ix+4),d

;     call debug_print
;     push hl
;     ld hl,num2
;     ld a,6
;     call dumpMemoryHex

;     pop ix
;     ret

; ; get DED'E'B from num2
; get2:
;     push ix
;     ld ix,num2
;     exx
;     ld b,(ix+0)
;     ld e,(ix+1)
;     ld d,(ix+2)
;     exx
;     ld e,(ix+3)
;     ld d,(ix+4)
;     pop ix
;     ret