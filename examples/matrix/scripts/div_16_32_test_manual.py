#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SoftFloat float16 arithmetic emulation in Python using fixed‐width helpers.
This script re‐implements the SoftFloat f16_div (float16 division)
and associated helper routines while managing proper bitwise integer
manipulations through the following utility functions.
"""

# ----------------------------
# Utility functions
# ----------------------------
def signF16UI(a): 
    return bool((a >> 15) & 1)

def expF16UI(a): 
    return (a >> 10) & 0x1F

def fracF16UI(a): 
    return a & 0x03FF

def u16(x): 
    return x & 0xFFFF

def u24(x): 
    return x & 0xFFFFFF

def u32(x): 
    return x & 0xFFFFFFFF

def s32(x): 
    return x if x < 0x80000000 else x - 0x100000000

def shr32(x, n): 
    return u32(x >> n)

def shr24(x, n): 
    return u24(x >> n)

def mul16x16(a, b): 
    return u32(a * b)

def mul16x8(a, b): 
    return u24(a * b)


# ----------------------------
# SoftFloat Setup and Globals
# ----------------------------

# Lookup table for count-leading-zeros in an 8-bit value.
softfloat_countLeadingZeros8 = [
    8, 7, 6, 6, 5, 5, 5, 5, 4, 4, 4, 4, 4, 4, 4, 4,
    3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3,
    2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
    2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
]

# Rounding mode constants (used by SoftFloat)
softfloat_roundingMode      = 0
softfloat_round_near_even   = 0
softfloat_round_minMag      = 1
softfloat_round_min         = 2
softfloat_round_max         = 3
softfloat_round_near_maxMag = 4
softfloat_round_odd         = 6

# Tininess detection mode constants
softfloat_detectTininess = 0
softfloat_tininess_beforeRounding = 0
softfloat_tininess_afterRounding  = 1

# Exception flag variables
softfloat_exceptionFlags = 0
softfloat_flag_inexact   = 1
softfloat_flag_underflow = 2
softfloat_flag_overflow  = 4
softfloat_flag_infinite  = 8
softfloat_flag_invalid   = 16

def softfloat_raiseFlags(flags):
    global softfloat_exceptionFlags
    softfloat_exceptionFlags |= flags


# ----------------------------
# SoftFloat Routines
# ----------------------------
# Represents C's 'struct exp8_sig16' containing an 8-bit exponent and 16-bit significand.
class exp8_sig16:
    def __init__(self, exp=0, sig=0):
        self.exp = exp
        self.sig = sig

def softfloat_countLeadingZeros16(a):
    # Ensure a is 16-bit.
    a = u16(a)
    count = 8
    if a >= 0x100:
        count = 0
        a = a >> 8
    return count + softfloat_countLeadingZeros8[a]

def softfloat_normSubnormalF16Sig(sig):
    shiftDist = softfloat_countLeadingZeros16(sig) - 5
    z = exp8_sig16()
    z.exp = 1 - shiftDist
    z.sig = u16(sig << shiftDist)
    return z

def packToF16UI(sign, exp, sig):
    # Pack sign, exponent, and significand into a 16-bit value.
    return u16((int(sign) << 15) + (exp << 10) + sig)

def softfloat_shiftRightJam32(a, dist):
    a = u32(a)
    if dist < 31:
        shifted = shr32(a, dist)
        # Check if any bits are shifted out.
        remainder = u32(a << ((-dist) & 31))
        jam = 1 if remainder != 0 else 0
        return u32(shifted | jam)
    else:
        return 1 if a != 0 else 0

# A minimal mimic of the C union: 'union ui16_f16'
class ui16_f16:
    def __init__(self, ui=0):
        self.ui = u16(ui)
        # 'f' field simply holds the same 16-bit integer.
        self.f = u16(ui)

def softfloat_roundPackToF16(sign, exp, sig):
    roundingMode = softfloat_roundingMode
    roundNearEven = (roundingMode == softfloat_round_near_even)
    roundIncrement = 0x8
    if (not roundNearEven) and (roundingMode != softfloat_round_near_maxMag):
        if roundingMode == (softfloat_round_min if sign else softfloat_round_max):
            roundIncrement = 0xF
        else:
            roundIncrement = 0
    roundBits = sig & 0xF

    if 0x1D <= exp:
        if exp < 0:
            isTiny = ((softfloat_detectTininess == softfloat_tininess_beforeRounding) or
                      (exp < -1) or (sig + roundIncrement < 0x8000))
            sig = softfloat_shiftRightJam32(sig, -exp)
            exp = 0
            roundBits = sig & 0xF
            if isTiny and roundBits:
                softfloat_raiseFlags(softfloat_flag_underflow)
        elif (0x1D < exp) or (0x8000 <= sig + roundIncrement):
            softfloat_raiseFlags(softfloat_flag_overflow | softfloat_flag_inexact)
            # Note: In C: subtract (!roundIncrement). Here we subtract 0 if roundIncrement nonzero, else 1.
            uiZ = packToF16UI(sign, 0x1F, 0) - (0 if roundIncrement else 1)
            return ui16_f16(uiZ).f

    sig = (sig + roundIncrement) >> 4
    if roundBits:
        softfloat_exceptionFlags |= softfloat_flag_inexact

    if (roundBits ^ 0x8) == 0 and roundNearEven:
        sig = sig & ~1

    if not sig:
        exp = 0

    uiZ = packToF16UI(sign, exp, sig)
    return ui16_f16(uiZ).f

defaultNaNF16UI = 0xFE00
def softfloat_propagateNaNF16UI(uiA, uiB):
    return defaultNaNF16UI

softfloat_approxRecip_1k0s = [
    0xFFC4, 0xF0BE, 0xE363, 0xD76F, 0xCCAD, 0xC2F0, 0xBA16, 0xB201,
    0xAA97, 0xA3C6, 0x9D7A, 0x97A6, 0x923C, 0x8D32, 0x887E, 0x8417
]
softfloat_approxRecip_1k1s = [
    0xF0F1, 0xD62C, 0xBFA1, 0xAC77, 0x9C0A, 0x8DDB, 0x8185, 0x76BA,
    0x6D3B, 0x64D4, 0x5D5C, 0x56B1, 0x50B6, 0x4B55, 0x4679, 0x4211
]

def f16_div(opA, opB):
    """
    Divide two float16 numbers (in 16-bit integer representation)
    using the SoftFloat algorithm.
    
    opA: dividend (16-bit integer bit pattern)
    opB: divisor  (16-bit integer bit pattern)
    Returns: the 16-bit integer representation of the quotient.
    """

    # ----------------------------
    # Unpack opA
    # ----------------------------
    uA = ui16_f16(opA)
    uiA = uA.ui
    signA = signF16UI(uiA)
    expA  = expF16UI(uiA)
    sigA  = fracF16UI(uiA)

    # Normalize subnormal A if needed
    if expA == 0 and sigA != 0:
        raw_expA = expA
        raw_sigA = sigA
        normExpSig = softfloat_normSubnormalF16Sig(sigA)
        expA = normExpSig.exp
        sigA = normExpSig.sig
        print(f'opA: sign=0x{int(signA):02X}, exp=0x{raw_expA:02X}, sig=0x{raw_sigA:04X}: after norm: exp=0x{expA & 0xFF:02X}, sig=0x{sigA:04X}')
    else:
        print(f'opA: sign=0x{int(signA):02X}, exp=0x{expA:02X}, sig=0x{sigA:04X}')

    # ----------------------------
    # Unpack opB
    # ----------------------------
    uB = ui16_f16(opB)
    uiB = uB.ui
    signB = signF16UI(uiB)
    expB  = expF16UI(uiB)
    sigB  = fracF16UI(uiB)

    # Normalize subnormal B if needed
    if expB == 0 and sigB != 0:
        raw_expB = expB
        raw_sigB = sigB
        normExpSig = softfloat_normSubnormalF16Sig(sigB)
        expB = normExpSig.exp
        sigB = normExpSig.sig
        print(f'opB: sign=0x{int(signB):02X}, exp=0x{raw_expB:02X}, sig=0x{raw_sigB:04X}: after norm: exp=0x{expB & 0xFF:02X}, sig=0x{sigB:04X}')
    else:
        print(f'opB: sign=0x{int(signB):02X}, exp=0x{expB:02X}, sig=0x{sigB:04X}')

    # ----------------------------
    # Proceed with division
    # ----------------------------
    signZ = signA ^ signB

    # Handle special cases where one operand is NaN or Infinity.
    if expA == 0x1F:
        if sigA != 0:
            # A is NaN → return canonical NaN
            uiZ = softfloat_propagateNaNF16UI(uiA, uiB)
            return ui16_f16(uiZ).f
        else:
            # A is Infinity
            if expB == 0x1F:
                # B is Infinity or NaN
                if sigB != 0:
                    # B is NaN → return NaN
                    uiZ = softfloat_propagateNaNF16UI(uiA, uiB)
                    return ui16_f16(uiZ).f
                else:
                    # Inf / Inf → invalid → return NaN
                    softfloat_raiseFlags(softfloat_flag_invalid)
                    uiZ = defaultNaNF16UI
                    return ui16_f16(uiZ).f
            # inf / x = inf (for any non-inf, non-NaN x)
            uiZ = packToF16UI(signZ, 0x1F, 0)
            return ui16_f16(uiZ).f

    if expB == 0x1F:
        if sigB != 0:
            # B is NaN → return NaN
            uiZ = softfloat_propagateNaNF16UI(uiA, uiB)
            return ui16_f16(uiZ).f
        # B is Infinity → finite / Inf = 0
        uiZ = packToF16UI(signZ, 0, 0)
        return ui16_f16(uiZ).f

    # B == 0 → handle zero divisor
    if expB == 0 and sigB == 0:
        # B is exactly zero
        if expA == 0 and sigA == 0:
            # 0 / 0 → NaN
            softfloat_raiseFlags(softfloat_flag_invalid)
            uiZ = defaultNaNF16UI
            return ui16_f16(uiZ).f
        # finite-nonzero / 0 → Infinity
        softfloat_raiseFlags(softfloat_flag_infinite)
        uiZ = packToF16UI(signZ, 0x1F, 0)
        return ui16_f16(uiZ).f
    
    # A == 0 → handle zero numerator
    if expA == 0 and sigA == 0:
        # 0 / non-zero → 0
        uiZ = packToF16UI(signZ, 0, 0)
        return ui16_f16(uiZ).f

    # ----------------------------
    # Now do the normal division path
    # ----------------------------
    expZ = expA - expB + 0xE
    sigA |= 0x0400
    sigB |= 0x0400

    if sigA < sigB:
        expZ = expZ - 1
        numShifts = 5
    else:
        numShifts = 4

    sigA = u16(sigA << numShifts)

    index = (sigB >> 6) & 0xF

    approx1k0s = softfloat_approxRecip_1k0s[index]
    approx1k1s = softfloat_approxRecip_1k1s[index]

    r0 = approx1k0s - (((approx1k1s * (sigB & 0x3F)) >> 10))

    sigZ = u32((sigA * r0) >> 16)

    rem  = u32((sigA << 10) - sigZ * sigB)

    rem_r0 = (rem * r0) >> 26

    sigZ += (rem_r0)

    sigZ = sigZ + 1
    if (sigZ & 7) == 0:
        sigZ = sigZ & ~1
        rem = u32((sigA << 10) - sigZ * sigB)
        if (rem & 0x8000) != 0:
            sigZ = sigZ - 2
        else:
            if rem != 0:
                sigZ = sigZ | 1

    return softfloat_roundPackToF16(signZ, expZ, sigZ)

def parse_float16_input(x):
    """
    Converts input `x` (string, float, int, or hex) to a float16 bit pattern (uint16).
    Accepts:
        - Float literals: 65504.0
        - Special strings: 'inf', '-inf', 'nan'
        - Hex strings: '0x7BFF', 'FE00'
        - Integers: 0x7BFF
    Returns:
        uint16 representing the float16 bit pattern
    """
    if isinstance(x, float):
        return int(np.float16(x).view(np.uint16))
    elif isinstance(x, int):
        return x & 0xFFFF
    elif isinstance(x, str):
        x = x.strip().lower()
        if x.startswith("0x"):
            return int(x, 16) & 0xFFFF
        try:
            val = float(x)
            return int(np.float16(val).view(np.uint16))
        except ValueError:
            raise ValueError(f"Invalid input: {x!r}")
    else:
        raise TypeError(f"Unsupported type for input: {type(x)}")



if __name__ == "__main__":
    import numpy as np

    # Input as Python float literals
    valA = 'inf'
    valB = 0.0

    # Convert to float16 bit patterns using NumPy
    opA = parse_float16_input(valA)
    opB = parse_float16_input(valB)

    print('----- DEBUG OUTPUT -----')

    # Perform the division using your SoftFloat-emulated f16_div
    result = f16_div(opA, opB)

    # Convert result back to Python float using NumPy
    valR = float(np.array([result], dtype=np.uint16).view(np.float16)[0])
    print(f'0x{opA:04X} / 0x{opB:04X} = 0x{result:04X}')


    # Output
    print(f'\r\n----- ASSEMBLY OUTPUT -----')
    print(f'    call printInline')
    print(f'    asciz "{valA} / {valB} = {valR}\\r\\n"')
    print(f'    call printInline')
    print(f'    asciz "0x{opA:04X} / 0x{opB:04X} = 0x{result:04X}\\r\\n"')
    print(f'    ld hl,0x{opA:04X} ; {valA}')
    print(f'    ld de,0x{opB:04X} ; {valB}')
    print(f'    call f16_div')
    print(f'    PRINT_HL_HEX " assembly result"')
    print(f'    call printNewLine')
