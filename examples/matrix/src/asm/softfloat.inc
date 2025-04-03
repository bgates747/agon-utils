; #define signF16UI( a ) ((bool) ((uint16_t) (a)>>15))
; #define expF16UI( a ) ((int_fast8_t) ((a)>>10) & 0x1F)
; #define fracF16UI( a ) ((a) & 0x03FF)
; #define packToF16UI( sign, exp, sig ) (((uint16_t) (sign)<<15) + ((uint16_t) (exp)<<10) + (sig))
; #define isNaNF16UI( a ) (((~(a) & 0x7C00) == 0) && ((a) & 0x03FF)); unpack the sign, exponent, and mantissa of a float16
;
; inputs: hl is the float16 to unpack
; outputs: a is the true exponent, hl is the normalised mantissa
;          sign and zero flags are correctly (re)set, carry set if hl is +/-zero
softfloat16_unpack:
; get hl's stored exponent
    ld a,h
    and %01111100
    jr nz,@is_nor ; non-zero exponent means normal number
; check for zero or -zero
    SIGN_HL ; get the 16-bit sign of hl
    scf ; assume zero result
    ret z ; result is zero so nothing more to do
    or l ; test l for zero (a is zero)
    jr nz,@is_sub ; number is subnormal
    ld a,h
    add a,a ; sets carry and zero flags if hl is -zero
    ret z ; result is -zero so nothing more to do
@is_sub:
    res 7,h ; clear sign bit
    call softfloat_normSubnormalF16Sig ; number is subnormal
    or a ; clear carry indicating non-zero result
    ret
@is_nor: ; compute hl's true exponent
    srl a
    srl a
    sub a,15
; put the explicit 1 into the mantissa and (re)set sign flag
    set 2,h
    SIGN_HL
    push af ; stack sign the true exponent
; mask out everything but the top three bits of hl's mantissa
    ld a,h
    and %00000111
    ld h,a
    pop af ; restore the true exponent
    scf ; set carry ...
    ccf ; ... then reset it indicating non-zero result
    ret
; end softfloat16_unpack

; INLINE uint_fast8_t softfloat_countLeadingZeros16( uint16_t a )
;     { return a ? __builtin_clz( a ) - 16 : 16; }
; #define softfloat_countLeadingZeros16 softfloat_countLeadingZeros16

; struct exp8_sig16 softfloat_normSubnormalF16Sig( uint_fast16_t sig )
; {
;     int_fast8_t shiftDist;
;     struct exp8_sig16 z;

;     shiftDist = softfloat_countLeadingZeros16( sig ) - 5;
;     z.exp = 1 - shiftDist;
;     z.sig = sig<<shiftDist;
;     return z;

; }
softfloat_normSubnormalF16Sig:
    ld a,1 ; set exponent to zero
@norm_loop:
    add hl,hl ; shift left
    dec a ; decrement exponent
    bit 2,h ; test for carry into assumed 1 place
    ret nz
    jr @norm_loop
; end softfloat_normSubnormalF16Sig

; Description:
;   Performs a logical right shift of a 32-bit value with jamming.
;
; Inputs: HLDE = 32-bit unsigned integer to shift (most to least significant byte)
;          A = number of bits to shift right (0–255, only 0–31 meaningful)
;
; Outputs: HLDE = shifted result, with LSB jammed (bit 0 set) if any 1s were shifted out
;          A = jam bit (0 or 1)
; destroys: b

softfloat_shiftRightJam32:
    ld b,a ; loop counter
    xor a ; zero jam bits and clear carry
@shift_loop:
    srl h
    srl l
    srl d
    srl e
    adc a,a ; jam bit
    or a ; clear carry
    djnz @shift_loop
    and %00000001 ; mask out all but the jam bit
    or a,e
    ld e,a ; jam bit to LSB
    ret

