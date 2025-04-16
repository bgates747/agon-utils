
; /*============================================================================

; This C source file is part of the SoftFloat IEEE Floating-Point Arithmetic
; Package, Release 3e, by John R. Hauser.

; Copyright 2011, 2012, 2013, 2014, 2015, 2017 The Regents of the University of
; California.  All rights reserved.

; Redistribution and use in source and binary forms, with or without
; modification, are permitted provided that the following conditions are met:

;  1. Redistributions of source code must retain the above copyright notice,
;     this list of conditions, and the following disclaimer.

;  2. Redistributions in binary form must reproduce the above copyright notice,
;     this list of conditions, and the following disclaimer in the documentation
;     and/or other materials provided with the distribution.

;  3. Neither the name of the University nor the names of its contributors may
;     be used to endorse or promote products derived from this software without
;     specific prior written permission.

; THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS "AS IS", AND ANY
; EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
; WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE, ARE
; DISCLAIMED.  IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS BE LIABLE FOR ANY
; DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
; (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
; ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
; (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
; SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

; =============================================================================*/

; ===============================================================================
; eZ80 Assembly Implementation
; Original C code has been simplified so that only the default rounding options 
; are used, and so branching tests are more ez80 friendly.
; ===============================================================================
; inputs: c = sign (0=pos, 0x80=neg), b = biased exp, 
;         hl = sig (implied 1 place in bit 14, rounding bits in bits 0-3)
; outputs: hl = packed float16, c = sign (0=pos, 0x80=neg), b = biased exp
; destroys: af, de
softfloat_roundPackToF16:
; uint_fast8_t roundIncrement = 0x8;
; uint_fast8_t roundBits = sig & 0xF;

; ; DEBUG
;     ld a,c
;     PRINT_A_HEX "sign"
;     ld a,b
;     PRINT_A_HEX "exp"
;     PRINT_HL_HEX_BIN "sigZ prior to rounding"
; ; END DEBUG

; if (exp < 0) {
    ld a,b ; get exponent
    cp 0
    jp p,@check_overflow
;     // -----------------------------
;     // Subnormal / Underflow path
;     // -----------------------------
;     bool isTiny = (
;         softfloat_detectTininess == softfloat_tininess_beforeRounding ||
;         exp < -1 ||
;         sig + roundIncrement < 0x8000
;     );
;     sig = softfloat_shiftRightJam32(sig, -exp);
        neg ; negate exponent
        ex de,hl ; move hl to lower bytes of the 32 bit argument
        ld hl,0 ; upper bytes of 32 bit argument to zero
        call softfloat_shiftRightJam32
        ex de,hl ; shifted/jammed sig back to hl
;     exp = 0;
        ld b,0
;     roundBits = sig & 0xF;
        ld a,0x0F
        and l
        ld d,a ; store roundBits
;     if (isTiny && roundBits) {
        jr z,@do_rounding ; skip if roundBits is zero
        and a,b ; check exponent for 0 (tiny)
        jr z,@do_rounding ; skip if exponent is zero
;         softfloat_raiseFlags(softfloat_flag_underflow);
;     }
        jr @do_rounding
; }
@check_overflow:
    ; } else if ( (0x1D < exp) || (0x8000 <= sig + roundIncrement) ) {
    ;     softfloat_raiseFlags(
    ;         softfloat_flag_overflow | softfloat_flag_inexact );
    ;     uiZ = packToF16UI( sign, 0x1F, 0 ) - ! roundIncrement;
        cp 0x1E
        jr nc,@return_inf ; return inf if exp < 0x1D
        jr nz,@do_rounding ; skip if exp != 0x1E (meaning we can round up without going to inf)
        ex de,hl ; preserve sig in de for upcoming test
        ld hl,0x8000 - 0x0008 - 1 ; 0x8000 - roundIncrement = 0x7FF7
        or a ; clear carry
        sbc hl, de           ; HL = 0x7FF7 - DE
        ex de, hl
        jr c, @return_inf    ; if sig > 0x7FF7, overflow
; }
@do_rounding:
; roundBits = sig & 0xF
    ld a,0x0F
    and l
    ld d,a ; store roundBits
; sig = (sig + roundIncrement) >> 4;
; add round increment
    ld a,l
    add 0x08
    ld l,a
    ld a,h
    adc a,0
    ld h,a
; shift right by 4 bits
; once
    or a ; clear carry
    rr h
    rr l
; twice
    or a
    rr h
    rr l
    or a
; thrice
    or a
    rr h
    rr l
; four times
    or a
    rr h
    rr l
; if (roundBits) {
;     softfloat_exceptionFlags |= softfloat_flag_inexact;
; }
    ; d == roundBits
    ld a,d
    cp 0x08
    jp nz,@check_sig_zero      ; Not exactly halfway -> skip
    ; Exactly halfway => round to even.
    bit 0,l                    ; Test LSB of HL
    jp z,@check_sig_zero       ; If LSB = 0 (already even), skip
    res 0,l                    ; Else clear LSB => rounding to even
    jp packToF16UI
; if (!sig) {
@check_sig_zero:
    SIGN_HL
    jp nz,packToF16UI ; skip if sig is not zero
;     exp = 0;
        ld b,0
; }
; return packToF16UI(sign, exp, sig);
    jp packToF16UI
@return_inf:
; // -----------------------------
; // Overflow after rounding
; // -----------------------------
; softfloat_raiseFlags(softfloat_flag_overflow | softfloat_flag_inexact);
; return packToF16UI(sign, 0x1F, 0) - !roundIncrement;
    ld hl,0x7C00
    ld a,c ; get sign
    or h
    ld h,a
    ld b,0x1F ; exponent
    ret
; end softfloat_roundPackToF16
