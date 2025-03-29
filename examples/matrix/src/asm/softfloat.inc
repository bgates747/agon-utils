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
;     if ( ! expA ) {
;         if ( ! sigA ) goto zero;
;         normExpSig = softfloat_normSubnormalF16Sig( sigA );
;         expA = normExpSig.exp;
;         sigA = normExpSig.sig;
;     }
;     if ( ! expB ) {
;         if ( ! sigB ) goto zero;
;         normExpSig = softfloat_normSubnormalF16Sig( sigB );
;         expB = normExpSig.exp;
;         sigB = normExpSig.sig;
;     }
;     /*------------------------------------------------------------------------
;     *------------------------------------------------------------------------*/
;     expZ = expA + expB - 0xF;
;     sigA = (sigA | 0x0400)<<4;
;     sigB = (sigB | 0x0400)<<5;
;     sig32Z = (uint_fast32_t) sigA * sigB;
;     sigZ = sig32Z>>16;
;     if ( sig32Z & 0xFFFF ) sigZ |= 1;
;     if ( sigZ < 0x4000 ) {
;         --expZ;
;         sigZ <<= 1;
;     }
;     return softfloat_roundPackToF16( signZ, expZ, sigZ );
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

; }

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

;     12
; x   34
; ----------
; +


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

; SECOND ATTEMPT
    di
    ld b,h
    ld c,l
    ld a,d
    ex af,af'
    ld d,l
    ld a,e
    mlt de
    ld l,a
    mlt hl
    ld a,d
    add a,l
    ld d,a
    ld a,h
    adc a,0
    ex af,af'
    ld h,a
    ld l,c
    mlt hl
    ld c,a
    ld a,l
    add a,d
    ld d,a
    ex af,af'
    adc a,h
    ld l,a
    ex af,af'
    mlt bc
    ld a,l
    adc a,c
    ld l,a
    ex af,af'
    ld a,b
    adc a,0
    ld h,a
    ei
    ret


; FIRST ATTEMPT
    di
    ld b,l
    ld c,e
    mlt bc
    ld a,c
    ex af,af'
    ld a,b
    ld b,h
    ld c,e
    mlt bc
    add a,c
    ld e,b
    ld b,l
    ld c,d
    mlt bc
    adc a,c
    ld c,d
    ld d,a
    ld a,e
    adc a,b
    ld b,h
    mlt bc
    adc a,c
    ld l,a
    ld a,b
    adc a,0
    ld h,a
    ex af,af'
    ld e,a
    ei
    ret