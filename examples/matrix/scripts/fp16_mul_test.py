import struct
import os
import numpy as np
import csv

def generate_valid_fp16():
    """
    Generates a number uniformly between -65504 and 65504 as a float64,
    then converts it to np.float16.
    Rejects any candidate whose absolute value is strictly less than 0.01.
    """
    while True:
        candidate = np.random.uniform(-65504, 65504)
        candidate_f16 = np.float16(candidate)
        if -0.01 < candidate_f16 < 0.01:
            continue
        return candidate_f16

def half_mul(a, b):
    """
    Performs multiplication of two IEEE 754 half-precision numbers (normalized only)
    given as 16-bit unsigned integers (their bit patterns). This routine extracts
    the sign, exponent, and fraction; multiplies the significands (with an implicit
    1 bit); and then normalizes/rounds the result.
    
    This version converts the intermediate values to Python ints to avoid overflow.
    
    Note: This routine assumes both operands are normalized (exponent ≠ 0).
    """
    # Ensure we are working with Python ints.
    a = int(a)
    b = int(b)
    
    # Extract fields for operand a.
    sign_a = a >> 15
    exp_a = (a >> 10) & 0x1F
    frac_a = a & 0x3FF

    # Extract fields for operand b.
    sign_b = b >> 15
    exp_b = (b >> 10) & 0x1F
    frac_b = b & 0x3FF

    # For normalized numbers, the significand includes an implicit 1.
    m_a = (1 << 10) | frac_a  # 11-bit significand
    m_b = (1 << 10) | frac_b  # 11-bit significand

    # Multiply the significands in full precision.
    product = m_a * m_b  # This product can be up to 22 bits wide.

    # Calculate tentative exponent. Bias for fp16 is 15.
    exp = exp_a + exp_b - 15

    # Determine normalization: if the product's bit 21 is set, we need to shift by 11 bits.
    if product & (1 << 21):
        shift = 11
        exp += 1  # Extra shift bumps up the exponent.
    else:
        shift = 10

    # Extract remainder for rounding.
    remainder = product & ((1 << shift) - 1)
    halfway = 1 << (shift - 1)
    quotient = product >> shift

    # Round to nearest even.
    if remainder > halfway or (remainder == halfway and (quotient & 1)):
        quotient += 1
        # Handle rounding overflow.
        if quotient == (1 << 11):
            quotient = (1 << 10)
            exp += 1

    # Handle exponent overflow: return infinity.
    if exp >= 31:
        return ((sign_a ^ sign_b) << 15) | (0x1F << 10)
    # Handle underflow: for simplicity, return zero (no subnormal handling).
    if exp <= 0:
        return (sign_a ^ sign_b) << 15

    # Remove the implicit 1 (only keep the lower 10 bits).
    frac = quotient & 0x3FF
    result = ((sign_a ^ sign_b) << 15) | (exp << 10) | frac
    return result

def half_precision_mul(a_f16, b_f16):
    """
    Multiplies two np.float16 numbers using our custom half-precision multiplication.
    Returns the result as an np.float16.
    """
    a_bits = a_f16.view(np.uint16)
    b_bits = b_f16.view(np.uint16)
    res_bits = half_mul(a_bits, b_bits)
    result = np.array([res_bits], dtype=np.uint16).view(np.float16)[0]
    return result

def generate_fp16_mul_test(N, outfile):
    """
    Generates test cases for fp16 multiplication using our custom multiplication.
    Each test case consists of three fields (each stored as 3 bytes):
      - operand1: 2-byte little-endian fp16 value plus 1 pad byte (0)
      - operand2: 2-byte little-endian fp16 value plus 1 pad byte (0)
      - result:   2-byte little-endian fp16 value plus 1 pad byte (0)
    
    Candidate operands are generated with generate_valid_fp16(). The pair is rejected
    if the computed product (using half_precision_mul) results in infinity or NaN.
    """
    data = bytearray()
    for _ in range(N):
        while True:
            op1 = generate_valid_fp16()
            op2 = generate_valid_fp16()
            result = half_precision_mul(op1, op2)
            if np.isinf(result) or np.isnan(result):
                continue
            break

        op1_rep = op1.view(np.uint16)
        op2_rep = op2.view(np.uint16)
        res_rep = result.view(np.uint16)
        
        # Pack each value into 3 bytes (2-byte little-endian + 1 pad byte).
        data += struct.pack('<HB', int(op1_rep), 0)
        data += struct.pack('<HB', int(op2_rep), 0)
        data += struct.pack('<HB', int(res_rep), 0)
    
    os.makedirs(os.path.dirname(outfile), exist_ok=True)
    with open(outfile, 'wb') as f:
        f.write(data)
    print(f"Wrote {N} test cases ({len(data)} bytes) to {outfile}")


