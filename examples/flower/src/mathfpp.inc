; integer operations		
iand:	EQU 0x00	; AND (INTEGER)
ibdiv:	EQU 0x01	; DIV
ieor:	EQU 0x02	; EOR
imod:	EQU 0x03	; MOD
ior:	EQU 0x04	; OR
ile:	EQU 0x05	; <=
ine:	EQU 0x06	; <>
ige:	EQU 0x07	; >=
ilt:	EQU 0x08	; <
ieq:	EQU 0x09	; =
imul:	EQU 0x0A	; *
iadd:	EQU 0x0B	; +
igt:	EQU 0x0C	; >
isub:	EQU 0x0D	; -
ipow:	EQU 0x0E	; ^
idiv:	EQU 0x0F	; /
;		
; floating point functions		
absv:	EQU 0x00	; ABS
acs:	EQU 0x01	; ACS
asn:	EQU 0x02	; ASN
atn:	EQU 0x03	; ATN
cos:	EQU 0x04	; COS
deg:	EQU 0x05	; DEG
exp:	EQU 0x06	; EXP
int_:	EQU 0x07	; INT
ln:	EQU 0x08	; LN
log:	EQU 0x09	; LOG
notk:	EQU 0x0A	; NOT
rad:	EQU 0x0B	; RAD
sgn:	EQU 0x0C	; SGN
sin:	EQU 0x0D	; SIN
sqr:	EQU 0x0E	; SQR
tan:	EQU 0x0F	; TAN
zero:	EQU 0x10	; ZERO
fone:	EQU 0x11	; FONE
true:	EQU 0x12	; TRUE
pi:	EQU 0x13	; PI
val:	EQU 0x14	; VAL
str:	EQU 0x15	; STR$
sfix:	EQU 0x16	; FIX
sfloat:	EQU 0x17	; FLOAT
ftest:	EQU 0x18	; TEST
fcomp:	EQU 0x19	; COMPARE
;		
; floating point operations		
fand:	EQU 0x00	; AND (FLOATING-POINT)
fbdiv:	EQU 0x01	; DIV
feor:	EQU 0x02	; EOR
fmod:	EQU 0x03	; MOD
ffor:	EQU 0x04	; OR
fle:	EQU 0x05	; <=
fne:	EQU 0x06	; <>
fge:	EQU 0x07	; >=
flt:	EQU 0x08	; <
feq:	EQU 0x09	; =
fmul:	EQU 0x0A	; *
fadd:	EQU 0x0B	; +
fgt:	EQU 0x0C	; >
fsub:	EQU 0x0D	; -
fpow:	EQU 0x0E	; ^
fdiv:	EQU 0x0F	; /