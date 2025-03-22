#!/usr/bin/env python3
import sys

def compute_true_exponent(fp16_hex):
    """
    Given a hex string for an FP16 value (e.g. "0x009CE4"),
    consider only the lower 16 bits (last 4 hex digits if longer) and compute:
      - the stored exponent (the 5-bit field)
      - the "true" exponent for multiplication arithmetic.
      
    For normalized numbers (exponent != 0):
       E_true = exponent_field - 15
    For subnormals (exponent == 0 and fraction != 0):
       Count left shifts required to normalize the 10-bit fraction.
       E_true = -15 - shift_count
    (For zero (fraction==0) we return -15.)
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
        true_exp = exponent_field - 15
    else:
        if fraction == 0:
            true_exp = -15  # zero case
        else:
            # Count how many left shifts needed to move the MSB of fraction to bit 9.
            # Convert fraction to a 10-bit binary string.
            bin_fraction = format(fraction, '010b')
            shift_count = bin_fraction.find('1')
            true_exp = -15 - shift_count
    return exponent_field, true_exp

def process_input(text):
    """
    Process multi-line text in the format:
    
    bexp    0xop1      0xop2      0xpython   0xasm   ex_p   ex_a   man_p   man_a
    36      0x009CE4   0x00826D  0x000003  0x0013DE 00000  00100  0x000003  0x0003DE
    ...
    
    For each record, extract the three FP16 hex values:
      - op1 (second column)
      - op2 (third column)
      - product (the third hex value, here assumed to be the '0xpython' column)
    Then compute the stored exponent (SE) and true exponent (TE) for each.
    
    The output is one compact line per record with columns aligned.
    The exponents are printed in a field 3 characters wide.
    """
    lines = text.strip().splitlines()
    output_lines = []
    
    # Remove header if present
    if lines and "bexp" in lines[0]:
        header = lines.pop(0)
    
    for line in lines:
        fields = line.split()
        if len(fields) < 4:
            continue
        op1 = fields[1]   # 0xop1
        op2 = fields[2]   # 0xop2
        product = fields[3]  # product from SoftFloat ("0xpython")
        
        stored1, true1 = compute_true_exponent(op1)
        stored2, true2 = compute_true_exponent(op2)
        stored_prod, true_prod = compute_true_exponent(product)
        
        # Format exponents to 3-character fields (including sign)
        se1 = f"{stored1:3d}"
        te1 = f"{true1:3d}"
        se2 = f"{stored2:3d}"
        te2 = f"{true2:3d}"
        se_prod = f"{stored_prod:3d}"
        te_prod = f"{true_prod:3d}"
        
        # Build a compact output line.
        line_out = (f"{op1} SE{se1} TE{te1} | "
                    f"{op2} SE{se2} TE{te2} | "
                    f"{product} SE{se_prod} TE={te_prod}")
        output_lines.append(line_out)
    
    return "\n".join(output_lines)

if __name__ == "__main__":
    # Sample multi-line input (you can pipe from a file or use input())
    sample_input = """\
bexp	op1	op2	python	asm	eop1	eop2	ex_p	ex_a	eop1	eop2	ex_p	ex_a	man_op1	man_op2	man_p	man_a
-5	0x009CE4	0x00826D	0x000003	0x00001E	00111	00000	00000	00000	-8	0	0	0	0x0080E4	0x00826D	0x000003	0x00001E
-7	0x008113	0x009F17	0x000002	0x000004	00000	00111	00000	00000	0	-8	0	0	0x008113	0x008317	0x000002	0x000004
-9	0x0005C3	0x0014CC	0x000002	0x000000	00001	00101	00000	00000	-14	-10	0	0	0x0001C3	0x0000CC	0x000002	0x000000
"""
    result = process_input(sample_input)
    print(result)
