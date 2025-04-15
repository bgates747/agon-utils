import random
import struct
import os

def generate_test_cases(output_file, num_cases, de_min, de_max, bc_min, bc_max):
    """Generate test cases and write them to the output file."""
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'wb') as f:
        for _ in range(num_cases):
            hl = random.randint(de_min, de_max)
            de = random.randint(bc_min, bc_max)

            quotient = hl // de
            remainder = hl % de

            # Fixed-point fractional part: (remainder << 16) // de
            fractional = (remainder << 16) // de

            # Clamp fractional to 16 bits in case of cosmic ray strike
            fractional &= 0xFFFF

            # Write hl, de, quotient, fractional, and 4 zero bytes (reserved result)
            f.write(struct.pack('<HHHHI', hl, de, quotient, fractional, 0))
            
    print(f"Generated {num_cases} test cases and wrote them to {output_file}")
    print(f"File size: {os.path.getsize(output_file)} bytes")

if __name__ == "__main__":
    output_file = '/home/smith/Agon/mystuff/agon-utils/examples/matrix/tgt/div_16_32_test.bin'
    num_cases = 10000
    
    de_min = 0
    de_max = 65535
    
    bc_min = 1  # Avoid zero to prevent division by zero
    bc_max = 65535
    
    generate_test_cases(output_file, num_cases, de_min, de_max, bc_min, bc_max)