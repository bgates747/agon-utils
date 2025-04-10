from cffi import FFI
import struct
import numpy as np

# Initialize CFFI
ffi = FFI()
softfloat_path = "/home/smith/Agon/mystuff/agon-utils/utils/SoftFloat-3e/build/Linux-x86_64-GCC/softfloat.so"
ffi.cdef("unsigned short f16_mul(unsigned short a, unsigned short b);")
lib = ffi.dlopen(softfloat_path)

def f16_mul_softfloat_cffi(input_string):
    def f16_to_f32_softfloat(bits):
        """Converts a 16-bit integer bit pattern to a float32."""
        f16 = np.uint16(bits).view(np.float16)
        return np.float32(f16)

    def decode_fp16(val):
        bin_str = format(val, '016b')
        sign = bin_str[0]
        exponent = bin_str[1:6]
        fraction = bin_str[6:]
        assumed = "1" if exponent != "00000" else "0"
        mantissa = assumed + fraction
        return sign, exponent, mantissa

    def format_fp16_output(val, description=""):
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
            mantissa_val = 0x0400 | frac_bits
        else:
            mantissa_val = frac_bits
        mantissa_hex = f"{mantissa_val:04x}"
        mantissa_bin = f"{mantissa_val:011b}".zfill(11)
        mantissa_byte1 = mantissa_bin[:3]
        mantissa_byte2 = mantissa_bin[3:]
        dec_val = f16_to_f32_softfloat(val)
        return f"; {val_hex} {byte1} {byte2} {sign_hex} {exp_hex} {mantissa_hex} {mantissa_byte1} {mantissa_byte2} {dec_val} {description}"

    def get_mantissa_and_exp(fp16):
        fraction = fp16 & 0x03FF
        exponent = (fp16 >> 10) & 0x1F
        if exponent != 0:
            mantissa = (1 << 10) | fraction
            return mantissa, exponent - 15
        else:
            if fraction == 0:
                return 0, -14
            shift = 0
            while (fraction & 0x0400) == 0:
                fraction <<= 1
                shift += 1
            mantissa = fraction & 0x07FF
            exponent = -14 - shift + 1
            return mantissa, exponent

    def hex_bin_format(val, width=16):
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

    # ---- Main Logic ----

    parts = input_string.strip().split()
    if len(parts) < 4:
        print("Error: expected 4 hex numbers separated by whitespace.")
        exit(1)

    a_hex, b_hex, expected_hex, output_hex = parts[:4]
    a_f16 = int(a_hex, 16)
    b_f16 = int(b_hex, 16)
    expected_f16 = int(expected_hex, 16)
    assembly_output = int(output_hex, 16)

    # Use the real C-based softfloat
    result_f16 = int(lib.f16_mul(a_f16, b_f16))

    print("; --- Inputs / Outputs ---")
    print(format_fp16_output(a_f16, "sigA"))
    print(format_fp16_output(b_f16, "sigB"))
    print(format_fp16_output(result_f16, "Expected Result"))
    print(format_fp16_output(assembly_output, "Assembly Result"))

    print("\n; --- Intermediate Results ---")
    for line in print_intermediate_result(a_f16, b_f16):
        print(line)

    # Assembly code output
    print("\n; --- Generated Assembly Test Code ---")
    print(f"    ld hl,{a_hex}")
    print(f"    ld de,{b_hex}")
    print(f"    ld bc,{expected_hex}")

# ----------------------------
# Main Execution
# ----------------------------
if __name__ == "__main__":
    input_string = "0x3830	0xF828	0xF45A	0xFC00"
    f16_mul_softfloat_cffi(input_string)