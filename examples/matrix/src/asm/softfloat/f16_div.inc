; r0 = softfloat_approxRecip_1k0s[index]-((softfloat_approxRecip_1k1s[index]*(sigB & 0x3F))>>10);

; inputs: hl = dividend, de = divisor
; outputs: hl = float16 result
f16_div:
; compute sign of the quotient
    ld a,h ; sign opA
    and %10000000
    xor d ; xor sign opA with sign opB
    and %10000000
    ld (@signZ),a

    ; PRINT_A_HEX "signZ" ; DEBUG

; unpack opB
    ex de,hl
    call softfloat16_unpack
    ld (@sigB),hl ; store sigB
    ld a,b ; exponent
    ld (@expB),a ; store exponent

; unpack opA
    ex de,hl
    call softfloat16_unpack
    ld a,b ; exponent
    ld (@expA),a
    ld (@sigA),hl ; store sigA

; === HANDLE SPECIAL CASES ===
; if ( expA == 0x1F ) {
    cp 0x1F ; check expA for inf
    jr nz,@check_expB_inf
;     if ( sigA ) goto propagateNaN;
        SIGN_HL
        jp nz,@return_nan
;     if ( expB == 0x1F ) {
        ld a,(@expB)
        cp 0x1F ; check expB for inf
        jp nz,@return_inf
;         if ( sigB ) goto propagateNaN;
            ld hl,(@sigB)
            SIGN_HL
            jp nz,@return_nan ; non-signalling NaN
;         goto invalid;
            jp @return_invalid ; signalling NaN
;     }
;     goto infinity; // handled above
; }
@check_expB_inf:
; if ( expB == 0x1F ) {
    ld a,(@expB) 
    cp 0x1F ; check expB for inf
    jr nz,@check_expB_zero
;     if ( sigB ) goto propagateNaN;
        ld hl,(@sigB)
        SIGN_HL
        jp nz,@return_nan ; non-signalling NaN
;     goto zero;
        jp @return_zero
; }
; /*------------------------------------------------------------------------
; *------------------------------------------------------------------------*/
@check_expB_zero:
; if ( ! expB ) {
    or a ; check expB for zero
    jr nz,@check_expA_zero
; if ( ! sigB ) {
    ld hl,(@sigB)
    SIGN_HL
    jr nz,@check_expA_zero
; if ( ! (expA | sigA) ) goto invalid;
    ld a,(@expA)
    or a ; check expA for zero
    jr nz,@b_zero_a_nonzero
    ld hl,(@sigA)
    SIGN_HL
    jr nz,@b_zero_a_nonzero
; 0/0 case
    jp @return_invalid
@b_zero_a_nonzero:
; softfloat_raiseFlags( softfloat_flag_infinite );
; goto infinity;
    jp @return_inf
; }
; normExpSig = softfloat_normSubnormalF16Sig( sigB );
; expB = normExpSig.exp;
; sigB = normExpSig.sig;
; }
@check_expA_zero:
; if ( ! expA ) {
    ld a,(@expA)
    or a ; check expA for zero
    jr nz,@end_specials
;     if ( ! sigA ) goto zero;
        ld hl,(@sigA)
        SIGN_HL
        jp z,@return_zero
; // we already normalized subormals so this is not needed
;    // normExpSig = softfloat_normSubnormalF16Sig( sigA );
;    // expA = normExpSig.exp;
;    // sigA = normExpSig.sig;
; }
@end_specials:

; expZ = expA - expB + 0xE
    ld a,(@expA)
    ld b,a
    ld a,(@expB)
    sub b
    neg
    add 0x0E
; if sigA < sigB: expZ = expZ - 1, numShifts = 5
; else: numShifts = 4
; sigA = u16(sigA << numShifts)
    ld bc,(@sigB)
    or a ; clear carry
    sbc.s hl,bc ; sigA - sigB (.s to force 16-bit subtraction)
    ld hl,(@sigA)
    jr nc,@sigA_gte_sigB ; sigA < sigB
; expZ = expZ - 1
    dec a
; sigA = u16(sigA << 5)
    add hl,hl
@sigA_gte_sigB:
    ld (@expZ),a
; else: sigA = u16(sigA << 4)
    add hl,hl
    add hl,hl
    add hl,hl
    add hl,hl
    ld (@sigA),hl ; store sigA shifted up

    ; PRINT_A_HEX "expZ" ; DEBUG
    ; PRINT_HL_HEX "sigA shifted left" ; DEBUG
    ; PRINT_BC_HEX "sigB" ; DEBUG

; index = sigB>>6 & 0xF;
    ld l,c
    ld h,b
    add hl,hl
    add hl,hl
    ld a,h
    and 0x0F ; index

    ; PRINT_A_HEX "index" ; DEBUG

    add a,a ; 2 bytes per LUT entry
    ld e,a
    ld d,0
    dec de
    inc.s de ; zero deu
    push ix ; preserve
    ld ix,softfloat_approxRecip_1k0s
    add ix,de

