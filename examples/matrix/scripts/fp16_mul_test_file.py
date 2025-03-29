#!/usr/bin/env python3
import struct
import numpy as np
import os
from SoftFloat import (
    float_to_f16_bits,
    f16_mul_softfloat,
    f16_to_f32_softfloat,
    float16_bits_to_float,
    f16_mul_python
)

# ----------------------------
# Modified generate_valid_fp16 using SoftFloat conversion
# ----------------------------
def generate_valid_fp16(min_val, max_val):
    """
    Generates a number uniformly between min_val and max_val as a float64,
    converts it to float16 using SoftFloat, and returns the resulting value.
    (Additional rejection criteria can be added if desired.)
    """
    while True:
        candidate = np.random.uniform(min_val, max_val)
        candidate_f16 = float16_bits_to_float(float_to_f16_bits(candidate))
        # You can add extra checks here if desired.
        return candidate_f16

def generate_fp16_mul_test(N, op1_min, op1_max, op2_min, op2_max, outfile):
    data = bytearray()
    for i in range(N):
        # Step 1: Generate op1 within [op1_min, op1_max]
        op1 = generate_valid_fp16(op1_min, op1_max)

        # Step 2: Determine safe op2 range.
        # To avoid overflow, if op1 is nonzero, restrict op2_max to min( op2_max, 65504/abs(op1) ).
        if abs(op1) > 0:
            safe_op2_max = min(op2_max, 65504 / abs(op1))
        else:
            safe_op2_max = op2_max

        # Ensure that op2_min is less than safe_op2_max.
        if op2_min > safe_op2_max:
            safe_op2_max = op2_min

        # Step 3: Generate op2 within [op2_min, safe_op2_max]
        while True:
            op2 = generate_valid_fp16(op2_min, safe_op2_max)
            result = f16_mul_python(op1, op2)
            if not (np.isinf(result) or np.isnan(result)):
                break

        # Encode and store
        op1_rep = np.float16(op1).view(np.uint16)
        op2_rep = np.float16(op2).view(np.uint16)
        res_rep = np.float16(result).view(np.uint16)

        data += struct.pack('<HB', int(op1_rep), 0)
        data += struct.pack('<HB', int(op2_rep), 0)
        data += struct.pack('<HB', int(res_rep), 0)

        print(f"\r{i+1}/{N} generated", end='', flush=True)

    print()
    os.makedirs(os.path.dirname(outfile), exist_ok=True)
    with open(outfile, 'wb') as f:
        f.write(data)
    print(f"Wrote {N} test cases ({len(data)} bytes) to {outfile}")

# ----------------------------
# Main Execution
# ----------------------------
if __name__ == "__main__":
    NUM_TESTS = 10000
    # # Specify op1 range: e.g., between -10.0 and 10.0
    # OP1_MIN = 0.000000059604645 # smallest positive subnormal
    # OP1_MAX = 0.000060975552 # largest positive subnormal
    # # Specify op2 range: e.g., between -5.0 and 5.0
    # OP2_MIN = 1.00097656 # smallest positive normal
    # OP2_MAX = 10.0

    # Specify op1 range: e.g., between -10.0 and 10.0
    OP1_MIN = 1.0
    OP1_MAX = 10.0
    # Specify op2 range: e.g., between -5.0 and 5.0
    OP2_MIN = 1.0
    OP2_MAX = 1000.0

    GENERATE_OUTFILE = '/home/smith/Agon/mystuff/agon-utils/examples/matrix/tgt/fp16_mul_test.bin'
    generate_fp16_mul_test(NUM_TESTS, OP1_MIN, OP1_MAX, OP2_MIN, OP2_MAX, GENERATE_OUTFILE)
