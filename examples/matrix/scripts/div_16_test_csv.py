#!/usr/bin/env python3
"""
Convert binary test results from EZ80 division test to CSV format.

Each 12-byte record contains:
- dividend (2 bytes)
- divisor (2 bytes)
- reference quotient (2 bytes)
- reference remainder (2 bytes)
- asm_result: quotient (2 bytes), remainder (2 bytes)

Outputs a CSV with:
dividend, divisor, quotient, remainder, asm_quotient, asm_remainder
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
            
            # Unpack: dividend, divisor, quotient, remainder, asm_quotient, asm_remainder
            dividend, divisor, quotient, remainder, asm_quotient, asm_remainder = struct.unpack('<HHHHHH', record_data)
            
            records.append({
                'dividend': f'0x{dividend:04x}',
                'divisor': f'0x{divisor:04x}',
                'quotient': f'0x{quotient:04x}',
                'remainder': f'0x{remainder:04x}',
                'asm_quotient': f'0x{asm_quotient:04x}',
                'asm_remainder': f'0x{asm_remainder:04x}'
            })
    
    # Write CSV
    with open(outfile, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'dividend', 'divisor',
            'quotient', 'remainder',
            'asm_quotient', 'asm_remainder'
        ])
        writer.writeheader()
        writer.writerows(records)
    
    print(f"Converted {len(records)} records from {infile} to {outfile}")
    print(f"All values formatted in hexadecimal with 0x prefix")

if __name__ == "__main__":
    CONVERT_INFILE = '/home/smith/Agon/mystuff/agon-utils/examples/matrix/tgt/div_16_test.bin'
    CONVERT_OUTFILE = '/home/smith/Agon/mystuff/agon-utils/examples/matrix/tgt/div_16_test.csv'
    
    bin_to_csv(CONVERT_INFILE, CONVERT_OUTFILE)
