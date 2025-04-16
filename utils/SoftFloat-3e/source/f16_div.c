
/*============================================================================

This C source file is part of the SoftFloat IEEE Floating-Point Arithmetic
Package, Release 3e, by John R. Hauser.

Copyright 2011, 2012, 2013, 2014, 2015, 2016 The Regents of the University of
California.  All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

 1. Redistributions of source code must retain the above copyright notice,
    this list of conditions, and the following disclaimer.

 2. Redistributions in binary form must reproduce the above copyright notice,
    this list of conditions, and the following disclaimer in the documentation
    and/or other materials provided with the distribution.

 3. Neither the name of the University nor the names of its contributors may
    be used to endorse or promote products derived from this software without
    specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS "AS IS", AND ANY
EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE, ARE
DISCLAIMED.  IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

=============================================================================*/

#include <stdbool.h>
#include <stdint.h>
#include "platform.h"
#include "internals.h"
#include "specialize.h"
#include "softfloat.h"
// #include <stdio.h>

extern const uint16_t softfloat_approxRecip_1k0s[];
extern const uint16_t softfloat_approxRecip_1k1s[];

float16_t f16_div( float16_t a, float16_t b )
{
    union ui16_f16 uA;
    uint_fast16_t uiA;
    bool signA;
    int_fast8_t expA;
    uint_fast16_t sigA;
    union ui16_f16 uB;
    uint_fast16_t uiB;
    bool signB;
    int_fast8_t expB;
    uint_fast16_t sigB;
    bool signZ;
    struct exp8_sig16 normExpSig;
    int_fast8_t expZ;
#ifdef SOFTFLOAT_FAST_DIV32TO16
    uint_fast32_t sig32A;
    uint_fast16_t sigZ;
#else
    int index;
    uint16_t r0;
    uint_fast16_t sigZ, rem;
#endif
    uint_fast16_t uiZ;
    union ui16_f16 uZ;

    /*------------------------------------------------------------------------
    *------------------------------------------------------------------------*/
    uA.f = a;
    uiA = uA.ui;
    signA = signF16UI( uiA );
    expA  = expF16UI( uiA );
    sigA  = fracF16UI( uiA );
    uB.f = b;
    uiB = uB.ui;
    signB = signF16UI( uiB );
    expB  = expF16UI( uiB );
    sigB  = fracF16UI( uiB );
    signZ = signA ^ signB;

    // printf("f16_div - signA: %s, expA: 0x%02X, sigA: 0x%04X %%.%08b_%08b\n", 
        // signA ? "true" : "false", 
        // (unsigned int)(expA & 0xFF), 
        // sigA,
        // (unsigned int)((sigA >> 8) & 0xFF),
        // (unsigned int)(sigA & 0xFF));
    // printf("f16_div - signB: %s, expB: 0x%02X, sigB: 0x%04X %%.%08b_%08b\n",
        // signB ? "true" : "false", 
        // (unsigned int)(expB & 0xFF), 
        // sigB,
        // (unsigned int)((sigB >> 8) & 0xFF),
        // (unsigned int)(sigB & 0xFF));
    /*------------------------------------------------------------------------
    *------------------------------------------------------------------------*/
    if ( expA == 0x1F ) {
        if ( sigA ) goto propagateNaN;
        if ( expB == 0x1F ) {
            if ( sigB ) goto propagateNaN;
            goto invalid;
        }
        goto infinity;
    }
    if ( expB == 0x1F ) {
        if ( sigB ) goto propagateNaN;
        goto zero;
    }
    /*------------------------------------------------------------------------
    *------------------------------------------------------------------------*/
    if ( ! expB ) {
        if ( ! sigB ) {
            if ( ! (expA | sigA) ) goto invalid;
            softfloat_raiseFlags( softfloat_flag_infinite );
            goto infinity;
        }
        normExpSig = softfloat_normSubnormalF16Sig( sigB );
        expB = normExpSig.exp;
        sigB = normExpSig.sig;
    }
    if ( ! expA ) {
        if ( ! sigA ) goto zero;
        normExpSig = softfloat_normSubnormalF16Sig( sigA );
        expA = normExpSig.exp;
        sigA = normExpSig.sig;
    }
    /*------------------------------------------------------------------------
    *------------------------------------------------------------------------*/
    expZ = expA - expB + 0xE;
    sigA |= 0x0400;
    sigB |= 0x0400;
#ifdef SOFTFLOAT_FAST_DIV32TO16
    if ( sigA < sigB ) {
        --expZ;
        sig32A = (uint_fast32_t) sigA<<15;
    } else {
        sig32A = (uint_fast32_t) sigA<<14;
    }
    sigZ = sig32A / sigB;
    if ( ! (sigZ & 7) ) sigZ |= ((uint_fast32_t) sigB * sigZ != sig32A);
#else
    if ( sigA < sigB ) {
        --expZ;
        sigA <<= 5;
    } else {
        sigA <<= 4;
    }
    index = sigB>>6 & 0xF;
    r0 = softfloat_approxRecip_1k0s[index]
             - (((uint_fast32_t) softfloat_approxRecip_1k1s[index]
                     * (sigB & 0x3F))
                    >>10);
    sigZ = ((uint_fast32_t) sigA * r0)>>16;
    rem = (sigA<<10) - sigZ * sigB;
    sigZ += (rem * (uint_fast32_t) r0)>>26;
    /*------------------------------------------------------------------------
    *------------------------------------------------------------------------*/
    ++sigZ;
    // printf("0x%08X   sigA\n", sigA);
    // printf("0x%08X   sigB\n", sigB);
    // printf("0x%08X ++sigZ\n", sigZ);
    if ( ! (sigZ & 7) ) {
        sigZ &= ~1;
        // printf("0x%08X sigZ &= ~1\n", sigZ);
        rem = (sigA<<10) - sigZ * sigB;
        // printf("0x%08X sigA<<10\n", (sigA<<10));
        // printf("0x%08X sigZ * sigB\n", sigZ * sigB);
        // printf("0x%08X rem\n", rem);
        if ( rem & 0x8000 ) {
            sigZ -= 2;
            // printf("0x%08X sigZ -= 2\n", sigZ);
        } else {
            if ( rem ) sigZ |= 1;
            // printf("0x%08X sigZ |= 1\n", sigZ);
        }
    }
#endif
    return softfloat_roundPackToF16( signZ, expZ, sigZ );
    /*------------------------------------------------------------------------
    *------------------------------------------------------------------------*/
 propagateNaN:
    uiZ = softfloat_propagateNaNF16UI( uiA, uiB );
    goto uiZ;
    /*------------------------------------------------------------------------
    *------------------------------------------------------------------------*/
 invalid:
    softfloat_raiseFlags( softfloat_flag_invalid );
    uiZ = defaultNaNF16UI;
    goto uiZ;
    /*------------------------------------------------------------------------
    *------------------------------------------------------------------------*/
 infinity:
    uiZ = packToF16UI( signZ, 0x1F, 0 );
    goto uiZ;
    /*------------------------------------------------------------------------
    *------------------------------------------------------------------------*/
 zero:
    uiZ = packToF16UI( signZ, 0, 0 );
 uiZ:
    uZ.ui = uiZ;
    return uZ.f;

}

