from SoftFloat import (
    float_to_f16_bits,
    f16_mul_softfloat,
    f16_to_f32_softfloat,
    float16_bits_to_float,
    f16_mul_python
)
import numpy as np
import struct
import os

# ----------------------------
# Modified generate_valid_fp16 using SoftFloat conversion
# ----------------------------
def generate_valid_fp16(abs_limit):
    """
    Generates a number uniformly between -abs_limit and abs_limit as a float64,
    converts it to float16 using SoftFloat, and rejects values with abs < 0.01.
    
    Parameters:
        abs_limit (float): Maximum absolute value for the random number.
    """
    while True:
        candidate = np.random.uniform(-abs_limit, abs_limit)
        candidate_f16 = float16_bits_to_float(float_to_f16_bits(candidate))
        # if -0.01 < candidate_f16 < 0.01:
        #     continue
        return candidate_f16

def generate_fp16_mul_test(N, outfile):
    data = bytearray()
    for i in range(N):
        # Step 1: Generate op1 within MAX_OP range
        op1 = generate_valid_fp16(MAX_OP)

        # Step 2: Calculate safe op2 range to avoid overflow
        if abs(op1) > 0:
            max_abs_op2 = min(65504 / abs(op1), MAX_OP)
        else:
            max_abs_op2 = MAX_OP  # Avoid division by zero

        # Step 3: Find valid op2 within this range
        while True:
            op2 = generate_valid_fp16(max_abs_op2)
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
    MAX_OP = 1.0
    NUM_TESTS = 1000000
    GENERATE_OUTFILE = 'examples/matrix/tgt/fp16_mul_test.bin'
    generate_fp16_mul_test(NUM_TESTS, GENERATE_OUTFILE)
