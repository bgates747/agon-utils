#!/usr/bin/env python3
import struct
import numpy as np
import os
from SoftFloat import (float_to_f16_bits, float16_bits_to_float, f16_mul_python)

def generate_valid_fp16(min_val, max_val):
    while True:
        candidate = np.random.uniform(min_val, max_val)
        candidate_f16 = float16_bits_to_float(float_to_f16_bits(candidate))
        return candidate_f16

def generate_fp16_mul_test(N, op1_min, op1_max, op2_min, op2_max, outfile):
    data = bytearray()
    for i in range(N):
        op1 = generate_valid_fp16(op1_min, op1_max)

        # Absolute value of op1 for safe multiplication bounds
        abs_op1 = abs(op1)
        if abs_op1 > 0:
            max_safe_magnitude = 65504 / abs_op1
        else:
            max_safe_magnitude = float('inf')  # No overflow possible

        # Bound op2_min/op2_max against overflow-safe magnitude, preserving sign
        def clamp_to_safe_range(val):
            if val < 0:
                return max(val, -max_safe_magnitude)
            elif val > 0:
                return min(val, max_safe_magnitude)
            else:
                return 0.0

        safe_op2_min = clamp_to_safe_range(op2_min)
        safe_op2_max = clamp_to_safe_range(op2_max)

        # Fix broken user input where min > max
        if safe_op2_max < safe_op2_min:
            safe_op2_max = safe_op2_min

        while True:
            op2 = generate_valid_fp16(safe_op2_min, safe_op2_max)
            result = f16_mul_python(op1, op2)
            if not (np.isinf(result) or np.isnan(result)):
                break

        op1_rep = np.float16(op1).view(np.uint16)
        op2_rep = np.float16(op2).view(np.uint16)
        res_rep = np.float16(result).view(np.uint16)
        asm_placeholder = 0x0000  # Still not writing assembly for you

        data += struct.pack('<HHHH', int(op1_rep), int(op2_rep), int(res_rep), asm_placeholder)
        print(f"\r{i+1}/{N} generated", end='', flush=True)

    print()
    os.makedirs(os.path.dirname(outfile), exist_ok=True)
    with open(outfile, 'wb') as f:
        f.write(data)
    print(f"Wrote {N} test cases ({len(data)} bytes) to {outfile}")


if __name__ == "__main__":
    NUM_TESTS = 10000
    OP1_MIN = -65504.0
    OP1_MAX = 65504.0
    OP2_MIN = -65504.0
    OP2_MAX = 65504.0
    GENERATE_OUTFILE = '/home/smith/Agon/mystuff/agon-utils/examples/matrix/tgt/fp16_mul_test.bin'

    generate_fp16_mul_test(NUM_TESTS, OP1_MIN, OP1_MAX, OP2_MIN, OP2_MAX, GENERATE_OUTFILE)
