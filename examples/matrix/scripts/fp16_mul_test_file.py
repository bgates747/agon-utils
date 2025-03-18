#!/usr/bin/env python3
from cffi import FFI
import numpy as np
import struct
import os

# ----------------------------
# Initialize cffi and load SoftFloat
# ----------------------------
ffi = FFI()
ffi.cdef("""
    typedef uint16_t float16_t;
    typedef uint32_t float32_t;

    // Convert a 32-bit float (represented as uint32_t bits) to a 16-bit float.
    float16_t f32_to_f16(float32_t a);

    // Multiply two float16 numbers.
    float16_t f16_mul(float16_t a, float16_t b);
""")
# Adjust the path to your shared library as needed.
lib = ffi.dlopen("utils/SoftFloat-3e/build/Linux-x86_64-GCC/softfloat.so")

# ----------------------------
# Helper conversion functions
# ----------------------------
def float_to_float32_bits(f):
    """Convert a Python float to its 32-bit IEEE 754 representation as an integer."""
    f32 = np.float32(f)
    return struct.unpack('<I', struct.pack('<f', f32))[0]

def float16_bits_to_float(f16_bits):
    """Convert a 16-bit integer (representing a float16) to a Python float via numpy."""
    return np.array([f16_bits], dtype=np.uint16).view(np.float16)[0]

def float_to_f16_bits(val):
    """Use SoftFloat to convert a float32 value (provided as Python float) to float16 bits."""
    bits32 = float_to_float32_bits(val)
    return lib.f32_to_f16(bits32)

def f16_mul_python(a, b):
    """Multiply two float16 numbers using SoftFloat's f16_mul."""
    a_bits = np.float16(a).view(np.uint16)
    b_bits = np.float16(b).view(np.uint16)
    res_bits = lib.f16_mul(a_bits, b_bits)
    return float16_bits_to_float(res_bits)

# ----------------------------
# Modified generate_valid_fp16 using SoftFloat conversion
# ----------------------------
def generate_valid_fp16():
    """
    Generates a number uniformly between -65504 and 65504 as a float64,
    then converts it to a SoftFloat-based np.float16 using f32_to_f16.
    Rejects any candidate whose absolute value is strictly less than 0.01.
    """
    while True:
        candidate = np.random.uniform(-65504, 65504)
        # Use SoftFloat conversion instead of np.float16(candidate)
        candidate_f16 = float16_bits_to_float(float_to_f16_bits(candidate))
        if -0.01 < candidate_f16 < 0.01:
            continue
        return candidate_f16

# ----------------------------
# Modified test case generator using SoftFloat functions
# ----------------------------
def generate_fp16_mul_test(N, outfile):
    """
    Generates test cases for float16 multiplication.
    Each test case consists of:
      - operand1 (3 bytes): 2 bytes for float16 + 1 pad byte (0)
      - operand2 (3 bytes): 2 bytes for float16 + 1 pad byte (0)
      - result   (3 bytes): 2 bytes for float16 + 1 pad byte (0)
    
    Operands are generated with generate_valid_fp16. Their product is computed
    using f16_mul from SoftFloat. The pair is rejected if the result is NaN or infinity.
    """
    data = bytearray()
    for _ in range(N):
        while True:
            op1 = generate_valid_fp16()
            op2 = generate_valid_fp16()
            result = f16_mul_python(op1, op2)
            if np.isinf(result) or np.isnan(result):
                continue
            break

        op1_rep = np.float16(op1).view(np.uint16)
        op2_rep = np.float16(op2).view(np.uint16)
        res_rep = np.float16(result).view(np.uint16)
        
        # Pack each value into 3 bytes (2-byte little-endian + 1 pad byte 0)
        data += struct.pack('<HB', int(op1_rep), 0)
        data += struct.pack('<HB', int(op2_rep), 0)
        data += struct.pack('<HB', int(res_rep), 0)
    
    os.makedirs(os.path.dirname(outfile), exist_ok=True)
    with open(outfile, 'wb') as f:
        f.write(data)
    print(f"Wrote {N} test cases ({len(data)} bytes) to {outfile}")

# ----------------------------
# Main Execution
# ----------------------------
if __name__ == "__main__":
    NUM_TESTS = 1000
    GENERATE_OUTFILE = 'examples/matrix/tgt/fp16_mul_test.bin'
    generate_fp16_mul_test(NUM_TESTS, GENERATE_OUTFILE)
