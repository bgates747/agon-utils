import sys
import math
from fractions import Fraction

def float_to_custom_format(x):
    if x == 0.0:
        exponent_bits = '00000000'
        mantissa_bits = '00000000000000000000000000000000'
        exponent_hex = '0x00'
        mantissa_hex = '0x00000000'
        return mantissa_hex, exponent_hex

    # Get sign bit
    if x < 0:
        sign_bit = '1'
    else:
        sign_bit = '0'

    x_abs = abs(x)

    # Get mantissa and exponent using frexp
    m, e = math.frexp(x_abs)  # x_abs = m * 2**e, m in [0.5,1.0)
    # Adjust m and e to get m in [1.0,2.0)
    m *= 2
    e -= 1

    # Now m in [1.0,2.0)
    # Get biased exponent
    biased_exponent = e + 128

    # Convert biased exponent to 8-bit binary and then to hex
    exponent_bits = format(int(biased_exponent) & 0xFF, '08b')
    exponent_hex = '0x' + format(int(exponent_bits, 2), '02X')

    # Get fractional part of mantissa
    fractional_part = Fraction(m - 1).limit_denominator(2**32)

    # Get 31 bits of fractional_part
    bits = []
    for i in range(31):
        fractional_part *= 2
        bit = int(fractional_part)
        bits.append(str(bit))
        fractional_part -= bit

    mantissa_bits = sign_bit + ''.join(bits)

    # Convert mantissa bits to hex
    mantissa_hex = '0x' + format(int(mantissa_bits, 2), '08X')

    return mantissa_hex, exponent_hex

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python float2hex.py <float_value>")
        sys.exit(1)
    x = float(sys.argv[1])
    mantissa_hex, exponent_hex = float_to_custom_format(x)
    print("Mantissa (hex):", mantissa_hex)
    print("Exponent (hex):", exponent_hex)
