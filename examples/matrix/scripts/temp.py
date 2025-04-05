#!/usr/bin/env python3
import sys
from cffi import FFI

ffi = FFI()
ffi.cdef("""
    typedef uint16_t float16_t;
    typedef uint32_t float32_t;
    float16_t softfloat_roundPackToF16(bool sign, int_fast16_t exp, uint_fast16_t sig);
""")

# Update this path to wherever your shared library is located:
lib = ffi.dlopen("/home/smith/Agon/mystuff/agon-utils/utils/SoftFloat-3e/build/Linux-x86_64-GCC/softfloat.so")

def main():
    # Our test case from the table:
    # sign=0x80 => "true" for negative
    sign_bool = True
    exp       = 0xF5  # 245 in decimal
    sig       = 0x4213
    
    # Call the SoftFloat function
    result = lib.softfloat_roundPackToF16(sign_bool, exp, sig)

    # Extract raw sign, exponent, and mantissa from the 16-bit result
    sign_out = (result >> 15) & 0x1
    exp_out = (result >> 10) & 0x1F
    mant_out = result & 0x3FF

    # Print everything in hex with leading zeros
    print(f"Input:")
    print(f"  sign=0x80 (bool={sign_bool}), exp=0x{exp:04x}, sig=0x{sig:04x}\n")
    print(f"Output raw float16 = 0x{result:04x}")
    print(f"  sign={sign_out}, exponent=0x{exp_out:02x}, mantissa=0x{mant_out:03x}")

if __name__ == "__main__":
    main()
