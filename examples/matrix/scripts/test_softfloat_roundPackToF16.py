#!/usr/bin/env python3
import os
import struct
import random
from cffi import FFI
import numpy as np

# ----------------------------
# SoftFloat CFFI Setup
# ----------------------------
ffi = FFI()
ffi.cdef("""
    typedef uint16_t float16_t;
    typedef uint32_t float32_t;
    float16_t softfloat_roundPackToF16(bool sign, int_fast16_t exp, uint_fast16_t sig);
""")
lib = ffi.dlopen("/home/smith/Agon/mystuff/agon-utils/utils/SoftFloat-3e/build/Linux-x86_64-GCC/softfloat.so")

# ----------------------------
# Helper Functions
# ----------------------------
def extract_f16_components(f16_value):
    """Extract sign, exponent, and mantissa from a float16 value."""
    sign = 0x80 if (f16_value >> 15) & 0x1 else 0x00
    exp = (f16_value >> 10) & 0x1F
    mantissa = f16_value & 0x3FF
    
    # Add implied 1 bit for normal numbers (exp != 0)
    if exp != 0:
        mantissa |= 0x400  # Set the implied 1 bit (bit 10)
    
    return sign, exp, mantissa

def generate_test_case(min_exp, max_exp, min_sig, max_sig):
    """Generate a random test case within the specified ranges."""
    # Generate random sign (0 or 0x80)
    sign_bool = random.choice([False, True])
    sign_byte = 0x80 if sign_bool else 0
    
    # Generate random biased exponent (1 to 0x1D)
    exp = random.randint(min_exp, max_exp)
    
    # Generate random significand with implied 1 at bit 14 and rounding bits at 0-3
    sig_base = 0x4000  # Bit 14 set (implied 1)
    
    # Generate random bits for the rest of the significand
    sig_random = random.randint(0, 0x3FFF)  # All other bits random
    sig = sig_base | sig_random
    
    # Ensure significand is within specified range
    sig = max(min_sig, min(max_sig, sig)) 

    # Call SoftFloat to get the expected result
    packed_p = lib.softfloat_roundPackToF16(sign_bool, exp, sig)
    
    # Extract components from the packed result
    sign_p, exp_p, mantissa_p = extract_f16_components(packed_p)
    
    # Default assembly results (zeros)
    packed_a = 0
    sign_a = 0
    exp_a = 0
    mantissa_a = 0
    
    # Return the adjusted exponent, not the original
    return sign_byte, exp, sig, packed_p, sign_p, exp_p, mantissa_p, packed_a, sign_a, exp_a, mantissa_a

def create_test_data_file(filename, num_trials, min_exp, max_exp, min_sig, max_sig):
    """Create a binary file with random test data."""
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    with open(filename, 'wb') as f:
        for _ in range(num_trials):
            sign, exp, sig, packed_p, sign_p, exp_p, mantissa_p, packed_a, sign_a, exp_a, mantissa_a = generate_test_case(min_exp, max_exp, min_sig, max_sig)
            
            # Pack all data into binary format - 11 fields total
            # Format: <BBHHBBHHBBH for sign,exp,sig,packed_p,sign_p,exp_p,mantissa_p,packed_a,sign_a,exp_a,mantissa_a
            record = struct.pack('<BBHHBBHHBBH', sign, exp, sig, packed_p, sign_p, exp_p, mantissa_p, packed_a, sign_a, exp_a, mantissa_a)
            f.write(record)
    
    print(f"Generated {num_trials} test cases in {filename}")

# ----------------------------
# Main Function
# ----------------------------
if __name__ == "__main__":
    # Set parameters directly
    output_file = 'tgt/softfloat_roundPackToF16.bin'
    num_trials = 100000
    min_exp = 1
    max_exp = 0x1D
    min_sig = 0x4000  # Ensure bit 14 is set
    max_sig = 0x7FFF
    
    create_test_data_file(
        output_file, 
        num_trials, 
        min_exp, 
        max_exp, 
        min_sig, 
        max_sig
    )