def convert_fp16_test_out_to_csv(infile,outfile):
    """
    Reads a binary file containing FP16 multiplication test output and converts it to CSV.
    Each record is 12 bytes (4 fields of 3 bytes each) with fields: op1, op2, python, asm.
    The CSV will contain both the float values and the corresponding hex representations.
    """
    with open(infile, 'rb') as f:
        data = f.read()
    
    record_size = 4 * 3  # 12 bytes per record
    num_records = len(data) // record_size
    rows = []
    
    for i in range(num_records):
        rec = data[i * record_size: (i + 1) * record_size]
        rec_values = []
        rec_hex = []
        
        for j in range(4):
            field_bytes = rec[j * 3: j * 3 + 3]
            (val_uint16,) = struct.unpack('<H', field_bytes[:2])
            f16 = np.array([val_uint16], dtype=np.uint16).view(np.float16)[0]
            rec_values.append(float(f16))
            
            # Convert all 3 bytes to a 24-bit little-endian hex value.
            val_uint24 = int.from_bytes(field_bytes, 'little')
            rec_hex.append(f"0x{val_uint24:06X}")
        
        # CSV columns: op1, op2, python, asm, 0xop1, 0xop2, 0xpython, 0xasm
        rows.append(rec_values + rec_hex)
    
    header = ['op1', 'op2', 'python', 'asm', '0xop1', '0xop2', '0xpython', '0xasm']
    os.makedirs(os.path.dirname(outfile), exist_ok=True)
    with open(outfile, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)
        writer.writerows(rows)
    
    print(f"Wrote {num_records} records to {os.path.abspath(outfile)}")

def decode_fp16(hex_str):
    """
    Decodes a hex string representing a 16-bit IEEE-754 binary16 value.
    Returns a tuple: (sign, exponent, mantissa)
    For normal numbers (exponent ≠ 00000) the mantissa is prefixed with '1',
    and for subnormals with '0'. If a 24-bit hex string is given (6 hex digits),
    only the lower 16 bits (last 4 hex digits) are used.
    """
    hex_str = hex_str.strip()
    if hex_str.lower().startswith("0x"):
        hex_str = hex_str[2:]
    if len(hex_str) > 4:
        hex_str = hex_str[-4:]
    val = int(hex_str, 16)
    bin_str = format(val, '016b')
    sign = bin_str[0]
    exponent = bin_str[1:6]
    fraction = bin_str[6:]
    assumed = "1" if exponent != "00000" else "0"
    mantissa = assumed + fraction
    return sign, exponent, mantissa

def run_decode_fp16(hex_input):
    """
    Splits a whitespace-separated hex string (each token 24-bit) and decodes each token.
    Prints raw binary (split into three 8-bit segments) and decoded FP16 fields.
    """
    tokens = hex_input.split()
    for token in tokens:
        token_stripped = token.strip()
        if token_stripped.lower().startswith("0x"):
            token_stripped = token_stripped[2:]
        token_stripped = token_stripped.zfill(6)
        val = int(token_stripped, 16)
        bin24 = format(val, '024b')
        byte1 = bin24[:8]
        byte2 = bin24[8:16]
        byte3 = bin24[16:]
        raw_str = f"Raw: {byte1} {byte2} {byte3}"
        
        s, exp, mantissa = decode_fp16(token)
        print(f"{token}\t{raw_str}\tSign: {s}\tExponent: {exp}\tMantissa: {mantissa}")

# =======================
# Configuration
# =======================
# For generate:
NUM_TESTS = 1000
GENERATE_OUTFILE = 'examples/matrix/tgt/fp16_mul_test.bin'

# For convert:
CONVERT_INFILE = 'examples/matrix/tgt/fp16_mul_test_out.bin'
CONVERT_OUTFILE = 'examples/matrix/tgt/fp16_mul_test_out.csv'

# For decode:
DECODE_HEX_STRING = "0x002A9F 0x005552 0x004467 0x000033"

if __name__ == "__main__":
    # generate_fp16_mul_test(N=NUM_TESTS, outfile=GENERATE_OUTFILE)
    convert_fp16_test_out_to_csv(infile=CONVERT_INFILE, outfile=CONVERT_OUTFILE)

    # run_decode_fp16(DECODE_HEX_STRING)
