#!/usr/bin/env python3
import struct
import numpy as np
import os
from SoftFloat import (float_to_f16_bits, float16_bits_to_float, f16_mul_python)

SPECIALS = [-np.nan, np.inf, -np.inf, 0.0, -0.0]

def generate_valid_fp16(min_val, max_val):
    if np.random.rand() < FREQ_SPECIALS:
        return np.random.choice(SPECIALS)
    
    candidate = np.random.uniform(min_val, max_val)
    if np.random.rand() < 0.5:
        candidate = -candidate
    candidate_f16 = float16_bits_to_float(float_to_f16_bits(candidate))
    return candidate_f16

def generate_fp16_mul_test(N, op1_min, op1_max, op2_min, op2_max, outfile):
    data = bytearray()
    for i in range(N):
        op1 = generate_valid_fp16(op1_min, op1_max)
        op2 = generate_valid_fp16(op2_min, op2_max)

        result = f16_mul_python(op1, op2)

        op1_rep = np.float16(op1).view(np.uint16)
        op2_rep = np.float16(op2).view(np.uint16)
        res_rep = np.float16(result).view(np.uint16)
        asm_placeholder = 0x0000  # This is your problem now

        data += struct.pack('<HHHH', int(op1_rep), int(op2_rep), int(res_rep), asm_placeholder)
        print(f"\r{i+1}/{N} generated", end='', flush=True)

    print()
    os.makedirs(os.path.dirname(outfile), exist_ok=True)
    with open(outfile, 'wb') as f:
        f.write(data)
    print(f"Wrote {N} test cases ({len(data)} bytes) to {outfile}")

if __name__ == "__main__":
# Passed 100%
    # NUM_TESTS = 1000000
    # OP1_MIN = 0.0
    # OP1_MAX = 2.0
    # OP2_MIN = 0.0
    # OP2_MAX = 65504.0

    NUM_TESTS = 1000000
    OP1_MIN = 0.0
    OP1_MAX = 1.0
    OP2_MIN = 0.0
    OP2_MAX = 2.0
    FREQ_SPECIALS = 0.1

    GENERATE_OUTFILE = '/home/smith/Agon/mystuff/agon-utils/examples/matrix/tgt/fp16_mul_test.bin'

    generate_fp16_mul_test(NUM_TESTS, OP1_MIN, OP1_MAX, OP2_MIN, OP2_MAX, GENERATE_OUTFILE)
