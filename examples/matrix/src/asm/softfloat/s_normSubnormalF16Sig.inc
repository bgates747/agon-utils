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
    ld a,1 ; set starting exponent
@norm_loop:
    add hl,hl ; shift left
    dec a ; decrement exponent
    bit 2,h ; test for carry into assumed 1 place
    ret nz
    jr @norm_loop
; end softfloat_normSubnormalF16Sig