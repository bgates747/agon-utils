#!/usr/bin/env python3
from cffi import FFI
import struct
import numpy as np

# ----------------------------
# Pure Python Helpers
# ----------------------------
def signF16UI(a):
    """Extract sign bit from float16 (bit 15)."""
    return bool((a >> 15) & 1)

def expF16UI(a):
    """Extract exponent bits [14:10] from float16 and return as signed int."""
    return (a >> 10) & 0x1F  # Returns as int, not necessarily int_fast8_t

def fracF16UI(a):
    """Extract fraction (mantissa) bits [9:0] from float16."""
    return a & 0x03FF

# ----------------------------
# SoftFloat CFFI Setup
# ----------------------------
# Load the SoftFloat shared library using CFFI.

ffi = FFI()
ffi.cdef("""
    typedef uint16_t float16_t;
    typedef uint32_t float32_t;
    // Convert a 32-bit float (given as its bit pattern) to float16.
    float16_t f32_to_f16(float32_t a);
    // Multiply two float16 values.
    float16_t f16_mul(float16_t a, float16_t b);
    // Convert a float16 value to a float32 value.
    float32_t f16_to_f32(float16_t a);
    // Pack sign, exponent and sig to a float16.
    float16_t softfloat_roundPackToF16( bool sign, int_fast16_t exp, uint_fast16_t sig );
""")
lib = ffi.dlopen("/home/smith/Agon/mystuff/agon-utils/utils/SoftFloat-3e/build/Linux-x86_64-GCC/softfloat.so")

# ----------------------------
# SoftFloat Functions
# ----------------------------

def float_to_float32_bits(f):
    """Convert a Python float to its 32-bit IEEE 754 representation as an integer."""
    f32 = np.float32(f)
    return struct.unpack('<I', struct.pack('<f', f32))[0]

def float_to_f16_bits(val):
    """
    Uses SoftFloat's f32_to_f16 to convert a Python float (via its float32 bit pattern)
    to a 16-bit float representation.
    Returns a 16-bit integer.
    """
    bits32 = float_to_float32_bits(val)
    return lib.f32_to_f16(bits32)

def f16_mul_softfloat(a_f16, b_f16):
    """
    Multiplies two half-precision numbers (provided as 16-bit integers)
    using SoftFloat's f16_mul.
    Returns the 16-bit integer result.
    """
    return lib.f16_mul(a_f16, b_f16)

def f16_to_f32_softfloat(a_f16):
    """
    Uses SoftFloat's f16_to_f32 to convert a half-precision number (given as a 16-bit integer)
    into a 32-bit float (returned as a Python float).
    """
    bits32 = lib.f16_to_f32(a_f16)
    return struct.unpack('<f', struct.pack('<I', bits32))[0]

def float16_bits_to_float(f16_bits):
    """
    Convert a 16-bit integer (representing a float16) to a Python float using NumPy.
    """
    return np.array([f16_bits], dtype=np.uint16).view(np.float16)[0]

def f16_mul_python(a, b):
    """
    Convenience function: multiply two Python floats interpreted as float16,
    using SoftFloat's f16_mul, and return a Python float result.
    """
    a_bits = np.float16(a).view(np.uint16)
    b_bits = np.float16(b).view(np.uint16)
    res_bits = lib.f16_mul(a_bits, b_bits)
    return float16_bits_to_float(res_bits)

def softfloat_roundPackToF16(sign, exp, sig):
    """
    Pack sign, exponent, and significand into a float16 representation.
    """
    return lib.softfloat_roundPackToF16(sign, exp, sig)

