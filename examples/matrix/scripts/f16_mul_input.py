#!/usr/bin/env python3
import sys

def compute_true_exponent(fp16_hex):
    """
    Given a hex string for an FP16 value (e.g. "0x009CE4"),
    use only the lower 16 bits (i.e. last 4 hex digits if longer)
    and compute the true (unbiased) exponent.
    
    For normal numbers: true_exponent = exponent_field - 15.
    For subnormals (exponent_field==0): we return -14 (if nonzero fraction).
    """
    s = fp16_hex.strip()
    if s.lower().startswith("0x"):
        s = s[2:]
    # If longer than 4 digits, assume the lower 16 bits are used.
    if len(s) > 4:
        s = s[-4:]
    try:
        val = int(s, 16)
    except ValueError:
        return None
    exponent_field = (val >> 10) & 0x1F
    if exponent_field == 0:
        # Subnormal numbers (nonzero fraction) use an effective exponent of -14.
        return -14
    else:
        return exponent_field - 15

def process_input(text):
    """
    Process multi-line text in the format:
    
    bexp    0xop1    0xop2    0xpython    0xasm    ex_p    ex_a    man_p    man_a
    36      0x009CE4    0x00826D    0x000003    0x0013DE    00000    00100    0x000003    0x0003DE
    ...
    
    For each record (ignoring header if found), compute the true exponent of 0xop1 and 0xop2.
    """
    lines = text.strip().splitlines()
    output_lines = []
    
    # Check if the first line contains "0xop1" (header)
    if lines and "0xop1" in lines[0]:
        header = lines.pop(0)
    
    for idx, line in enumerate(lines, start=1):
        # Split on whitespace; expect at least 3 fields: bexp, 0xop1, 0xop2, ...
        fields = line.split()
        if len(fields) < 3:
            continue
        op1 = fields[1]  # second column: 0xop1
        op2 = fields[2]  # third column: 0xop2
        true_exp_op1 = compute_true_exponent(op1)
        true_exp_op2 = compute_true_exponent(op2)
        output_lines.append(f"Record {idx}: op1 {op1} -> true exponent {true_exp_op1}, op2 {op2} -> true exponent {true_exp_op2}")
    
    return "\n".join(output_lines)

if __name__ == "__main__":
    # Example multi-line input (you can also pipe this from a file or stdin)
    sample_input = """\
bexp\t0xop1\t0xop2\t0xpython\t0xasm\tex_p\tex_a\tman_p\tman_a
36\t0x009CE4\t0x00826D\t0x000003\t0x0013DE\t00000\t00100\t0x000003\t0x0003DE
31\t0x009E6E\t0x000098\t0x008001\t0x00FFA3\t00000\t11111\t0x008001\t0x0083A3
33\t0x0003AA\t0x0019F4\t0x000003\t0x000574\t00000\t00001\t0x000003\t0x000174
34\t0x008113\t0x009F17\t0x000002\t0x0008C7\t00000\t00010\t0x000002\t0x0000C7
28\t0x00033F\t0x00066F\t0x000000\t0x007139\t00000\t11100\t0x000000\t0x000139
34\t0x009DE8\t0x000398\t0x008005\t0x00894E\t00000\t00010\t0x008005\t0x00814E
36\t0x001FB2\t0x0083FF\t0x008008\t0x00937C\t00000\t00100\t0x008008\t0x00837C
26\t0x008021\t0x0012D0\t0x008000\t0x00EB07\t00000\t11010\t0x008000\t0x008307
33\t0x001F02\t0x000201\t0x000004\t0x000706\t00000\t00001\t0x000004\t0x000306
34\t0x000353\t0x009EC3\t0x008006\t0x00899F\t00000\t00010\t0x008006\t0x00819F
31\t0x00005C\t0x00A0AF\t0x008001\t0x00FEBC\t00000\t11111\t0x008001\t0x0082BC
30\t0x008062\t0x009D5E\t0x000001\t0x007838\t00000\t11110\t0x000001\t0x000038
"""
    result = process_input(sample_input)
    print(result)