; ; DEBUG
;     ld hl,(ix)
;     PRINT_HL_HEX "approx1k0s"
;     ld hl,(ix+32)
;     PRINT_HL_HEX "approx1k1s"
; ; END DEBUG

; r0 = approx1k0s - (((approx1k1s * (sigB & 0x3F)) >> 10))
    ld hl,(ix+32) ; approx1k1s
    ld a,c ; sigB low byte
    and 0x3F ; sigB & 0x3F
    call mul16x8 ; (sigB & 0x3F) -> ade
; >>10
    or a ; clear carry
    rra
    rr d
    or a ; clear carry
    rra
    rr d
    ld e,d
    ld d,a
    dec de
    inc.s de ; zero deu
    ld hl,(ix) ; approx1k0s
    pop ix ; send back how it came in
    or a ; clear carry
    sbc.s hl,de ; hl = r0 = approx1k0s - ((approx1k1s * (sigB & 0x3F)) >> 10)
    ld (@r0),hl ; store r0

    ; PRINT_HL_HEX "r0" ; DEBUG

; sigZ = u32((sigA * r0) >> 16)
    ld de,(@sigA)
    call mul_16_32_calc84maniac ; hl = sigZ
    ld (@sigZ),hl

    ; PRINT_HL_HEX "sigZ" ; DEBUG

    call @compute_sigZ_error

; sigZ += (rem * (uint_fast32_t) r0)>>26;
; both multiplicands are 16 bits so we can use 16x16->32 bit multiply
    ld hl,(@r0)
    call mul_16_32_calc84maniac ; hlde = rem * r0
    ld a,h ; top byte of product
    srl a
    srl a

    ; PRINT_A_HEX "rem * r0 >> 26" ; DEBUG

    ld hl,(@sigZ)
    add a,l
    ld l,a
    adc a,h
    sub l
    ld h,a

    ; PRINT_HL_HEX "sigZ + (rem * r0)>>26" ; DEBUG

; ++sigZ;
    inc hl
    
    ; PRINT_HL_HEX "sigZ + 1" ; DEBUG

; if ( ! (sigZ & 7) ) {
    ld a,l
    and 0x07
    jr nz,@return
;     sigZ &= ~1;
        res 0,l
        ld (@sigZ),hl
        ; PRINT_HL_HEX "sigZ &= ~1" ; DEBUG
;     rem = (sigA<<10) - sigZ * sigB;
        call @compute_sigZ_error
        ; PRINT_DE_HEX "rem = (sigA<<10) - sigZ * sigB" ; DEBUG
;     if ( rem & 0x8000 ) {
        ld hl,(@sigZ)
        ld a,d
        and 0x80
        jr z,@F
;         sigZ -= 2;
            dec hl
            dec hl
            jr @return
;     } else {
@@:
;         if ( rem ) sigZ |= 1;
            ld a,d
            or a
            jr nz,@F
            ld a,e
            or a
            jr z,@return
@@:
            set 0,l
            ; PRINT_HL_HEX "sigZ |= 1" ; DEBUG
;     }
; }

@return:
; hl must be set to sigZ at this point
    ld bc,(@signZ) ; b=expZ, c=signZ
    jp softfloat_roundPackToF16 ; assumes hl holds sig
@return_invalid: ; fow now, we don't distinguish between signalling and non-signalling NaN
@return_nan:
    ld hl,0xFE00 ; canonical NaN
    ret
@return_inf:
    ld l,0
    ld a,(@signZ)
    or 0x7C
    ld h,a
    ret
@return_zero:
    ld l,0
    ld a,(@signZ)
    ld h,a
    ret
; compute the error of sigZ
; inputs: hl = sigZ, (@sigB), (@sigA), (@r0)
; returns: hlde = rem (only de should matter)
@compute_sigZ_error:
; rem = u32((sigA << 10) - sigZ * sigB)
    ld de,(@sigB)
    ; PRINT_DE_HEX "sigB" ; DEBUG
    call mul_16_32_calc84maniac ; hlde = sigZ * sigB
    ; PRINT_HLDE_HEX "sigZ * sigB"
    push hl ; stack upper word of product
    ld hl,(@sigA)
    add hl,hl
    add hl,hl
    ; ld (@scratch),hl ; only need to do this if difference will occupy more than four bytes
    pop bc ; restore upper word of product (was hl)
    xor a ; a is our phantom zero register
; now we're set to do the subtraction:
;   uhl0
; - bcde
;  ------
;   bcde
    sub e
    ld e,a
    ld a,l
    sbc a,d
    ld d,a
; ; de should contain our answer, so we should not have to do the following
;     ld a,h
;     sbc a,c
;     ld c,a
;     ld a,(@scratch+2) ; hlu
;     sub b
;     ld b,a ; we assume no carry out

