import numpy as np
import struct
import warnings

# Optionally suppress runtime warnings from operations in half precision.
warnings.filterwarnings("ignore", category=RuntimeWarning)

# Number of test cases
N = 65536

# We'll build a bytearray to hold the binary data.
# Each test case: operand1 (3 bytes) + operand2 (3 bytes) + result (3 bytes)
data = bytearray()

for _ in range(N):
    # Generate random 16-bit bit patterns (0..65535) for the operands.
    op1_bits = np.random.randint(0, 65536, dtype=np.uint16)
    op2_bits = np.random.randint(0, 65536, dtype=np.uint16)
    
    # Reinterpret the bit patterns as IEEE-754 binary16 (half precision).
    # Note: This may generate infinities or NaNs, which is fine for testing.
    op1 = np.array([op1_bits], dtype=np.uint16).view(np.float16)[0]
    op2 = np.array([op2_bits], dtype=np.uint16).view(np.float16)[0]
    
    # Multiply the two half-precision values.
    result = np.float16(op1 * op2)
    
    # Get the 16-bit binary representations of each value.
    op1_rep = np.float16(op1).view(np.uint16)
    op2_rep = np.float16(op2).view(np.uint16)
    res_rep = np.float16(result).view(np.uint16)
    
    # Pack each 16-bit value into 3 bytes (2 bytes little-endian + 1 pad byte of 0)
    data += struct.pack('<HB', int(op1_rep), 0)
    data += struct.pack('<HB', int(op2_rep), 0)
    data += struct.pack('<HB', int(res_rep), 0)

# Write the data to the specified file.
with open('examples/matrix/scripts/fp16_mul_test.bin', 'wb') as f:
    f.write(data)

print(f"Wrote {N} test cases ({len(data)} bytes) to examples/matrix/scripts/fp16_mul_test.bin")
