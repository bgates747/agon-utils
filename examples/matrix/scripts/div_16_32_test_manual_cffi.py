#!/usr/bin/env python3
import numpy as np
from SoftFloat import f16_div_softfloat

def parse_float16_input(x):
    """
    Converts input `x` (string, float, int, or hex) to a float16 bit pattern (uint16).
    Accepts:
        - Float literals: 65504.0
        - Special strings: 'inf', '-inf', 'nan'
        - Hex strings: '0x7BFF', 'FE00'
        - Integers: 0x7BFF
    Returns:
        uint16 representing the float16 bit pattern
    """
    if isinstance(x, float):
        return int(np.float16(x).view(np.uint16))
    elif isinstance(x, int):
        return x & 0xFFFF
    elif isinstance(x, str):
        x = x.strip().lower()
        if x.startswith("0x"):
            return int(x, 16) & 0xFFFF
        try:
            val = float(x)
            return int(np.float16(val).view(np.uint16))
        except ValueError:
            raise ValueError(f"Invalid input: {x!r}")
    else:
        raise TypeError(f"Unsupported type for input: {type(x)}")



if __name__ == "__main__":

    # Input as Python float literals
    valA = 7364.0
    valB = -9752.0

    # Convert to float16 bit patterns using NumPy
    opA = parse_float16_input(valA)
    opB = parse_float16_input(valB)

    print('----- DEBUG OUTPUT -----')

    # Perform the division using your SoftFloat-emulated f16_div
    result = f16_div_softfloat(opA, opB)

    # Convert result back to Python float using NumPy
    valR = float(np.array([result], dtype=np.uint16).view(np.float16)[0])
    print(f'0x{opA:04X} / 0x{opB:04X} = 0x{result:04X}')


    # # Output
    # print(f'\r\n----- ASSEMBLY OUTPUT -----')
    # print(f'    call printInline')
    # print(f'    asciz "{valA} / {valB} = {valR}\\r\\n"')
    # print(f'    call printInline')
    # print(f'    asciz "0x{opA:04X} / 0x{opB:04X} = 0x{result:04X}\\r\\n"')
    # print(f'    ld hl,0x{opA:04X} ; {valA}')
    # print(f'    ld de,0x{opB:04X} ; {valB}')
    # print(f'    call f16_div')
    # print(f'    PRINT_HL_HEX " assembly result"')
    # print(f'    call printNewLine')