; ; DEBUG
;     push bc
;     pop hl
;     PRINT_HLDE_HEX "rem"
; ; END DEBUG
    ret
; end @compute_sigZ_error

; scratch variables
@expA: db 0
@expB: db 0
@sigA: dl 0
@sigB: dl 0
@r0:  dl 0
@signZ: db 0
@expZ: db 0
@sigZ: dl 0
@scratch: dl 0
; end f16_div

; Inputs: hl is the 16 bit multiplicand, a is the 8 bit multiplier
; Outputs: ade = 24-bit result
; Destroys: f, hl
mul16x8:
    ld d,l
    ld e,a
    mlt de ; l * a
    ld l,a
    mlt hl ; h * a
; hl<<8 + de -> ade
    ld a,d
    add a,l
    ld d,a
    adc a,h
    sub a,d
    ret
; end mul16x8

; ; Inputs: hl is the 16 bit multiplicand, a is the 8 bit multiplier
; ; Outputs: uhl = 24-bit result
; ; Destroys: f, de
; mul16x8:
;     ld d,l
;     ld e,a
;     mlt de ; l * a
;     ld l,a
;     mlt hl ; h * a
; ; hl<<8 + de -> uhl
;     add hl,hl ; 1
;     add hl,hl ; 2
;     add hl,hl ; 3
;     add hl,hl ; 4
;     add hl,hl ; 5
;     add hl,hl ; 6
;     add hl,hl ; 7
;     add hl,hl ; 8
;     add hl,de
;     ret
; ; end mul16x8

softfloat_approxRecip_1k0s:
    dw 0xFFC4, 0xF0BE, 0xE363, 0xD76F, 0xCCAD, 0xC2F0, 0xBA16, 0xB201
    dw 0xAA97, 0xA3C6, 0x9D7A, 0x97A6, 0x923C, 0x8D32, 0x887E, 0x8417

softfloat_approxRecip_1k1s:
    dw 0xF0F1, 0xD62C, 0xBFA1, 0xAC77, 0x9C0A, 0x8DDB, 0x8185, 0x76BA
    dw 0x6D3B, 0x64D4, 0x5D5C, 0x56B1, 0x50B6, 0x4B55, 0x4679, 0x4211


div_16_32_xeda:
    call div_16_xeda
    push de
    call div_16_xeda
    pop hl
    ex de,hl
    ret


div_16_xeda:
;;Inputs: DE is the numerator, BC is the divisor
;;Outputs: DE is the result, HL is the remainder
;;         A is a copy of E
;;         BC is not changed
;140 bytes
;145cc
    xor a 
    sbc.s hl,hl
    ld a,d
    rla 
    adc.s hl,hl 
    sbc.s hl,bc 
    jr nc,$+4 
    add.s hl,bc
    rla 
    adc.s hl,hl 
    sbc.s hl,bc 
    jr nc,$+4 
    add.s hl,bc
    rla 
    adc.s hl,hl 
    sbc.s hl,bc 
    jr nc,$+4 
    add.s hl,bc
    rla 
    adc.s hl,hl 
    sbc.s hl,bc 
    jr nc,$+4 
    add.s hl,bc
    rla 
    adc.s hl,hl 
    sbc.s hl,bc 
    jr nc,$+4 
    add.s hl,bc
    rla 
    adc.s hl,hl 
    sbc.s hl,bc 
    jr nc,$+4 
    add.s hl,bc
    rla 
    adc.s hl,hl 
    sbc.s hl,bc 
    jr nc,$+4 
    add.s hl,bc
    rla 
    adc.s hl,hl 
    sbc.s hl,bc 
    jr nc,$+4 
    add.s hl,bc
    rla 
    cpl 
    ld d,a

    ld a,e
    rla 
    adc.s hl,hl 
    sbc.s hl,bc 
    jr nc,$+4 
    add.s hl,bc
    rla 
    adc.s hl,hl 
    sbc.s hl,bc 
    jr nc,$+4 
    add.s hl,bc
    rla 
    adc.s hl,hl 
    sbc.s hl,bc 
    jr nc,$+4 
    add.s hl,bc
    rla 
    adc.s hl,hl 
    sbc.s hl,bc 
    jr nc,$+4 
    add.s hl,bc
    rla 
    adc.s hl,hl 
    sbc.s hl,bc 
    jr nc,$+4 
    add.s hl,bc
    rla 
    adc.s hl,hl 
    sbc.s hl,bc 
    jr nc,$+4 
    add.s hl,bc
    rla 
    adc.s hl,hl 
    sbc.s hl,bc 
    jr nc,$+4 
    add.s hl,bc
    rla 
    adc.s hl,hl 
    sbc.s hl,bc 
    jr nc,$+4 
    add.s hl,bc
    rla 
    cpl 
    ld e,a
    ret

;;End of div16