def roundPackToF16(sign, exp, frac):
    """
    Pack sign, exponent, and fraction bits into a float16 value,
    handling the hidden bit and exponent adjustments automatically.
    
    Args:
        sign (bool): Sign bit (True for negative, False for positive)
        exp (int): Biased exponent bits (0-31)
        frac (int): Fraction bits (0-1023, the 10 LSBs of the significand)
        
    Returns:
        int: The packed float16 value as an integer
    """
    # Determine if this is a normalized number
    is_normalized = (exp != 0)
    
    # For normalized numbers, add hidden bit and adjust exponent
    if is_normalized:
        sig = ((0x0400 | frac) << 4)  # Include hidden bit and shift left 4 bits
        adjusted_exp = exp - 1  # Adjust exponent for normalization
    else:  # Subnormal number
        sig = (frac << 4)  # No hidden bit, but still shift for rounding bits
        adjusted_exp = exp  # No exponent adjustment needed
    
    # Special cases for zero, infinity, NaN
    if exp == 0 and frac == 0:  # Zero
        return 0 if not sign else 0x8000
    elif exp == 31:  # Infinity or NaN
        if frac == 0:  # Infinity
            return 0x7C00 if not sign else 0xFC00
        else:  # NaN
            return 0x7E00 if not sign else 0xFE00  # Quiet NaN
    
    # Normal case - call SoftFloat function
    return lib.softfloat_roundPackToF16(sign, adjusted_exp, sig)

def test_rounding(float16_hex, rounding_bits):
    """
    Three-line output format for rounding tests.
    
    Args:
        float16_hex (int): Float16 value in hex (e.g., 0x3C00 for 1.0)
        rounding_bits (int): 4-bit rounding value (0-15)
    """
    # Line 1: Extract components without shifting
    sign = signF16UI(float16_hex)
    exp = expF16UI(float16_hex)
    frac = fracF16UI(float16_hex)
    
    # Display original components without shifting
    print(f"Original:   0x{float16_hex:04x} Sign={sign}, Exp={exp}, Sig=0x{frac:04x} {format((float16_hex >> 8) & 0xFF, '08b')} {format(float16_hex & 0xFF, '08b')} ({float16_bits_to_float(float16_hex)})")
    
    # Line 2: Prepare significand with rounding bits
    is_normalized = (exp != 0)
    if is_normalized:
        sig = ((0x0400 | frac) << 4) | (rounding_bits & 0xF)
        adjusted_exp = exp - 1
    else:
        sig = (frac << 4) | (rounding_bits & 0xF)
        adjusted_exp = exp
    
    # Calculate the pre-rounded value with full float32 precision
    f16_value = float(np.float16(float16_bits_to_float(float16_hex)))  # Get as Python float
    
    if is_normalized:
        # For normalized values: 1 ULP = 2^-10 * 2^(exp-15)
        ulp_size = 2**(-10) * 2**(exp-15)
        rounding_fraction = rounding_bits / 16.0
        rounding_value = f16_value + (ulp_size * rounding_fraction)
    else:
        # For subnormal values
        ulp_size = 2**(-14) * 2**(exp-25)  # Adjusted for subnormals
        rounding_fraction = rounding_bits / 16.0
        rounding_value = f16_value + (ulp_size * rounding_fraction)
    
    # Display significand with rounding bits
    print(f"Prerounded:        Sign={sign}, Exp={adjusted_exp}, Sig=0x{sig:04x} {format((sig >> 8) & 0xFF, '08b')} {format(sig & 0xFF, '08b')} ({rounding_value:.10f})")
    
    # Line 3: Call rounding/packing function and display result
    result = lib.softfloat_roundPackToF16(sign, adjusted_exp, sig)
    
    # Display final result
    print(f"Rounded:    0x{result:04x} Sign={signF16UI(result)}, Exp={expF16UI(result)}, Sig=0x{fracF16UI(result):04x} {format((result >> 8) & 0xFF, '08b')} {format(result & 0xFF, '08b')} ({float16_bits_to_float(result)})")
    
    return result

# Example usage
if __name__ == "__main__":
    base_value = 0x3C00
    rounding_bits = 0b1001
    print(f"=== TEST WITH ROUNDING BITS 0b{rounding_bits:04b} ===")
    test_rounding(base_value, rounding_bits)