import numpy as np

def float_to_binary16_hex(value):
    # Convert the value to a NumPy float16
    half = np.float16(value)
    # View the underlying binary data as an unsigned 16-bit integer
    half_int = half.view(np.uint16)
    # Format as hexadecimal with leading "0x"
    return f"0x{half_int:04X}"

def float_to_fixed16_hex(value):
    """
    Convert a decimal value to a 16.8 fixed-point representation.
    The fixed-point number is stored in 24 bits (16 integer bits, 8 fractional bits).
    For negative numbers, compute two's complement (modulo 2^24).
    """
    # Multiply by 256 (2^8) to shift into 16.8 fixed-point format.
    fixed_val = int(round(value * 256))
    if fixed_val < 0:
        fixed_val = (1 << 24) + fixed_val
    return f"0x{fixed_val:06X}"

def main(value, register):
    fixed_hex = float_to_fixed16_hex(value)
    half_hex = float_to_binary16_hex(value)
    # Convert half_hex string to an integer.
    half_int = int(half_hex, 16)
    # Extract the 5-bit exponent field (bits 14..10).
    biased_exponent = (half_int >> 10) & 0x1F
    # Compute the true exponent by subtracting the bias (15).
    true_exponent = biased_exponent - 15
    # Format the biased exponent as a 5-bit binary string.
    biased_bin = format(biased_exponent, '05b')
    # Format the true exponent as a 5-bit binary string.
    true_bin = format(true_exponent, '05b')
    
    asm_line = (f"    ld {register},{half_hex} ; {value}, 16.8 fixed = {fixed_hex} | "
                f"Biased exp: {biased_exponent} ({biased_bin}), True exp: {true_exponent} ({true_bin})")
    print(asm_line)

if __name__ == "__main__":
    register0 = 'hl'
    value1 = 0.007808684396234746
    main(value1, register0)
    register1 = 'de'
    value2 = 0.007808684396234746
    main(value2, register1)
    register2 = 'hl'
    value = value1 * value2
    main(value, register2)