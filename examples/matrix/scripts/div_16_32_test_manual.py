from typing import Tuple

# Constants from SoftFloat spec
defaultNaNF16UI = 0xFE00

def softfloat_propagateNaNF16UI(uiA: int, uiB: int) -> int:
    return 0xFE00  # canonical NaN, no questions asked

def packToF16UI(sign: int, exp: int, sig: int) -> int:
    return ((sign & 0x1) << 15) | ((exp & 0x1F) << 10) | (sig & 0x03FF)

def softfloat_roundPackToF16(sign: int, exp: int, sig: int) -> int:
    """
    Round and pack sign, exponent, and significand into a float16 value.
    Implements round-to-nearest-even only.
    Assumes `sig` is left-aligned with 4 guard bits (i.e., shifted << 4).
    """
    roundBits = sig & 0xF
    roundIncrement = 0x8  # round to nearest even
    
    # Shift into position with rounding
    # sig = (sig + roundIncrement) >> 4

    # Round to even: if the lower 4 bits were exactly 0b1000, round to even
    if roundBits == 0x8:
        sig &= ~1  # clear LSB to round to even

    # If result rounds to zero, flush exponent
    if sig == 0:
        exp = 0

    # Handle overflow (max exp for float16 is 0x1F, so max normal exp is 0x1D)
    if exp >= 0x1F:
        return packToF16UI(sign, 0x1F, 0)  # Infinity

    return packToF16UI(sign, exp, sig)

def softfloat_countLeadingZeros16(x: int) -> int:
    """Counts the number of leading zero bits in a 16-bit integer."""
    return 16 - x.bit_length() if x != 0 else 16

def softfloat_normSubnormalF16Sig(sig: int) -> Tuple[int, int]:
    """
    Normalize a subnormal float16 significand.
    
    Returns:
        (exp, sig) where:
        - exp is the corrected exponent
        - sig is the left-shifted normalized significand
    """
    shiftDist = softfloat_countLeadingZeros16(sig) - 5
    exp = 1 - shiftDist
    sig <<= shiftDist
    return exp, sig

# Utility functions
def signF16UI(a): return bool((a >> 15) & 1)
def expF16UI(a): return (a >> 10) & 0x1F
def fracF16UI(a): return a & 0x03FF
def u16(x): return x & 0xFFFF
def u24(x): return x & 0xFFFFFF
def u32(x): return x & 0xFFFFFFFF
def s32(x): return x if x < 0x80000000 else x - 0x100000000
def shr32(x, n): return u32(x >> n)
def shr24(x, n): return u24(x >> n)
def mul16x16(a, b): return u32(a * b)
def mul16x8(a, b): return u24(a * b)

softfloat_approxRecip_1k0s = [
    0xFFC4, 0xF0BE, 0xE363, 0xD76F,
    0xCCAD, 0xC2F0, 0xBA16, 0xB201,
    0xAA97, 0xA3C6, 0x9D7A, 0x97A6,
    0x923C, 0x8D32, 0x887E, 0x8417
]

