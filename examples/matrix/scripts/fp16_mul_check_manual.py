#!/usr/bin/env python3
import struct
import numpy as np
from SoftFloat import float_to_float32_bits, float_to_f16_bits, f16_mul_softfloat, f16_to_f32_softfloat

# ----------------------------
# Decoding and Formatting Functions
# ----------------------------
def decode_fp16(val):
    """
    Decodes a 16-bit integer (representing an IEEE 754 binary16 value)
    into its sign, exponent, and mantissa fields.
    For normalized numbers, the implicit leading bit is '1'; for subnormals it is '0'.
    """
    bin_str = format(val, '016b')
    sign = bin_str[0]
    exponent = bin_str[1:6]
    fraction = bin_str[6:]
    assumed = "1" if exponent != "00000" else "0"
    mantissa = assumed + fraction
    return sign, exponent, mantissa


def format_fp16_output(val):
    """
    Given a 16-bit integer representing a float16 value, pack it into 3 bytes
    (2 bytes for the value and a pad byte 0) to form a 24-bit little-endian number.
    Then, format and return a string with the hex representation, the raw binary
    split into three 8-bit segments, the decoded sign, exponent, mantissa, and
    the decimal value (via f16_to_f32_softfloat).
    """
    # Pack into 3 bytes: two bytes for the 16-bit value and one pad byte (0)
    packed = struct.pack('<HB', val, 0)
    val_uint24 = int.from_bytes(packed, 'little')
    hex_field = f"0x{val_uint24:06X}"
    raw_bin = format(val_uint24, '024b')
    byte1 = raw_bin[:8]
    byte2 = raw_bin[8:16]
    byte3 = raw_bin[16:]
    s, exp, mantissa = decode_fp16(val)
    # Convert float16 (given as 16-bit int) to a Python float via SoftFloat.
    decimal_value = f16_to_f32_softfloat(val)
    return (f"{hex_field}\tRaw: {byte1} {byte2} {byte3}\t"
            f"Sign: {s}\tExponent: {exp}\tMantissa: {mantissa}\t"
            f"Decimal: {decimal_value}")


# ----------------------------
# Main Execution
# ----------------------------
if __name__ == "__main__":
    # Input parameters (hard-coded)
    a_input = -0.87353515625	
    b_input = 25216

    # Convert the Python floats to half-precision using SoftFloat.
    a_f16 = float_to_f16_bits(a_input)  # 16-bit integer representation for a
    b_f16 = float_to_f16_bits(b_input)  # 16-bit integer representation for b

    # Multiply the two half-precision values using SoftFloat.
    result_f16 = f16_mul_softfloat(a_f16, b_f16)

    # Print the outputs in the required format.
    print(format_fp16_output(a_f16))
    print(format_fp16_output(b_f16))
    print(format_fp16_output(result_f16))
