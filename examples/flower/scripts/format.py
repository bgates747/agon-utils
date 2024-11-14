def reformat_file(input_file, output_file, col1_width, col2_width, col3_width):
    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        for line in infile:
            # Replace all tabs with a single space
            line = line.replace('\t', ' ')
            # Ensure each line begins with exactly one space
            line = ' ' + line.lstrip()

            # Split the line into main sections based on delimiters
            parts = line.split('||')
            if len(parts) == 1:
                # If there's only one set of pipes, handle the first part and output the address
                col1 = parts[0]
                col2 = ''
                col3 = ''
            elif len(parts) == 2:
                # If there are two sets of pipes, split col1 and handle the addresses
                col1 = parts[0]
                col2 = ''
                col3 = parts[1]
            elif len(parts) == 3:
                # If there are three sets of pipes, split all columns accordingly
                col1 = parts[0]
                col2 = parts[1]
                col3 = parts[2]
            else:
                continue  # Skip lines that don't match the expected pattern

            # Split col1 and col2 into sub-columns
            sub_parts1 = col1.split(';')
            col1_instr = sub_parts1[0].strip() if len(sub_parts1) > 0 else ''
            col1_addr = sub_parts1[1].strip() if len(sub_parts1) > 1 else ''

            sub_parts2 = col2.split(';')
            col2_instr = sub_parts2[0].strip() if len(sub_parts2) > 0 else ''
            col2_addr = sub_parts2[1].strip() if len(sub_parts2) > 1 else ''

            # Format columns with appropriate padding
            col1_instr = col1_instr.ljust(col1_width)[:col1_width]
            col2_instr = col2_instr.ljust(col2_width)[:col2_width]

            # Construct address part, making sure both addresses are side-by-side if available
            col3_addr = f"{col1_addr} {col2_addr}".strip().ljust(col3_width)[:col3_width]

            # Construct final formatted line
            formatted_line = f"{col1_instr} ; {col2_instr} | {col3_addr} || {col3.strip()}"
            outfile.write(formatted_line + '\n')

# Parameters for column widths - tweakable to get the desired spacing
COL1_WIDTH = 16
COL2_WIDTH = 16
COL3_WIDTH = 13

# Input and output files
INPUT_FILE = 'utils/dif/bbcbasic24ez.dif'
OUTPUT_FILE = f'{INPUT_FILE.split(".")[0]}.inc'

# Run the reformatting
reformat_file(INPUT_FILE, OUTPUT_FILE, COL1_WIDTH, COL2_WIDTH, COL3_WIDTH)
