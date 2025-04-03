
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
; Original C code has been simplified so that only the default options are used.
; ===============================================================================
;  softfloat_roundPackToF16
; 
;  This function rounds and packs the fields for a 16‐bit floating‐point
;  value. It assumes:
;    - Default rounding mode is round‑nearest‑even.
;    - Tininess is detected before rounding.
; 
;  The algorithm is:
;    1. Set the round increment to 0x8 (because round‑nearest‑even).
;    2. Compute roundBits = sig & 0xF.
;    3. If exp is high enough (>= 0x1D):
;         a. For subnormals (exp < 0): shift sig right with “jam” by –exp,
;            set exp to 0, recompute roundBits, and raise underflow if any
;            roundBits are nonzero.
;         b. Otherwise, if exp is too high or the adjusted sig overflows,
;            raise overflow/inexact flags and pack an infinity (or max value).
;    4. Add the round increment to sig and shift right by 4 bits.
;    5. If any roundBits were set, mark the result as inexact.
;    6. Apply the round‑to‑even adjustment (clear the LSB if exactly tied).
;    7. If sig becomes zero, force exp to 0.
;    8. Pack the sign, exp, and sig into the final 16‐bit float.
; ------------------------------------------------------------------------------
; uint16_t softfloat_roundPackToF16( bool sign, int_fast16_t exp, uint_fast16_t sig )
; inputs: c = sign (0=pos, 0x80=neg), b = biased exp, hl = sig (implied 1 place in bit 14)
; destroys: af, de
softfloat_roundPackToF16:
; {
;     // Default: round-nearest-even mode; no need to check other rounding modes.
;     uint_fast8_t roundIncrement = 0x8;
;     uint_fast8_t roundBits = sig & 0xF;
;
;     /*----------------------------------------------------------------------
;      * If the exponent is high (>= 0x1D) we may need to adjust for subnormals
;      * or overflow.
;      *---------------------------------------------------------------------*/
;     if ( 0x1D <= (unsigned int) exp ) {
        ld a,b ; get exponent
        cp 0x1D ; exp >= 0x1D
        jp m,@do_rounding ; skip overflow check if exp < 0x1D

    ; call printHexHL
    ; call printBinHL
    ; call printNewLine

;         if ( exp < 0 ) {
            and a ; check for negative exponent
            jp p,@check_overflow ; skip if exp is positive
;             // Subnormal case: shift right with jam and detect tininess.
;             sig = softfloat_shiftRightJam32( sig, -exp );
                neg ; negate exponent
                ex de,hl ; move hl to lower bytes of the 32 bit argument
                ld hl,0 ; upper bytes of 32 bit argument to zero
                call softfloat_shiftRightJam32

    ; call printHexHL
    ; call printBinHL
    ; call printNewLine

                ex de,hl ; shifted/jammed sig back to hl
;             exp = 0;
                ld b,0
;             roundBits = sig & 0xF;
;             if ( roundBits ) {
;                 softfloat_raiseFlags( softfloat_flag_underflow );
;             }
;         } else if ( (0x1D < exp) || (0x8000 <= sig + roundIncrement) ) {
@check_overflow:
            cp 0x1E ; exp > 0x1D
            jp p,@do_rounding ; skip overflow check if exp <= 0x1D
            ex de,hl ; preserve sig in de for upcoming test
            ld hl, 0x8000 - 0x0080 ; 0x8000 - roundIncrement
            or a ; clear carry
            sbc hl,de ; sig + roundIncrement > 0x8000 
            ex de,hl ; restore sig to hl
            jp m,@do_rounding ; skip if sig + roundIncrement < 0x8000
;             // Overflow: raise flags and pack the maximum finite value.
;             softfloat_raiseFlags( softfloat_flag_overflow | softfloat_flag_inexact );
;             uiZ = packToF16UI( sign, 0x1F, 0 ) - !roundIncrement;
;             goto uiZ;
;         }
;     }

;     /*----------------------------------------------------------------------
;      * Round the significand: add the round increment, shift right by 4 bits,
;      * and if any discarded bits were nonzero, mark the result as inexact.
;      * Then, adjust for round-to-even (tie-breaker).
;      *---------------------------------------------------------------------*/
@do_rounding:
;     roundBits = sig & 0xF
        ld a,0x0F
        and l
        ld d,a ; store roundBits
;     sig = (sig + roundIncrement) >> 4;
        ld a,l
        add 0x08 ; add round increment
        ld l,a
        ld a,h
        adc a,0
        ld h,a

    ; call printHexHL
    ; call printBinHL
    ; call printNewLine

    ; shift right by 4 bits
        or a ; clear carry
    ; once
        rr h
        rr l
        or a
    ; twice
        rr h
        rr l
        or a
    ; thrice
        rr h
        rr l
        or a
    ; four times
        rr h
        rr l
;     if ( roundBits ) {
        ld a,d ; get round bits
        or a ; test for zero
        jr z,@check_even ; skip if round bits is zero
;         softfloat_exceptionFlags |= softfloat_flag_inexact;
;     }
;     // Round-to-even: if tie (i.e. roundBits exactly equal to 8), clear LSB.
;     sig &= ~(uint_fast16_t)(!(roundBits ^ 8));
@check_even:
        cp 0x08 ; check for tie
        jr nz,@check_exp_0 ; skip if round bits is not 0x08 (exactly halfway)
        res 0,l ; clear LSB
;     if ( ! sig ) {
@check_exp_0:
        SIGN_HL ; check for zero
        jp nz,@packReturn ; skip if not zero
;         exp = 0;
            ld b,0
;     }

@packReturn:
;     uiZ = packToF16UI( sign, exp, sig );
    jp packToF16UI
; end softfloat_roundPackToF16
