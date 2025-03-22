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
18	0x00C500	0x004122	0x00CA6A	0x00CA6B	10001	10000	10010	10010	2	1	3	3	0x008100	0x000122	0x00826A	0x00826B
13	0x00A900	0x00C8D2	0x003606	0x003607	01010	10010	01101	01101	-5	3	-2	-2	0x008100	0x0080D2	0x000206	0x000207
20	0x00C76E	0x004600	0x00D192	0x00D193	10001	10001	10100	10100	2	2	5	5	0x00836E	0x000200	0x008192	0x008193
20	0x004630	0x0048E0	0x00538A	0x00538B	10001	10010	10100	10100	2	3	5	5	0x000230	0x0000E0	0x00038A	0x00038B
9	0x00B43A	0x00AD00	0x002548	0x002549	01101	01011	01001	01001	-2	-4	-6	-6	0x00803A	0x008100	0x000148	0x000149
18	0x004424	0x004080	0x0048A8	0x0048A9	10001	10000	10010	10010	2	1	3	3	0x000024	0x000080	0x0000A8	0x0000A9
20	0x00C8BA	0x00C500	0x0051E8	0x0051E9	10010	10001	10100	10100	3	2	5	5	0x0080BA	0x008100	0x0001E8	0x0001E9
20	0x004810	0x00C6A0	0x00D2BA	0x00D2BB	10010	10001	10100	10100	3	2	5	5	0x000010	0x0082A0	0x0082BA	0x0082BB
19	0x004640	0x0042D0	0x004D52	0x004D53	10001	10000	10011	10011	2	1	4	4	0x000240	0x0002D0	0x000152	0x000153
19	0x00C600	0x00C4CF	0x004F36	0x004F37	10001	10001	10011	10011	2	2	4	4	0x008200	0x0080CF	0x000336	0x000337
20	0x00C600	0x00C8CF	0x005336	0x005337	10001	10010	10100	10100	2	3	5	5	0x008200	0x0080CF	0x000336	0x000337
17	0x004500	0x00BD22	0x00C66A	0x00C66B	10001	01111	10001	10001	2	0	2	2	0x000100	0x008122	0x00826A	0x00826B
17	0x00BCF0	0x004560	0x00C6A2	0x00C6A3	01111	10001	10001	10001	0	2	2	2	0x0080F0	0x000160	0x0082A2	0x0082A3
20	0x00C828	0x00C540	0x005174	0x005175	10010	10001	10100	10100	3	2	5	5	0x008028	0x008140	0x000174	0x000175
21	0x004864	0x004880	0x0054F0	0x0054F1	10010	10010	10101	10101	3	3	6	6	0x000064	0x000080	0x0000F0	0x0000F1
18	0x00C818	0x00BDC0	0x0049E2	0x0049E3	10010	01111	10010	10010	3	0	3	3	0x008018	0x0081C0	0x0001E2	0x0001E3
16	0x003660	0x0048B0	0x004378	0x004379	01101	10010	10000	10000	-2	3	1	1	0x000260	0x0000B0	0x000378	0x000379
17	0x00C2A0	0x003FA0	0x00C650	0x00C651	10000	01111	10001	10001	1	0	2	2	0x0082A0	0x0003A0	0x008250	0x008251
17	0x00442B	0x003E00	0x004640	0x004641	10001	01111	10001	10001	2	0	2	2	0x00002B	0x000200	0x000240	0x000241
17	0x00C858	0x0038C0	0x00C528	0x00C529	10010	01110	10001	10001	3	-1	2	2	0x008058	0x0000C0	0x008128	0x008129" \
"""
    result = process_input(sample_input)
    print(result)
