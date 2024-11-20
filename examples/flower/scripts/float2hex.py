import sys
import math
from decimal import Decimal, getcontext

def float_to_custom_format(x):
    getcontext().prec = 64  # Increase precision

    if x == 0.0:
        exponent_byte = 0x00
        mantissa_bytes = [0x00, 0x00, 0x00, 0x00]
        return exponent_byte, mantissa_bytes

    # Check if x is an integer and fits in 32-bit signed integer
    if x == int(x):
        x_int = int(x)
        if -0x80000000 <= x_int <= 0x7FFFFFFF:
            # Handle as integer
            exponent_byte = 0x00
            x_int &= 0xFFFFFFFF  # Ensure 32-bit unsigned representation
            # Convert to bytes in little-endian order
            mantissa_bytes = [
                x_int & 0xFF,
                (x_int >> 8) & 0xFF,
                (x_int >> 16) & 0xFF,
                (x_int >> 24) & 0xFF
            ]
            return exponent_byte, mantissa_bytes

    # Floating point number handling
    # Get sign bit
    sign_bit = '1' if x < 0 else '0'

    x_abs = abs(Decimal(str(x)))

    # Normalize the mantissa and exponent
    e = x_abs.adjusted()  # Base-10 exponent
    m = x_abs / (Decimal(10) ** e)
    # Convert to binary exponent
    e *= 3.3219280948873626  # Approximate log2(10)
    e = int(e)
    m = x_abs / (Decimal(2) ** e)

    # Adjust m and e to get m in [1.0, 2.0)
    while m < 1:
        m *= 2
        e -= 1
    while m >= 2:
        m /= 2
        e += 1

    # Apply excess-128 bias to exponent
    biased_exponent = e + 128
    exponent_byte = int(biased_exponent) & 0xFF

    # Remove the leading '1' from mantissa
    fractional_part = m - Decimal(1)

    # Extract 31 bits of fractional_part
    mantissa_bits = sign_bit  # Start with the sign bit

    for _ in range(31):
        fractional_part *= 2
        if fractional_part >= 1:
            bit = 1
            fractional_part -= 1
        else:
            bit = 0
        mantissa_bits += str(bit)

    # Round the mantissa
    fractional_part *= 2
    if fractional_part >= 1:
        mantissa_int = int(mantissa_bits, 2) + 1
        if mantissa_int >= (1 << 32):
            # Handle mantissa overflow
            mantissa_int >>= 1
            exponent_byte += 1
            exponent_byte &= 0xFF
    else:
        mantissa_int = int(mantissa_bits, 2)

    # Split mantissa into four bytes (little-endian order)
    mantissa_bytes = [
        mantissa_int & 0xFF,
        (mantissa_int >> 8) & 0xFF,
        (mantissa_int >> 16) & 0xFF,
        (mantissa_int >> 24) & 0xFF
    ]

    return exponent_byte, mantissa_bytes

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python float2hex.py <float_value>")
        sys.exit(1)
    x = float(sys.argv[1])
    exponent_byte, mantissa_bytes = float_to_custom_format(x)

    # Prepare the output in assembly code format with little-endian byte order
    byte_strings = ['0x%02X' % b for b in [exponent_byte] + mantissa_bytes]
    output = 'db   ' + ', '.join(byte_strings)

    # Add a comment with the decimal value
    output += ' ; ' + str(x)

    print(output)
