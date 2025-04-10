#!/usr/bin/env python3
import struct
import numpy as np
from SoftFloat import f16_mul_softfloat, f16_to_f32_softfloat

# ----------------------------
# Decoding and Formatting Functions
# ----------------------------
def decode_fp16(val):
    """
    Decodes a 16-bit integer (representing an IEEE 754 binary16 value)
    into its sign, exponent, and fraction fields.
    For normalized numbers, the implied leading bit is '1'; for subnormals it is '0'.
    Returns a tuple: (sign, exponent, mantissa)
    where 'mantissa' is a string consisting of the implied bit concatenated with the 10-bit fraction.
    """
    bin_str = format(val, '016b')
    sign = bin_str[0]
    exponent = bin_str[1:6]
    fraction = bin_str[6:]
    # If normalized, the implied bit is 1; if subnormal, it is 0.
    assumed = "1" if exponent != "00000" else "0"
    mantissa = assumed + fraction
    return sign, exponent, mantissa

def format_fp16_output(val, description=""):
    """
    Format a 16-bit float16 integer representation into:
    val (4-digit hex) val (binary, 2-byte split) sign (2-digit hex) exponent (2-digit hex)
    mantissa (4-digit hex) mantissa (binary, 2-byte split) decimal
    """
    val_hex = f"{val:04x}"

    bin_str = f"{val:016b}"
    byte1 = bin_str[:8]
    byte2 = bin_str[8:]

    sign_bit = (val >> 15) & 0x1
    sign_hex = "80" if sign_bit else "00"

    exp_bits = (val >> 10) & 0x1F
    exp_hex = f"{exp_bits:02x}"

    frac_bits = val & 0x03FF
    if exp_bits != 0:
        mantissa_val = 0x0400 | frac_bits  # implied 1
    else:
        mantissa_val = frac_bits  # subnormal

    mantissa_hex = f"{mantissa_val:04x}"
    mantissa_bin = f"{mantissa_val:011b}".zfill(11)
    mantissa_byte1 = mantissa_bin[:3]  # implied + next 2
    mantissa_byte2 = mantissa_bin[3:]  # lower 8 bits

    dec_val = f16_to_f32_softfloat(val)

    return f"; {val_hex} {byte1} {byte2} {sign_hex} {exp_hex} {mantissa_hex} {mantissa_byte1} {mantissa_byte2} {dec_val} {description}"


# ----------------------------
# Intermediate Mantissa Multiplication Functions
# ----------------------------
def get_mantissa_and_exp(fp16):
    """
    Extracts the normalized mantissa and adjusted exponent from a float16 bit pattern.
    For normalized numbers: returns (mantissa, exponent)
    For subnormals: shifts left until bit 10 is set, adjusts exponent accordingly.
    The returned exponent is unbiased.
    """
    fraction = fp16 & 0x03FF
    exponent = (fp16 >> 10) & 0x1F

    if exponent != 0:
        mantissa = (1 << 10) | fraction
        return mantissa, exponent - 15
    else:
        if fraction == 0:
            return 0, -14  # zero has exponent -14 by convention
        # normalize subnormal
        shift = 0
        while (fraction & 0x0400) == 0:
            fraction <<= 1
            shift += 1
        mantissa = fraction & 0x07FF
        exponent = -14 - shift + 1  # subnormal exponent logic
        return mantissa, exponent


def hex_bin_format(val, width=16):
    """
    Return formatted hex and byte-split binary for a given value.
    Width can be 16 or 32 (bits).
    """
    if width == 16:
        hexstr = f"{val:04x}"
        binstr = f"{val:016b}"
        return hexstr, f"{binstr[:8]} {binstr[8:]}"
    elif width == 32:
        hexstr = f"{val:08x}"
        binstr = f"{val:032b}"
        return hexstr, f"{binstr[:8]} {binstr[8:16]} {binstr[16:24]} {binstr[24:]}"
    else:
        raise ValueError("Unsupported width")

def print_intermediate_result(a_fp16, b_fp16):
    """
    Formats intermediate multiplication results using normalized mantissas
    and adjusted exponents from float16 values.
    """
    m1, e1 = get_mantissa_and_exp(a_fp16)
    m2, e2 = get_mantissa_and_exp(b_fp16)

    sigA = m1 << 4
    sigB = m2 << 5
    sig32Z = sigA * sigB

    hi16 = (sig32Z >> 16) & 0xFFFF
    lo16 = sig32Z & 0xFFFF

    hexA, binA = hex_bin_format(sigA, 16)
    hexB, binB = hex_bin_format(sigB, 16)
    hexHi, binHi = hex_bin_format(hi16, 16)
    hexLo, binLo = hex_bin_format(lo16, 16)

    return [
        f"; {hexA} {binA}  sigA (<<4, normalized)",
        f"; {hexB} {binB}  sigB (<<5, normalized)",
        f"; {hexHi} {binHi}  sig32Z >> 16 (upper 16 bits of 32-bit product)",
        f"; {hexLo} {binLo}  sig32Z & 0xFFFF (lower 16 bits of 32-bit product)",
        f"; expA = {e1}, expB = {e2}, expA + expB = {e1 + e2}"
    ]


def main(input_string):

    # Split the input string by whitespace.
    parts = input_string.split()
    if len(parts) < 4:
        print("Error: expected 4 hex numbers separated by whitespace.")
        exit(1)

    # Parse the hex numbers.
    a_hex, b_hex, expected_hex, output_hex = parts[:4]
    a_f16 = int(a_hex, 16)
    b_f16 = int(b_hex, 16)
    # Expected result is ignored (since we compute it via SoftFloat).
    assembly_output = int(output_hex, 16)

    # Compute SoftFloat multiplication result.
    result_f16 = f16_mul_softfloat(a_f16, b_f16)
    intermediate_results = print_intermediate_result(a_f16, b_f16)

    # Print the SoftFloat outputs.
    print("; --- Inputs / Outputs ---")
    print(format_fp16_output(a_f16, "sigA"))
    print(format_fp16_output(b_f16, "sigB"))
    print(format_fp16_output(result_f16,"Expected Result"))
    print(format_fp16_output(assembly_output,"Assembly Result"))

    print("\n; --- Intermediate Results ---")
    for line in intermediate_results:
        print(line)

    
    # Get float (decimal) values for the operands and product.
    a_float = f16_to_f32_softfloat(a_f16)
    b_float = f16_to_f32_softfloat(b_f16)
    
    # Format the float values in a human-readable (or scientific) form.
    # Adjust precision as desired.
    a_float_str = f"{a_float:.16e}"
    b_float_str = f"{b_float:.16e}"
    
    # For the product, generate the 24-bit representation.
    packed = struct.pack('<HB', result_f16, 0)
    val_uint24 = int.from_bytes(packed, 'little')
    # Format the 24-bit hex without the "0x" prefix.
    result_hex_str = f"{val_uint24:06X}"
    # Get the raw 24-bit binary split into three groups.
    raw_bin = format(val_uint24, '024b')
    raw_parts = f"{raw_bin[:8]} {raw_bin[8:16]} {raw_bin[16:]}"
    
    # Now, generate the assembly test code.
    asm_lines = [
        f"    ld hl,{a_hex}",
        f"    ld de,{b_hex}",
        f"    ld bc,{expected_hex}"
    ]

    print("\n; --- Generated Assembly Test Code ---")
    for line in asm_lines:
        print(line)

# ----------------------------
# Main Execution
# ----------------------------
if __name__ == "__main__":
    input_string = "0x8000	0xEF25	0x0000	0x8000"
    main(input_string)