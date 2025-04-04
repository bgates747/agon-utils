

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
    push af ; stack the biased exponent
    ; sigA = (sigA | 0x0400)<<4; (softfloat16_unpack already OR'd in the implicit 1)
    add hl,hl
    add hl,hl
    add hl,hl
    add hl,hl
; unpack de
    ex de,hl
    call softfloat16_unpack
    jr c,@de_zero
    ld c,a ; store biased exponent of de
    pop af ; restore biased exponent of hl
    ; expZ = expA + expB - 0xF;
    add a,c
    sub a,0xF
    ld c,a ; store biased exponent of hl
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
    jr @no_sticky
@need_sticky:
    set 0,l ; set sticky bit
@no_sticky:
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
    jr nz,@normalise_loop
@@: ; we land here if product was normal

;     return softfloat_roundPackToF16( signZ, expZ, sigZ );
    jp softfloat_roundPackToF16


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
