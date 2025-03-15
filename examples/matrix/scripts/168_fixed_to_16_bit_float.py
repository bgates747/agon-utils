import struct

def float_to_half(f):
    """Converts a 32-bit float (Python float) to IEEE 754 binary16 (half-precision)."""
    # Pack float into 32-bit binary representation
    f32 = struct.unpack('>I', struct.pack('>f', f))[0]
    
    # Extract sign (bit 31), exponent (bits 30-23) and mantissa (bits 22-0)
    sign = (f32 >> 16) & 0x8000
    exponent = ((f32 >> 23) & 0xFF) - 127  # Unbias the exponent from float32
    mantissa = f32 & 0x007FFFFF
    
    # Handle special cases: Inf or NaN
    if exponent == 128:
        # Infinity
        if mantissa == 0:
            return sign | 0x7C00
        # NaN: propagate some mantissa bits (quiet NaN convention)
        mantissa >>= 13
        return sign | 0x7C00 | mantissa | (mantissa == 0)
    
    # Adjust exponent for float16 (bias 15 instead of 127)
    exponent += 15
    
    # Handle exponent overflow/underflow
    if exponent >= 0x1F:  # Overflow: represent as infinity
        return sign | 0x7C00
    elif exponent <= 0:
        # Subnormal numbers (or zero)
        if exponent < -10:
            # Too small: becomes zero
            return sign
        # Convert to subnormal half-precision value.
        mantissa |= 0x00800000  # Add the implicit leading 1
        shift = 14 - exponent
        half_mantissa = (mantissa >> shift) + ((mantissa >> (shift - 1)) & 1)
        return sign | half_mantissa
    else:
        # Normalized number: shift mantissa from 23 to 10 bits with rounding
        mantissa = mantissa + 0x00001000  # 0x1000 is the rounding constant for half
        if mantissa & 0x00800000:
            # Rounding overflow: adjust exponent
            mantissa = 0
            exponent += 1
        if exponent >= 0x1F:
            # Check again for overflow
            return sign | 0x7C00
        return sign | (exponent << 10) | (mantissa >> 13)

def fixed16_8_to_half(fp_value):
    """
    Converts a 16.8 fixed-point number (passed as an integer)
    to IEEE-754 binary16 (half-precision) format.
    """
    # Convert fixed-point to float by dividing by 256.
    f = fp_value / 256.0
    # Convert the float to half-precision
    half = float_to_half(f)
    return half

def main(value_hex):
    """
    Expects a hex string representing a 16.8 fixed-point number.
    For example, '000180' represents 1.5 (384/256 = 1.5).
    """
    try:
        # Convert the hex string to an integer
        fp_value = int(value_hex, 16)
    except ValueError:
        print("Invalid hex string. Please enter a valid 16.8 fixed-point hex string.")
        return

    half_hex = fixed16_8_to_half(fp_value)
    fixed_val_decimal = fp_value / 256.0
    print(f"Fixed-point hex '{value_hex}' (i.e. {fixed_val_decimal}) converts to half-precision: 0x{half_hex:04X}")

if __name__ == "__main__":
    value = '0xFE9968'
    main(value)
