import random
import struct
import os

def generate_test_cases(output_file, num_cases, hl_min, hl_max, de_min, de_max):
    """Generate test cases and write them to the output file."""
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'wb') as f:
        for _ in range(num_cases):
            hl = random.randint(hl_min, hl_max)
            de = random.randint(de_min, de_max)
            product = hl * de
            
            # Write operands, expected product, and reserve space (4 zero-bytes)
            f.write(struct.pack('<HHI4x', hl, de, product))
            
    print(f"Generated {num_cases} test cases and wrote them to {output_file}")
    print(f"File size: {os.path.getsize(output_file)} bytes")

if __name__ == "__main__":
    output_file = '/home/smith/Agon/mystuff/agon-utils/examples/matrix/tgt/mul_16_32_test.bin'
    num_cases = 1000000
    
    hl_min = 0
    hl_max = 65535
    
    de_min = 0
    de_max = 65535
    
    generate_test_cases(output_file, num_cases, hl_min, hl_max, de_min, de_max)
