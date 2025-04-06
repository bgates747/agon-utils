

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
    ld c,a ; save sign ; a=0x00

; ; DEBUG
;     call dumpRegistersHex
; ; END DEBUG

; unpack hl
    call softfloat16_unpack
    jr c,@hl_zero
    ld a,b ; get exponent
    push af ; save exponent
    ; sigA = (sigA | 0x0400)<<4; (softfloat16_unpack already OR'd in the implicit 1)
    add hl,hl
    add hl,hl
    add hl,hl
    add hl,hl
; unpack de
    ex de,hl
    call softfloat16_unpack
    jr c,@de_zero
    pop af ; restore exponent of hl
    ; a=0x0f, b=0x0f, hl=0x0400, de=0x4000

; ; DEBUG
;     call dumpRegistersHex
; ; END DEBUG

    ; expZ = expA + expB - 0xF;
    add a,b ; expA + expB
    sub 0x0F ; expA + expB - 0xF
    ld b,a ; store exponent of hl
    ; sigB = (sigB | 0x0400)<<5; (softfloat16_unpack already OR'd in the implicit 1)
    add hl,hl
    add hl,hl
    add hl,hl
    add hl,hl
    add hl,hl
    ; c=0x00, b=0x0f, hl=0x8000, de=0x4000

; ; DEBUG
;     call dumpRegistersHex
; ; END DEBUG

    ; sig32Z = (uint_fast32_t) sigA * sigB;
    push bc ; save sign and exponent
    call mul_16_32 ; 32-bit product in hlde ...
    pop bc ; restore sign and exponent
    ; b=0x0f, c=0x00, hl=0x2000, de=0x0000

; ; DEBUG
;     call dumpRegistersHex
; ; END DEBUG

    ; sigZ = sig32Z>>16;
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
    ; not taken
; ; DEBUG
;     call dumpRegistersHex
; ; END DEBUG
@no_sticky:
    ; if ( sigZ < 0x4000 ) {
    ;     --expZ;
    ;     sigZ <<= 1;
    ; }
; check for subnormal
    ld a,h
    and %11000000 ; sigZ - 0x4000
    jr nz,@end_normalise ; sigZ >= 0x4000
@normalise_loop:
    dec b ; --expZ
    add hl,hl ; sigZ <<= 1
    bit 6,h ; test for carry into assumed 1 place
    jr nz,@normalise_loop
@end_normalise: ; we land here if product was normal
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
