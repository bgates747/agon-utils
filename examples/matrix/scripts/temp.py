#!/usr/bin/env python3
import sys
import subprocess
from cffi import FFI

def hex_to_signed_8(value):
    val = int(value, 16)
    return val if val < 0x80 else val - 0x100

def run_cli(sign_hex, exp_hex, sig_hex):
    executable = "/home/smith/Agon/mystuff/agon-utils/utils/SoftFloat-3e/build/Linux-x86_64-GCC/cli_softfloat_roundPackToF16"
    cmd = [executable, sign_hex, exp_hex, sig_hex]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error executing CLI tool: {e}"

def run_cffi(sign_hex, exp_hex, sig_hex):
    ffi = FFI()
    ffi.cdef("""
        typedef uint16_t float16_t;
        extern int softfloat_roundingMode;
        float16_t softfloat_roundPackToF16(_Bool sign, int exp, unsigned int sig);
    """)
    lib = ffi.dlopen("/home/smith/Agon/mystuff/agon-utils/utils/SoftFloat-3e/build/Linux-x86_64-GCC/softfloat.so")

    # Convert inputs
    sign_val = int(sign_hex, 16)
    exp_val = int(exp_hex, 16)
    sig_val = int(sig_hex, 16)

    sign_byte = sign_val if sign_val < 0x80 else sign_val - 0x100
    exp_byte  = exp_val if exp_val < 0x80 else exp_val - 0x100
    sign = (sign_byte < 0)
    exp  = int(exp_byte)
    sig  = sig_val

    # Set rounding mode to nearest even (0)
    lib.softfloat_roundingMode = 0

    result = lib.softfloat_roundPackToF16(bool(sign), exp, sig)
    result = int(result)  # Ensure result is a native Python int

    return f"""Input: sign=0x{sign_val:02x}, exp=0x{exp_val:02x}, sig=0x{sig_val:04x}
Interpreted: sign={int(sign)}, exp={exp} (0x{exp & 0xFFFF:04x}), sig=0x{sig:04x}
Output: 0x{result:04x}
"""

def main(input_str):
    input_str = input_str.strip()
    parts = input_str.split()
    if len(parts) != 3:
        print("Error: Expected three hex values.")
        return

    print("=== CLI tool output ===")
    print(run_cli(parts[0], parts[1], parts[2]))

    print("=== CFFI output ===")
    print(run_cffi(parts[0], parts[1], parts[2]))

if __name__ == "__main__":
    main("0x80	0x1a	0x66fa")