; float16_t f16_mul( float16_t a, float16_t b )
; {
;     union ui16_f16 uA;
;     uint_fast16_t uiA;
;     bool signA;
;     int_fast8_t expA;
;     uint_fast16_t sigA;
;     union ui16_f16 uB;
;     uint_fast16_t uiB;
;     bool signB;
;     int_fast8_t expB;
;     uint_fast16_t sigB;
;     bool signZ;
;     uint_fast16_t magBits;
;     struct exp8_sig16 normExpSig;
;     int_fast8_t expZ;
;     uint_fast32_t sig32Z;
;     uint_fast16_t sigZ, uiZ;
;     union ui16_f16 uZ;

; multiply two signed fixed16 numbers and get a fixed16 result
; operation: 0hl * 0de -> 0hl
; destroys: af,af', bc, de
f16_mul:
;     /*------------------------------------------------------------------------
;     *------------------------------------------------------------------------*/
;     uA.f = a;
;     uiA = uA.ui;
;     signA = signF16UI( uiA );
;     expA  = expF16UI( uiA );
;     sigA  = fracF16UI( uiA );
;     uB.f = b;
;     uiB = uB.ui;
;     signB = signF16UI( uiB );
;     expB  = expF16UI( uiB );
;     sigB  = fracF16UI( uiB );
;     signZ = signA ^ signB;
;     /*------------------------------------------------------------------------
;     *------------------------------------------------------------------------*/
;     if ( expA == 0x1F ) {
;         if ( sigA || ((expB == 0x1F) && sigB) ) goto propagateNaN;
;         magBits = expB | sigB;
;         goto infArg;
;     }
;     if ( expB == 0x1F ) {
;         if ( sigB ) goto propagateNaN;
;         magBits = expA | sigA;
;         goto infArg;
;     }
;     /*------------------------------------------------------------------------
;     *------------------------------------------------------------------------*/
    ; if ( ! expA ) {
    ;     if ( ! sigA ) goto zero;
    ;     normExpSig = softfloat_normSubnormalF16Sig( sigA );
    ;     expA = normExpSig.exp;
    ;     sigA = normExpSig.sig;
    ; }
;     if ( ! expB ) {
;         if ( ! sigB ) goto zero;
;         normExpSig = softfloat_normSubnormalF16Sig( sigB );
;         expB = normExpSig.exp;
;         sigB = normExpSig.sig;
;     }
; determine sign of result and stack it
    ld a,h
    and %10000000
    xor d
    and %10000000
    push af ; stack the sign
; unpack hl
    push de ; TODO: figure out why DE gets stomped here
    call softfloat16_unpack
    pop de ; restore de TODO: figure out why DE gets stomped above
    jr c,@hl_zero
    push af ; stack the true exponent
    ; sigA = (sigA | 0x0400)<<4; (softfloat16_unpack already OR'd in the implicit 1)
    add hl,hl
    add hl,hl
    add hl,hl
    add hl,hl
; unpack de
    ex de,hl
    call softfloat16_unpack
    jr c,@de_zero
    ld c,a ; store true exponent of de
    pop af ; restore true exponent of hl
    ; expZ = expA + expB - 0xF;
    add a,c
    sub a,0xF
    ld c,a ; store true exponent of hl
    ; sigB = (sigB | 0x0400)<<5; (softfloat16_unpack already OR'd in the implicit 1)
    add hl,hl
    add hl,hl
    add hl,hl
    add hl,hl
    add hl,hl
    ; sig32Z = (uint_fast32_t) sigA * sigB;
    call mul_16_32 ; 32-bit product in hlde ...
    ; sigZ = sig32Z>>16; ... so we only need hl
    ; if ( sig32Z & 0xFFFF ) sigZ |= 1; set sticky bit
    ld a,e
    and a
    jr nz,@need_sticky
    ld a,d
    and a
    jr nz,@need_sticky
    jr @F
@need_sticky:
    set 0,l ; set sticky bit
@@: ; we land here if we did not need sticky
    ; if ( sigZ < 0x4000 ) {
    ;     --expZ;
    ;     sigZ <<= 1;
    ; }
; check for underflow
    ld a,h
    and %11000000 ; sigZ - 0x4000
    jr nz,@F ; sigZ >= 0x4000
@normalise_loop:
    dec c ; --expZ
    add hl,hl ; sigZ <<= 1
    bit 6,h ; test for carry into assumed 1 place
    jr nz @normalise_loop
@@: ; we land here if product was normal

;     return softfloat_roundPackToF16( signZ, expZ, sigZ );


; float16_t softfloat_roundPackToF16(bool sign, int_fast16_t exp, uint_fast16_t sig)
; {
;     uint_fast8_t roundBits;
;     uint_fast16_t uiZ;
;     union ui16_f16 uZ;

;     roundBits = sig & 0xF;

    ld a,l
    and 0xF
    ld b,a ; store round bits


    ld a,c ; get stored exponent
    cp 0x1D ; check for overflow
    jp nc,@do_rounding ; skip underflow/overflow check if exp < 0x1D
;     if ((unsigned int)exp >= 0x1D) {
    or a
    jp p,@check_overflow
;         if (exp < 0) {
    ld a,c ; exponent
    neg ; -exp = number of right shifts
    push bc ; next call stomps b (roundBits)
;             sig = softfloat_shiftRightJam32(sig, -exp);
    pop bc ; restore b (roundBits)
    call softfloat_shiftRightJam32
;             exp = 0;
    ld c,0 ; set exponent to zero
;             roundBits = sig & 0xF;
    ld a,0xF
    and b
    ld b,a ; store round bits
    jr @do_rounding

@check_overflow:
    cp 0x1D
    jp c,@do_rounding ; skip overflow check if exp < 0x1D
    ; TODO

;         } else if ((exp > 0x1D) || (sig + 0x8 >= 0x8000)) {
;             uiZ = packToF16UI(sign, 0x1F, 0);
;             return (float16_t)uiZ;
;         }
;     }
@do_rounding:
;     sig = (sig + 0x8) >> 4;
; add 0x8 to hlde
    ld a,e
    add a,0x08
    ld e,a
    ld a,d
    adc a,0
    ld d,a
    ld a,l
    adc a,0
    ld l,a
    ld a,h
    adc a,0
    ld h,a
; shift right four bits
; one
    srl h
    srl l
    srl d
    srl e
    or a ; clear carry
; two
    srl h
    srl l
    srl d
    srl e
    or a
; three
    srl h
    srl l
    srl d
    srl e
    or a 
; four
    srl h
    srl l
    srl d
    srl e

;     if (roundBits && (roundBits == 0x8) && !(sig & 1)) {
    ld a,b ; a = round bits
    or a
    jr z,@check_exp_0 ; skip if sig is zero
    cp 0x08
    jr nz,@check_exp_0 ; skip if round bits is not 0x08 (exactly halfway)
    bit 0,e ; check sig for even
    jr z,@check_exp_0 ; skip if odd
;         sig &= ~1; // round to even
    res 0,e ; clear LSB
;     }
@check_exp_0:
;     if (!sig) exp = 0;
    ld a,c ; get exponent
    or a ; check for zero
    jp z,packToF16UI ;  ; 

;     uiZ = packToF16UI(sign, exp, sig);
;     uZ.ui = uiZ;
;     return uZ.f;
; }

; #define packToF16UI( sign, exp, sig ) (((uint16_t) (sign)<<15) + ((uint16_t) (exp)<<10) + (sig))
packToF16UI:
    or a,h ; sign
    ld h,a ; sign
    ld a,c ; exponent
    add a,a ; exponent << 1
    add a,a ; exponent << 2
    or a,h ; sign + exponent
    ld h,a ; sign + exponent
    ret
; end packToF16UI


;     /*------------------------------------------------------------------------
;     *------------------------------------------------------------------------*/
;  propagateNaN:
;     uiZ = softfloat_propagateNaNF16UI( uiA, uiB );
;     goto uiZ;
;     /*------------------------------------------------------------------------
;     *------------------------------------------------------------------------*/
;  infArg:
;     if ( ! magBits ) {
;         softfloat_raiseFlags( softfloat_flag_invalid );
;         uiZ = defaultNaNF16UI;
;     } else {
;         uiZ = packToF16UI( signZ, 0x1F, 0 );
;     }
;     goto uiZ;
;     /*------------------------------------------------------------------------
;     *------------------------------------------------------------------------*/
;  zero:
;     uiZ = packToF16UI( signZ, 0, 0 );
;  uiZ:
;     uZ.ui = uiZ;
;     return uZ.f;
@de_zero:
    pop de ; dummy pop to balance stack
@hl_zero:
    pop de ; dummy pop to balance stack
    ret 

; }


; unsigned multiplication of two 16-bit integers with a 32-bit result
; inputs: hl,de = operands
; outputs: hlde = 32-bit product
; destroys: af, af', bc
mul_16_32:
    di
    ld b,h
    ld c,d
    push bc   ; h*d
    ld b,l
    push bc   ; l*d
    ld d,l
    ld b,h
    ld c,e
    mlt de    ; l*e / e out
    mlt bc    ; h*e
    ld a,d
    add a,c
    ld d,a    ; accum d
    ld a,b
    adc a,0
    ld l,a    ; accum l
    ex af,af' ; af'=carry h
    pop bc    ; l*d
    mlt bc    ; l*d
    ld a,d
    add a,c
    ld d,a    ; d out
    ld a,l
    adc a,b
    ld l,a    ; accum l
    ld a,0
    adc a,a
    ld h,a    ; accum h
    ex af,af' ; af=carry h
    ld a,h
    adc a,0
    ld h,a    ; accum h
    pop bc    ; h*d
    mlt bc    ; h*d
    ld a,l
    add a,c
    ld l,a    ; l out
    ld a,h
    adc a,b
    ld h,a    ; h out
    ei
    ret
; end mul_16_32
