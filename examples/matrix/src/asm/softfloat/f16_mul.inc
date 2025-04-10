; multiply two signed fixed16 numbers and get a fixed16 result
; operation: 0hl * 0de -> 0hl
; destroys: af,af', bc, de
f16_mul:
; compute sign of product
    ld a,h ; sign hl
    and %10000000
    xor d ; xor sign hl with sign de
    and %10000000
    ld c,a  ; signZ

; check operands for NaN
    ld a,0xFE ; NaN upper byte is all we need
    cp h
    jp z,@ret_nan
    cp d
    jp z,@ret_nan

; check de for zero
    ex de,hl ; flip operands
    res 7,h ; clear sign bit
    SIGN_HL
    ; DUMP_REGISTERS_HEX "after de sign test:"
    jp z,@de_zero

; get exponent of de
    res 7,h ; clear sign bit (makes life easier on the zero-check later)
    ld a,h ; expB
    and %01111100 ; stored exp of de
    rra ; shift exp
    rra ; down twice
    cp  %00011111 ; test for inf
    jp z,@de_inf
    ld b,a ; assume normal
    and a ; test for subnormal
    call z,softfloat_normSubnormalF16Sig

; get mantissa of de
    ld a,h
    and %00000011 ; mask out sign and exponent
    ld h,a
    ex de,hl ; flip operands back

; check hl for zero
    res 7,h ; clear sign bit
    SIGN_HL
    ; DUMP_REGISTERS_HEX "after hl sign test:"
    jp z,@hl_zero

; get exponent of hl
    ld a,h ; expB
    and %01111100 ; stored exp of hl
    rra ; shift exp
    rra ; down twice
    cp  %00011111 ; test for inf
    jp z,@hl_inf
    and a ; test for subnormal
    jr nz,@F ; skip if normal
    ld a,b ; a = expB
    call softfloat_normSubnormalF16Sig
@@:
; compute exponent of product
    ; DUMP_REGISTERS_HEX "a=exp hl, b=exp de:"
    add a,b ; expA + expB
    sub 0x0F ; expA + expB - 0xF
    ld b,a ; expZ
    ; DUMP_REGISTERS_HEX "b=exp product:"

; get mantissa of hl
    ld a,h
    and %00000011 ; mask out sign and exponent
    ld h,a

; cleared to proceed with the multiplication
    ; DUMP_REGISTERS_HEX "cleared to proceed with the multiplication:"
    push bc ; stack sign and exponent of product
; sigA = (sigA | 0x0400)<<4;
    set 2,h ; set implicit 1
    add hl,hl
    add hl,hl
    add hl,hl
    add hl,hl
    ; PRINT_HL_HEX_BIN "sigA <<4:"
; sigB = (sigB | 0x0400)<<5;
    ex de,hl
    set 2,h ; set implicit 1
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
    jp nz,@need_sticky
    ld a,d
    and a
    jp nz,@need_sticky
    jp @do_sign_exp
@need_sticky:
    set 0,l ; set sticky bit
@do_sign_exp:
    pop bc ; exp and sign of product
    ; DUMP_REGISTERS_HEX "b = exp and c = sign of product:"
; check for subnormal
    ld a,h
    and %11000000 ; sigZ - 0x4000
    jp nz,@end_normalise ; sigZ >= 0x4000
    ; PRINT_HL_HEX_BIN "sigZ subnormal (hl):"
@normalise_loop:
    dec b ; --expZ
    add hl,hl ; sigZ <<= 1
    bit 6,h ; test for carry into assumed 1 place
    jp z,@normalise_loop
    ; PRINT_HL_HEX_BIN "sigZ normalised (hl):"
@end_normalise: ; we land here if product was normal
; return softfloat_roundPackToF16( signZ, expZ, sigZ );
    jp softfloat_roundPackToF16
@de_zero:
    ld a,d ; is really h because we're flipped
    and %01111100 ; stored exp of hl
    cp %01111100 ; check for inf
    jp z,@ret_nan ; return NaN if exponent is 0x1F    
    ld a,c ; sign
    or h ; (re)set sign bit
    ld h,a
    ret
@hl_zero:
    ld a,b ; de's exponent
    cp 0x1F ; check for inf
    jp z,@ret_nan ; return NaN if exponent is 0x1F
    ld a,c ; sign
    or h ; (re)set sign bit
    ld h,a
    ret
@hl_inf:
@de_inf:
    ex de,hl          ; flip operands
    res 7,h           ; clear sign bit just in case
    SIGN_HL           ; test hl for zero
    jr z,@ret_nan     ; zero * inf = NaN
    ld hl,0x7C00      ; Inf result
    ld a,c            ; get product sign
    or h              ; reapply sign
    ld h,a
    ret
@ret_nan:
    ld hl,0xFE00      ; canonical NaN
    ; ld a,c            ; get product sign
    ; or h              ; reapply sign
    ; ld h,a
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