softfloat_approxRecip_1k1s = [
    0xF0F1, 0xD62C, 0xBFA1, 0xAC77,
    0x9C0A, 0x8DDB, 0x8185, 0x76BA,
    0x6D3B, 0x64D4, 0x5D5C, 0x56B1,
    0x50B6, 0x4B55, 0x4679, 0x4211
]
def f16_div(a: int, b: int) -> int:
    print(f"\n--- f16_div(a=0x{a:04X}, b=0x{b:04X}) ---")

    uiA = a
    uiB = b

    signA = signF16UI(uiA)
    expA  = expF16UI(uiA)
    sigA  = fracF16UI(uiA)
    signB = signF16UI(uiB)
    expB  = expF16UI(uiB)
    sigB  = fracF16UI(uiB)
    signZ = signA ^ signB

    print(f"  A: sign={signA}, exp={expA}, sig=0x{sigA:03X}")
    print(f"  B: sign={signB}, exp={expB}, sig=0x{sigB:03X}")

    if expA == 0x1F:
        if sigA:
            return softfloat_propagateNaNF16UI(uiA, uiB)
        if expB == 0x1F:
            if sigB:
                return softfloat_propagateNaNF16UI(uiA, uiB)
            return packToF16UI(1, 0x1F, 1)  # Invalid (inf / inf)
        return packToF16UI(signZ, 0x1F, 0)

    if expB == 0x1F:
        if sigB:
            return softfloat_propagateNaNF16UI(uiA, uiB)
        return packToF16UI(signZ, 0, 0)

    if expB == 0:
        if sigB == 0:
            if expA == 0 and sigA == 0:
                return packToF16UI(1, 0x1F, 1)  # Invalid (0/0)
            return packToF16UI(signZ, 0x1F, 0)
        expB, sigB = softfloat_normSubnormalF16Sig(sigB)

    if expA == 0:
        if sigA == 0:
            return packToF16UI(signZ, 0, 0)
        expA, sigA = softfloat_normSubnormalF16Sig(sigA)

    expZ = expA - expB + 0xE
    sigA |= 0x0400
    sigB |= 0x0400

    print(f"  Normalized sigA = 0x{sigA:04X}, sigB = 0x{sigB:04X}, expZ = {expZ}")

    if sigA < sigB:
        expZ -= 1
        sigA <<= 5
        print(f"  sigA << 5 = 0x{sigA:08X} (sigA < sigB)")
    else:
        sigA <<= 4
        print(f"  sigA << 4 = 0x{sigA:08X} (sigA >= sigB)")

    index = (sigB >> 6) & 0xF
    offset = sigB & 0x3F
    lut0 = softfloat_approxRecip_1k0s[index]
    lut1 = softfloat_approxRecip_1k1s[index]
    correction = shr24(mul16x8(lut1, offset), 10)
    r0 = u16(lut0 - correction)

    print(f"  Index = {index}, offset = 0x{offset:02X}")
    print(f"  LUT0 = 0x{lut0:04X}, LUT1 = 0x{lut1:04X}")
    print(f"  Correction = 0x{correction:04X}, r0 = 0x{r0:04X}")

    # Full 32-bit product, no premature shifts
    sigZ = mul16x16(sigA & 0xFFFF, r0)  # still in 32-bit fixed format

    sigZ_estimate = shr32(sigZ, 16)
    sigZ_sigB = mul16x16(sigZ_estimate, sigB)
    rem = u32((sigA << 10) - sigZ_sigB)

    refinement = shr32(u32(s32(rem) * r0), 26)
    sigZ += refinement << 16
    sigZ += 1 << 16  # increment

    print(f"  sigZ_estimate = 0x{sigZ_estimate:04X}")
    print(f"  refinement = 0x{refinement:04X}")
    print(f"  sigZ (after refinement & +1) = 0x{sigZ:08X}")

    sigZ_final = shr32(sigZ, 12)  # keep 16.4 fixed-point for roundPack
    print(f"  sigZ_final (16.4 fixed) = 0x{sigZ_final:05X}")

    if not (sigZ_final & 0x7):
        sigZ_final &= ~1
        rem2 = u32((sigA << 10) - mul16x16(sigZ_final >> 4, sigB))
        print(f"  Alignment check: rem2 = 0x{rem2:08X}")
        if rem2 & 0x80000000:
            sigZ_final -= 2
            print(f"  rem2 negative → sigZ corrected to 0x{sigZ_final:05X}")
        elif rem2 != 0:
            sigZ_final |= 1
            print(f"  rem2 non-zero → sigZ |= 1 → 0x{sigZ_final:05X}")

    print(f"  Final sigZ = 0x{sigZ_final:05X}, expZ = {expZ}, signZ = {signZ}")
    return softfloat_roundPackToF16(signZ, expZ, sigZ_final)

if __name__ == "__main__":
    # Example: 10.0 / 2.0 in float16
    a = 0x4900  # float16 representation of 10.0
    b = 0x4000  # float16 representation of 2.0
    result = f16_div(a, b)
    print(f"\nResult: 0x{result:04X}")
