; multiply two signed fixed16 numbers and get a fixed16 result
; operation: 0hl * 0de -> 0hl
; destroys: af,af', bc, de
f16_mul:
; unpack hl
    call softfloat16_unpack
    push bc ; save sign and exponent of hl
    push af ; save carry, masquerading here as zero flag
; unpack de
    ex de,hl
    call softfloat16_unpack
    ex de,hl
    jp c,@de_zero ; jr c,@de_zero
; check hl for zero
    pop af ; restore hl's zero flag to carry
    jp c,@hl_zero ; jr c,@hl_zero
; cleared to proceed with the multiplication
    push bc ; stack sign and exponent of de
; sigA = (sigA | 0x0400)<<4; (softfloat16_unpack already OR'd in the implicit 1)
    add hl,hl
    add hl,hl
    add hl,hl
    add hl,hl
    ; PRINT_HL_HEX_BIN "sigA <<4:"
; sigB = (sigB | 0x0400)<<5; (softfloat16_unpack already OR'd in the implicit 1)
    ex de,hl
    add hl,hl
    add hl,hl
    add hl,hl
    add hl,hl
    add hl,hl
    ; PRINT_HL_HEX_BIN "sigB <<5:"
    ex de,hl
; sig32Z = (uint_fast32_t) sigA * sigB;
    call mul_16_32 ; 32-bit product in hlde ...
    ; PRINT_HL_HEX_BIN "sig32Z upper (hl):"
    ex de,hl
    ; PRINT_HL_HEX_BIN "sig32Z lower (de):"
    ex de,hl
; sigZ = sig32Z>>16; (we get this for free since HL contains the relevant bits)
; if ( sig32Z & 0xFFFF ) sigZ |= 1; set sticky bit
    ld a,e
    and a
    jr nz,@need_sticky
    ld a,d
    and a
    jr nz,@need_sticky
    jr @do_sign_exp
@need_sticky:
    set 0,l ; set sticky bit
@do_sign_exp:
    pop de ; exp and sign of de
    pop bc ; exp and sign of hl
    ; DUMP_REGISTERS_HEX "Get back signs and exponents in de and bc:"
; expZ = expA + expB - 0xF;
    ld a,d ; expB
    add a,b ; expA + expB
    sub 0x0F ; expA + expB - 0xF
    ld b,a ; expZ
; compute sign of product
    ld a,e ; sign de
    xor c ; xor sign de with sign hl
    ld c,a  ; signZ
    ; DUMP_REGISTERS_HEX "Computed product exp in b, sign in c:"
; check for subnormal
    ld a,h
    and %11000000 ; sigZ - 0x4000
    jr nz,@end_normalise ; sigZ >= 0x4000
    ; PRINT_HL_HEX_BIN "sigZ subnormal (hl):"
@normalise_loop:
    dec b ; --expZ
    add hl,hl ; sigZ <<= 1
    bit 6,h ; test for carry into assumed 1 place
    jr z,@normalise_loop
    ; PRINT_HL_HEX_BIN "sigZ normalised (hl):"
@end_normalise: ; we land here if product was normal
; return softfloat_roundPackToF16( signZ, expZ, sigZ );
    jp softfloat_roundPackToF16
@de_zero:
    pop af ; contains hl's zero flag in carry
    jr c,@hl_zero
    pop af ; unstack hl's exponent to a (was b)
    cp 0x1F ; check for inf
    jr z,@ret_nan ; return NaN if exponent is 0x1F
    ex de,hl ; put de into hl to return zero
    ld a,c ; sign
    or h ; (re)set sign bit
    ld h,a
    ret
@hl_zero:
    pop af ; dummy pop to balance stack
    ld a,b ; de's exponent
    cp 0x1F ; check for inf
    jr z,@ret_nan ; return NaN if exponent is 0x1F
    ld a,c ; sign
    or h ; (re)set sign bit
    ld h,a
    ret
@ret_nan:
    ld hl,0x7E00 ; NaN
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
