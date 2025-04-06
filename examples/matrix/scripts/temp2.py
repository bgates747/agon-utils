def nibble_string(value, bits=16):
    """Return a spaced binary string, one nibble (4 bits) at a time."""
    return ' '.join(f"{value:0{bits}b}"[i:i+4] for i in range(0, bits, 4))

def extract_f16_components(f16_value):
    """Extract sign, exponent, and mantissa from a float16 value."""
    sign = 0x80 if (f16_value >> 15) & 0x1 else 0x00
    exp = (f16_value >> 10) & 0x1F
    mantissa = f16_value & 0x3FF

    # Add implied 1 bit for normal numbers (exp != 0)
    if exp != 0:
        mantissa |= 0x400  # Set the implied 1 bit (bit 10)

    return sign, exp, mantissa

# Test value
test_value = 0xee70
sign, exp, mant = extract_f16_components(test_value)

print(f"{nibble_string(test_value)}   original (0x{test_value:04x})")
print(f"{nibble_string(sign, 8):>19}   sign       (0x{sign:02x})")
print(f"{nibble_string(exp, 8):>19}   exponent   (0x{exp:02x})")
print(f"{nibble_string(mant, 16)}   mantissa (0x{mant:04x})")
