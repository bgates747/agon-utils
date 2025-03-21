#!/usr/bin/env python3
import sys

def compute_true_exponent(fp16_hex):
    """
    Given a hex string for an FP16 value (e.g. "0x009CE4"),
    consider only the lower 16 bits (last 4 hex digits if longer) and compute:
      - the stored exponent (the 5-bit field)
      - the "true" exponent that the multiplication step should use.
      
    For normalized numbers (exponent != 0):
       E_true = exponent_field - 15
    For subnormals (exponent == 0 and fraction != 0):
       E_true = -15 - shift_count
    where shift_count is the number of left shifts required to move the most
    significant 1 of the 10-bit fraction into bit position 9 (zero-indexed),
    which represents the assumed 1 position in a normalized number.
    
    (Note: For zero (fraction==0) we return E_true = -15.)
    """
    s = fp16_hex.strip()
    if s.lower().startswith("0x"):
        s = s[2:]
    if len(s) > 4:
        s = s[-4:]
    try:
        val = int(s, 16)
    except ValueError:
        return None, None

    exponent_field = (val >> 10) & 0x1F
    fraction = val & 0x03FF  # lower 10 bits
    if exponent_field != 0:
        # Normalized: true exponent = (exponent_field - bias)
        true_exp = exponent_field - 15
    else:
        # Subnormal: if fraction is zero, we treat it as zero.
        if fraction == 0:
            true_exp = -15  # convention; zero doesn't really have an exponent
        else:
            # Count leading zeros in the 10-bit fraction.
            bin_fraction = format(fraction, '010b')
            shift_count = bin_fraction.find('1')
            # The formula: true exponent = -15 - shift_count
            true_exp = -15 - shift_count
    return exponent_field, true_exp

def process_input(text):
    """
    Process multi-line text in the format:
    
    bexp    0xop1      0xop2      0xpython   0xasm   ex_p  ex_a  man_p  man_a
    36      0x009CE4   0x00826D  0x000003  0x0013DE 00000 00100 0x000003 0x0003DE
    ...
    
    For each record, compute the stored exponent and true exponent for the
    two FP16 operands (0xop1 and 0xop2).
    """
    lines = text.strip().splitlines()
    output_lines = []
    
    # Remove header if present
    if lines and "bexp" in lines[0]:
        header = lines.pop(0)
    
    for idx, line in enumerate(lines, start=1):
        fields = line.split()
        if len(fields) < 3:
            continue
        op1 = fields[1]  # second column: 0xop1
        op2 = fields[2]  # third column: 0xop2
        stored1, true1 = compute_true_exponent(op1)
        stored2, true2 = compute_true_exponent(op2)
        output_lines.append(
            f"Record {idx}: op1 {op1} -> stored exponent {stored1}, true exponent {true1}; "
            f"op2 {op2} -> stored exponent {stored2}, true exponent {true2}"
        )
    
    return "\n".join(output_lines)

if __name__ == "__main__":
    # Sample multi-line input (you can pipe from a file or use input())
    sample_input = """\
bexp	op1	op2	python	asm	eop1	eop2	ex_p	ex_a	eop1	eop2	ex_p	ex_a	man_op1	man_op2	man_p	man_a
-5	0x009CE4	0x00826D	0x000003	0x00001E	00111	00000	00000	00000	-8	0	0	0	0x0080E4	0x00826D	0x000003	0x00001E
-7	0x008113	0x009F17	0x000002	0x000004	00000	00111	00000	00000	0	-8	0	0	0x008113	0x008317	0x000002	0x000004
-13	0x00033F	0x00066F	0x000000	0x000005	00000	00001	00000	00000	0	-14	0	0	0x00033F	0x00026F	0x000000	0x000005
-10	0x00005C	0x00A0AF	0x008001	0x008035	00000	01000	00000	00000	0	-7	0	0	0x00005C	0x0080AF	0x008001	0x008035
-11	0x008062	0x009D5E	0x000001	0x000010	00000	00111	00000	00000	0	-8	0	0	0x008062	0x00815E	0x000001	0x000010
"""
    result = process_input(sample_input)
    print(result)
