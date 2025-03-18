#!/usr/bin/env python3
import struct
import os
import numpy as np
import csv
from SoftFloat import f16_to_f32_softfloat

def format_fp16_output(val):
    """
    Given a 16-bit integer representing a float16 value, pack it into 3 bytes
    (2 bytes for the value and a pad byte 0) to form a 24-bit little-endian number.
    Then, format and return a string with:
      - the hex representation,
      - the raw binary (split into three 8-bit segments),
      - the decoded sign, exponent, and mantissa,
      - and the decimal value (obtained via SoftFloat's f16_to_f32_softfloat).
    """
    # Pack into 3 bytes: two bytes for the 16-bit value and one pad byte (0)
    packed = struct.pack('<HB', val, 0)
    val_uint24 = int.from_bytes(packed, 'little')
    hex_field = f"0x{val_uint24:06X}"
    raw_bin = format(val_uint24, '024b')
    byte1 = raw_bin[:8]
    byte2 = raw_bin[8:16]
    byte3 = raw_bin[16:]
    s, exp, mantissa = decode_fp16(hex_field)
    # Use SoftFloat to get the decimal value:
    dec = f16_to_f32_softfloat(val)
    return f"{hex_field}\tRaw: {byte1} {byte2} {byte3}\tSign: {s}\tExponent: {exp}\tMantissa: {mantissa}\tDecimal: {dec}"

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

def convert_fp16_test_out_to_csv(infile, outfile):
    """
    Reads a binary file containing FP16 multiplication test output and converts it to CSV.
    Each record is 12 bytes (4 fields of 3 bytes each) with fields: op1, op2, python, asm.
    The CSV will contain both the numeric values and the corresponding hex representations.
    For the 'asm' field, the decimal value is obtained using SoftFloat's f16_to_f32_softfloat.
    """
    with open(infile, 'rb') as f:
        data = f.read()
    
    record_size = 4 * 3  # 12 bytes per record
    num_records = len(data) // record_size
    rows = []
    
    # For each record, process each of the 4 fields:
    for i in range(num_records):
        rec = data[i * record_size: (i + 1) * record_size]
        # We'll accumulate numeric values and hex strings separately.
        rec_values = []
        rec_hex = []
        for j in range(4):
            field_bytes = rec[j * 3: j * 3 + 3]
            # The first 2 bytes are the 16-bit value.
            (val_uint16,) = struct.unpack('<H', field_bytes[:2])
            # Convert the full 3 bytes into a 24-bit little-endian hex string.
            val_uint24 = int.from_bytes(field_bytes, 'little')
            rec_hex.append(f"0x{val_uint24:06X}")
            
            # For op1, op2, and the 'python' field, use numpy conversion:
            if j != 3:
                f16_val = np.array([val_uint16], dtype=np.uint16).view(np.float16)[0]
                rec_values.append(float(f16_val))
            else:
                # For the asm field, use SoftFloat conversion.
                rec_values.append(f16_to_f32_softfloat(val_uint16))
        
        rows.append(rec_values + rec_hex)
    
    header = ['op1', 'op2', 'python', 'asm', '0xop1', '0xop2', '0xpython', '0xasm']
    os.makedirs(os.path.dirname(outfile), exist_ok=True)
    with open(outfile, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)
        writer.writerows(rows)
    
    print(f"Wrote {num_records} records to {os.path.abspath(outfile)}")

if __name__ == "__main__":
    # Hard-coded file paths
    CONVERT_INFILE = 'examples/matrix/tgt/fp16_mul_test_out.bin'
    CONVERT_OUTFILE = 'examples/matrix/tgt/fp16_mul_test_out.csv'
    
    convert_fp16_test_out_to_csv(CONVERT_INFILE, CONVERT_OUTFILE)


