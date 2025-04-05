
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

; #include <stdbool.h>
; #include <stdint.h>
; #include "platform.h"
; #include "internals.h"
; #include "softfloat.h"

; float16_t softfloat_roundPackToF16( bool sign, int_fast16_t exp, uint_fast16_t sig )
; {
;     uint_fast8_t roundingMode;
;     bool roundNearEven;
;     uint_fast8_t roundIncrement, roundBits;
;     bool isTiny;
;     uint_fast16_t uiZ;
;     union ui16_f16 uZ;

;     /*------------------------------------------------------------------------
;     *------------------------------------------------------------------------*/
;     roundingMode = softfloat_roundingMode;
;     roundNearEven = (roundingMode == softfloat_round_near_even);
;     roundIncrement = 0x8;
;     if ( ! roundNearEven && (roundingMode != softfloat_round_near_maxMag) ) {
;         roundIncrement =
;             (roundingMode
;                  == (sign ? softfloat_round_min : softfloat_round_max))
;                 ? 0xF
;                 : 0;
;     }
;     roundBits = sig & 0xF;
;     /*------------------------------------------------------------------------
;     *------------------------------------------------------------------------*/
;     if ( 0x1D <= (unsigned int) exp ) {
;         if ( exp < 0 ) {
;             /*----------------------------------------------------------------
;             *----------------------------------------------------------------*/
;             isTiny =
;                 (softfloat_detectTininess == softfloat_tininess_beforeRounding)
;                     || (exp < -1) || (sig + roundIncrement < 0x8000);
;             sig = softfloat_shiftRightJam32( sig, -exp );
;             exp = 0;
;             roundBits = sig & 0xF;
;             if ( isTiny && roundBits ) {
;                 softfloat_raiseFlags( softfloat_flag_underflow );
;             }
;         } else if ( (0x1D < exp) || (0x8000 <= sig + roundIncrement) ) {
;             /*----------------------------------------------------------------
;             *----------------------------------------------------------------*/
;             softfloat_raiseFlags(
;                 softfloat_flag_overflow | softfloat_flag_inexact );
;             uiZ = packToF16UI( sign, 0x1F, 0 ) - ! roundIncrement;
;             goto uiZ;
;         }
;     }
;     /*------------------------------------------------------------------------
;     *------------------------------------------------------------------------*/
;     sig = (sig + roundIncrement)>>4;
;     if ( roundBits ) {
;         softfloat_exceptionFlags |= softfloat_flag_inexact;
; #ifdef SOFTFLOAT_ROUND_ODD
;         if ( roundingMode == softfloat_round_odd ) {
;             sig |= 1;
;             goto packReturn;
;         }
; #endif
;     }
;     sig &= ~(uint_fast16_t) (! (roundBits ^ 8) & roundNearEven);
;     if ( ! sig ) exp = 0;
;     /*------------------------------------------------------------------------
;     *------------------------------------------------------------------------*/
;  packReturn:
;     uiZ = packToF16UI( sign, exp, sig );
;  uiZ:
;     uZ.ui = uiZ;
;     return uZ.f;
; }


; ===============================================================================
; eZ80 Assembly Implementation
; Original C code has been simplified so that only the default rounding options 
; are used, and so branching tests are more ez80 friendly.
; ===============================================================================
; inputs: c = sign (0=pos, 0x80=neg), b = biased exp, hl = sig (implied 1 place in bit 14)
; outputs: hl = packed float16, c = sign (0=pos, 0x80=neg), b = biased exp
; destroys: af, de
softfloat_roundPackToF16:
; uint_fast8_t roundIncrement = 0x8;
; uint_fast8_t roundBits = sig & 0xF;
    ld a,b ; get exponent
; if (exp < 0) {
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
;     if (isTiny && roundBits) {
;         softfloat_raiseFlags(softfloat_flag_underflow);
;     }
        jr @do_rounding
; }
; else if (exp > 0x1D) {
@check_overflow:
    cp 0x1E
    jr nc,@return_inf
; }
; else if ((sig + roundIncrement) >= 0x8000) {
    ex de,hl ; preserve sig in de for upcoming test
    ld hl, 0x8000 - 0x0008 - 1 ; 0x8000 - roundIncrement - 1
    or a ; clear carry
    sbc hl,de ; sig + roundIncrement > 0x8000 
    ex de,hl ; restore sig to hl
    jr c,@return_inf ; return inf if sig + roundIncrement < 0x8000
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
;
    ; d == roundBits
    ld a,d
    cp 0x08
    jp nz,@check_sig_zero      ; Not exactly halfway -> skip
    ; Exactly halfway => round to even.
    bit 0,l                    ; Test LSB of HL
    jp z,@check_sig_zero       ; If LSB = 0 (already even), skip
    res 0,l                    ; Else clear LSB => rounding to even
    jp packToF16UI
;
; if (!sig) {
@check_sig_zero:

    call printHexHL
    ld a,d
    call printHexA
    call printNewLine

    SIGN_HL
    jp nz,packToF16UI ; skip if sign is zero
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
    ret
; end softfloat_roundPackToF16
