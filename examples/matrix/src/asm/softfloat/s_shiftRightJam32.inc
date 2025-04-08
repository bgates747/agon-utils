; /*----------------------------------------------------------------------------
; | Shifts 'a' right by the number of bits given in 'dist', which must not
; | be zero.  If any nonzero bits are shifted off, they are "jammed" into the
; | least-significant bit of the shifted value by setting the least-significant
; | bit to 1.  This shifted-and-jammed value is returned.
; |   The value of 'dist' can be arbitrarily large.  In particular, if 'dist' is
; | greater than 32, the result will be either 0 or 1, depending on whether 'a'
; | is zero or nonzero.
; *----------------------------------------------------------------------------*/
;
; uint32_t softfloat_shiftRightJam32( uint32_t a, uint_fast16_t dist )
; {

;     return
;         (dist < 31) ? a>>dist | ((uint32_t) (a<<(-dist & 31)) != 0) : (a != 0);

; }
;
; Inputs: HLDE = 32-bit unsigned integer to shift (most to least significant byte)
;          A = number of bits to shift right (0–255, only 0–31 meaningful)
;
; Outputs: HLDE = shifted result, with LSB jammed (bit 0 set) if any 1s were shifted out
;          A = jam bit (0 or 1)

softfloat_shiftRightJam32:
    ; call dumpRegistersHex

    push bc ; preserve b
    ld b,a ; loop counter
    xor a ; zero jam bits and clear carry
@shift_loop:
    rr h
    rr l
    rr d
    rr e
    adc a,0 ; jam bit
    or a ; clear carry
    djnz @shift_loop
    or a ; check whether to set jam bit
    jr z, @done ; no jam bit set
    set 0,e ; set jam bit to LSB
@done:
    pop bc ; restore b
    ret
; end softfloat_shiftRightJam32