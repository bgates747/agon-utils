#!/usr/bin/env python3
import struct
import os
import numpy as np
import csv
from SoftFloat import f16_to_f32_softfloat

def convert_fp16_test_out_to_csv(infile, outfile):
    """
    Reads a binary file containing FP16 multiplication test output and converts it to CSV.
    Each record is 8 bytes:
      - 4 fields of 2 bytes each: op1, op2, python result, asm result
    The CSV will contain both float32 values and 16-bit hex representations.
    """
    with open(infile, 'rb') as f:
        data = f.read()
    
    record_size = 8  # 4 fields * 2 bytes
    num_records = len(data) // record_size
    rows = []
    
    for i in range(num_records):
        rec = data[i * record_size: (i + 1) * record_size]
        rec_values = []
        rec_hex = []
        for j in range(4):
            field_bytes = rec[j * 2: j * 2 + 2]
            (val_uint16,) = struct.unpack('<H', field_bytes)
            rec_hex.append(f"0x{val_uint16:04X}")
            
            # For op1, op2, python result: use numpy
            if j != 3:
                f16_val = np.array([val_uint16], dtype=np.uint16).view(np.float16)[0]
                rec_values.append(float(f16_val))
            else:
                # For asm result: use SoftFloat
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
    CONVERT_INFILE = '/home/smith/Agon/mystuff/agon-utils/examples/matrix/tgt/fp16_mul_test.bin'
    CONVERT_OUTFILE = '/home/smith/Agon/mystuff/agon-utils/examples/matrix/tgt/fp16_mul_test.csv'
    
    convert_fp16_test_out_to_csv(CONVERT_INFILE, CONVERT_OUTFILE)
