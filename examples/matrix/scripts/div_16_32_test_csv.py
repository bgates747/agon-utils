#!/usr/bin/env python3
"""
Convert binary test results from EZ80 division test to CSV format.

Each 12-byte record contains:
- dividend (2 bytes)
- divisor (2 bytes)
- reference quotient_h (2 bytes)
- reference quotient_l (2 bytes)
- asm_result: quotient_h (2 bytes), quotient_l (2 bytes)

Outputs a CSV with:
dividend, divisor, quotient_h, quotient_l, asm_quotient_h, asm_quotient_l
All formatted as hex with 0x prefix.
"""

import struct
import csv

def bin_to_csv(infile, outfile):
    """Convert division test binary to CSV with hex representation."""
    records = []
    
    with open(infile, 'rb') as f:
        while True:
            record_data = f.read(12)
            if not record_data or len(record_data) < 12:
                break
            
            # Unpack: dividend, divisor, quotient_h, quotient_l, asm_quotient_h, asm_quotient_l
            dividend, divisor, quotient_h, quotient_l, asm_quotient_h, asm_quotient_l = struct.unpack('<HHHHHH', record_data)
            
            records.append({
                'dividend': f'0x{dividend:04x}',
                'divisor': f'0x{divisor:04x}',
                'quotient_h': f'0x{quotient_h:04x}',
                'quotient_l': f'0x{quotient_l:04x}',
                'asm_quotient_h': f'0x{asm_quotient_h:04x}',
                'asm_quotient_l': f'0x{asm_quotient_l:04x}'
            })
    
    # Write CSV
    with open(outfile, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'dividend', 'divisor',
            'quotient_h', 'quotient_l',
            'asm_quotient_h', 'asm_quotient_l'
        ])
        writer.writeheader()
        writer.writerows(records)
    
    print(f"Converted {len(records)} records from {infile} to {outfile}")
    print(f"All values formatted in hexadecimal with 0x prefix")

if __name__ == "__main__":
    CONVERT_INFILE = '/home/smith/Agon/mystuff/agon-utils/examples/matrix/tgt/div_16_32_test.bin'
    CONVERT_OUTFILE = '/home/smith/Agon/mystuff/agon-utils/examples/matrix/tgt/div_16_32_test.csv'
    
    bin_to_csv(CONVERT_INFILE, CONVERT_OUTFILE)
