#!/usr/bin/env python3
from cffi import FFI
import struct
import numpy as np

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
""")
# Adjust the path to your shared library as needed.
lib = ffi.dlopen("/home/smith/Agon/mystuff/agon-utils/utils/SoftFloat-3e/build/Linux-x86_64-GCC/softfloat.so")

# ----------------------------
# Helper conversion functions
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
