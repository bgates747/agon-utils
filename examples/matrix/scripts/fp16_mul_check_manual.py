#!/usr/bin/env python3
import struct
import numpy as np
from SoftFloat import float_to_f16_bits, f16_mul_softfloat, f16_to_f32_softfloat

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

def format_fp16_output(val):
    """
    Given a 16-bit integer representing a float16 value, pack it into 3 bytes
    (2 bytes for the value and a pad byte 0) to form a 24-bit little-endian number.
    Then, format and return a string with the hex representation, the raw binary
    split into three 8-bit segments, the decoded sign, exponent, and a formatted mantissa,
    and the decimal value (via f16_to_f32_softfloat).
    
    The formatted mantissa displays the implied bit, then a space, then the top 2 bits of the fraction,
    then a space, then the lower 8 bits of the fraction.
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
    # Format the mantissa: if normalized, mantissa length is 11; if subnormal, 10.
    if len(mantissa) == 11:
        # For normalized numbers, the format becomes: implied_bit, space, next 2 bits, space, remaining 8 bits.
        formatted_mantissa = f"{mantissa[0]} {mantissa[1:3]} {mantissa[3:]}"
    elif len(mantissa) == 10:
        # For subnormals, do the same (implied bit is '0').
        formatted_mantissa = f"{mantissa[0]} {mantissa[1:3]} {mantissa[3:]}"
    else:
        formatted_mantissa = mantissa

    decimal_value = f16_to_f32_softfloat(val)
    return (f"{hex_field} r:{byte1} {byte2} {byte3} "
            f"s:{s} e:{exp} m:{formatted_mantissa} "
            f"d:{decimal_value}")

# ----------------------------
# Intermediate Mantissa Multiplication Functions
# ----------------------------
def get_mantissa(fp16):
    """
    Extracts the 11-bit mantissa from a 16-bit float16 representation.
    For normals, returns (1<<10)|fraction; for subnormals, just the fraction.
    """
    fraction = fp16 & 0x03FF      # lower 10 bits
    exponent = (fp16 >> 10) & 0x1F  # 5-bit exponent
    if exponent != 0:
        # Normalized number: implicit 1 is added as bit 10.
        mantissa = (1 << 10) | fraction
    else:
        # Subnormal: no implicit 1.
        mantissa = fraction
    return mantissa

def format_mantissa_product(a_fp16, b_fp16):
    """
    Multiplies the 11-bit mantissae (with implicit bit for normals)
    of two float16 numbers to produce a 22-bit product,
    and returns both the 6-digit hex (zero-padded to 24 bits) and the byte-separated
    24-bit binary string.
    Note: The product is not left-shifted.
    """
    m1 = get_mantissa(a_fp16)
    m2 = get_mantissa(b_fp16)
    product = m1 * m2  # 22-bit product, maximum result from two 11-bit numbers
    # Represent product in a 24-bit format without any left-shift.
    product_24 = product
    hex_field = f"0x{product_24:06X}"
    bin_str = f"{product_24:024b}"
    formatted_bin = f"{bin_str[0:8]} {bin_str[8:16]} {bin_str[16:24]}"
    return hex_field, formatted_bin

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
    mantissa_hex, mantissa_bin = format_mantissa_product(a_f16, b_f16)

    # Print the SoftFloat outputs.
    print(format_fp16_output(a_f16))
    print(format_fp16_output(b_f16))
    print(f"{mantissa_hex} r:{mantissa_bin}")
    print(format_fp16_output(result_f16))
    print(format_fp16_output(assembly_output))
    
    # --- Generate the assembly test code ---
    #
    # We generate the following assembly snippet:
    #
    #   ld hl,0x000CF8 ; 0.0003032684326171875
    #   ld de,0x00ADFE ; -0.0936279296875
    #   call float16_smul 
    #   push hl
    #   call printInline
    #   asciz "-2.8371810913085938e-05\r\n0081DC 00000000 10000001 11011100\r\n"
    #
    # The product's decimal value (in scientific notation) and its 24-bit fields
    # are generated from our SoftFloat multiplication result.
    
    # Get float (decimal) values for the operands and product.
    a_float = f16_to_f32_softfloat(a_f16)
    b_float = f16_to_f32_softfloat(b_f16)
    product_float = f16_to_f32_softfloat(result_f16)
    
    # Format the float values in a human-readable (or scientific) form.
    # Adjust precision as desired.
    a_float_str = f"{a_float:.16e}"
    b_float_str = f"{b_float:.16e}"
    product_float_str = f"{product_float:.16e}"
    
    # For the product, generate the 24-bit representation.
    packed = struct.pack('<HB', result_f16, 0)
    val_uint24 = int.from_bytes(packed, 'little')
    # Format the 24-bit hex without the "0x" prefix.
    result_hex_str = f"{val_uint24:06X}"
    # Get the raw 24-bit binary split into three groups.
    raw_bin = format(val_uint24, '024b')
    raw_parts = f"{raw_bin[:8]} {raw_bin[8:16]} {raw_bin[16:]}"
    
    # Now, generate the assembly test code.
    asm_lines = []
    asm_lines.append(f"    ld hl,{a_hex} ; {a_float_str}")
    asm_lines.append(f"    ld de,{b_hex} ; {b_float_str}")
    asm_lines.append("    call float16_smul")
    asm_lines.append("    push hl")
    asm_lines.append("    call printInline")
    # The asciz string: first line is the product's decimal value, second line the FP16 fields.
    asm_lines.append(f'    asciz "\\r\\n{product_float_str}\\r\\n{result_hex_str} {raw_parts}\\r\\n"')
    
    print("\n; --- Generated Assembly Test Code ---")
    for line in asm_lines:
        print(line)

# ----------------------------
# Main Execution
# ----------------------------
if __name__ == "__main__":
    input_string = "0x00C0B9	0x00C3E5	0x0048A9	0x0048A9"
    main(input_string)
