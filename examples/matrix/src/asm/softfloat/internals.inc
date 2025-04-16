; #define signF16UI( a ) ((bool) ((uint16_t) (a)>>15))
; #define expF16UI( a ) ((int_fast8_t) ((a)>>10) & 0x1F)
; #define fracF16UI( a ) ((a) & 0x03FF)
; inputs: hl is the float16 to unpack
; outputs: c is the sign (0=pos,1=neg), b is the biased exponent, hl is the normalised mantissa
;          sign and zero flags are correctly (re)set, carry set if hl is +/-zero
; destroys: a
softfloat16_unpack:
; set sign
    ld a,h
    and %10000000
    ld c,a ; sign
; get hl's stored exponent and shift down twice
    ld a,h
    rrca
    rrca
    and %00011111
    ld b,a ; biased exponent
    or a ; check for zero
    jr nz,@check_special ; non-zero exponent means normal number
; check for zero or -zero
    res 7,h ; clear sign bit
    SIGN_HL
    jr z,@is_zero ; result is zero so nothing more to do
@is_sub:
    call softfloat_normSubnormalF16Sig ; number is subnormal
    ld a,c ; get sign
    or a ; (re)set sign flag and clear carry indicating non-zero result    
    ret
@check_special:
; Check for special values - infinity and NaN
    cp 0x1F ; Is exponent 0x1F?
    jr nz,@is_nor ; non-zero exponent means normal number
; mask out everything but the top tw bits of hl's mantissa
    ld a,h
    and %00000011
    ld h,a
    or a ; reset carry indicating non-zero result
    ret
@is_nor: 
; put the explicit 1 into the mantissa and (re)set sign flag
    set 2,h
    SIGN_HL
; mask out everything but the top three bits of hl's mantissa
    ld a,h
    and %00000111
    ld h,a
    or a ; reset carry indicating non-zero result
    ret
@is_zero:
    ld a,c ; get sign
    or a ; (re)set sign flag 
    scf ; set carry indicating zero result
    ret
; end softfloat16_unpack


; #define packToF16UI( sign, exp, sig ) (((uint16_t) (sign)<<15) + ((uint16_t) (exp)<<10) + (sig))
; inputs: c = sign (0=pos, 0x80=neg), b = exp, hl = sig (implied 1 place in bit 10)
packToF16UI:
; exponent
    ld a,b
    add a,a
    add a,a
    add a,h
    ld h,a
; sign
    ld a,c
    or h
    ld h,a
; extract exponent
    rra
    rra
    and %00011111
    ld b,a
    ret
; end packToF16UI

; #define isNaNF16UI( a ) (((~(a) & 0x7C00) == 0) && ((a) & 0x03FF))