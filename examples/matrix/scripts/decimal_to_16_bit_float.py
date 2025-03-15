import numpy as np

def float_to_binary16_hex(value):
    # Convert the value to a NumPy float16
    half = np.float16(value)
    # View the underlying binary data as an unsigned 16-bit integer
    half_int = half.view(np.uint16)
    # Format as hexadecimal with leading "0x"
    return f"0x{half_int:04X}"

def main(value):
    hex_representation = float_to_binary16_hex(value)
    print(f"The IEEE-754 binary16 representation of {value} is: {hex_representation}")

if __name__ == "__main__":
    value = -358.59375
    main(value)
