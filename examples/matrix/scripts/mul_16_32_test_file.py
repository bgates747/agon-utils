#!/usr/bin/env python3
"""
Generate test cases for EZ80 16x16=32 bit multiplication.

This script generates random pairs of 16-bit integers within specified ranges,
multiplies them, and writes the operands and results to a binary file.
Each record is 8 bytes: 2 bytes for each operand and 4 bytes for the product.
"""

import random
import struct
import os

def generate_test_cases(output_file, num_cases, hl_min, hl_max, de_min, de_max):
    """Generate test cases and write them to the output file."""
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'wb') as f:
        for _ in range(num_cases):
            # Generate random operands within specified ranges
            hl = random.randint(hl_min, hl_max)
            de = random.randint(de_min, de_max)
            
            # Calculate the product
            product = hl * de
            
            # Write the operands and product to the file
            # Format: hl (2 bytes), de (2 bytes), product (4 bytes)
            f.write(struct.pack('<HHI', hl, de, product))
            
    print(f"Generated {num_cases} test cases and wrote them to {output_file}")
    print(f"File size: {os.path.getsize(output_file)} bytes")

if __name__ == "__main__":
    # Configuration parameters - modify these values as needed
    output_file = '/home/smith/Agon/mystuff/agon-utils/examples/matrix/tgt/mul_16_32_test.bin'
    num_cases = 10000
    
    # Range for the first operand (HL)
    hl_min = 0
    hl_max = 65535
    
    # Range for the second operand (DE)
    de_min = 0
    de_max = 65535
    
    # Generate the test cases
    generate_test_cases(output_file, num_cases, hl_min, hl_max, de_min, de_max)