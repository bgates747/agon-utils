
/*============================================================================

This C source file is part of the SoftFloat IEEE Floating-Point Arithmetic
Package, Release 3e, by John R. Hauser.

Copyright 2011, 2012, 2013, 2014, 2015 The Regents of the University of
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

#include <stdint.h>
#include "platform.h"
#include "specialize.h"
#include "softfloat.h"

// /*----------------------------------------------------------------------------
// | Assuming `uiA' has the bit pattern of a 16-bit floating-point NaN, converts
// | this NaN to the common NaN form, and stores the resulting common NaN at the
// | location pointed to by `zPtr'.  If the NaN is a signaling NaN, the invalid
// | exception is raised.
// *----------------------------------------------------------------------------*/
// void softfloat_f16UIToCommonNaN( uint_fast16_t uiA, struct commonNaN *zPtr )
// {

//     if ( softfloat_isSigNaNF16UI( uiA ) ) {
//         softfloat_raiseFlags( softfloat_flag_invalid );
//     }
//     zPtr->sign = uiA>>15;
//     zPtr->v64  = (uint_fast64_t) uiA<<54;
//     zPtr->v0   = 0;

// }

void softfloat_f16UIToCommonNaN(uint_fast16_t uiA, struct commonNaN *zPtr)
{
    if (softfloat_isSigNaNF16UI(uiA)) {
        softfloat_raiseFlags(softfloat_flag_invalid);
    }

    // Force canonical NaN: sign = 1, payload = 0xFE00 << 54
    zPtr->sign = 1;
    zPtr->v64  = (uint_fast64_t)defaultNaNF16UI << 54;
    zPtr->v0   = 0;
}

