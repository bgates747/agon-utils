import re
import tempfile
import os

def load_lookup_data(lookup_filename):
    """Load lookup data from a file and return a dictionary with addresses as keys."""
    lookup_data = {}
    with open(lookup_filename, 'r') as lookup_file:
        for line in lookup_file:
            # Extract the address and the text up to the double pipe
            match = re.search(r'(\b[0-9A-Fa-f]{6}\b).*?(\|\|)', line)
            if match:
                address = match.group(1)
                text = line[:match.start(2)].strip()  # Text up to and including '||'
                lookup_data[address] = text
    return lookup_data

def expand_lines(input_filename, temp_filename):
    """Read input lines, expand multibyte lines, and write to a temporary file."""
    with open(input_filename, 'r') as infile, open(temp_filename, 'w') as temp_file:
        lines = infile.readlines()
        current_address = None  # Tracks the current address

        for line in lines:
            # Splitting the line based on fixed-width columns
            col1 = line[:7].strip()      # Address (7 chars)
            col2 = line[7:19].strip()    # Byte code (12 chars)
            col3_and_4 = line[19:].rstrip()  # Line number and source code (rest of the line)

            # Separate the line number and source code
            col3_split = col3_and_4.split(maxsplit=1)
            col3 = col3_split[0].strip().rjust(8) if col3_split else ""
            col4 = col3_split[1] if len(col3_split) > 1 else ""

            # Update the current address if available
            if col1:
                try:
                    current_address = int(col1, 16)
                except ValueError:
                    current_address = None

            # Expand byte code if present
            if col2:
                bytes_list = col2.split()

                # Write the first byte with source line details
                if current_address is not None:
                    temp_file.write(f"{current_address:06X} {bytes_list[0]:<3} {col3} {col4}\n")
                    for byte in bytes_list[1:]:
                        current_address += 1
                        temp_file.write(f"{current_address:06X} {byte:<3}\n")
                else:
                    temp_file.write(f"{' ' * 7} {bytes_list[0]:<3} {col3} {col4}\n")
                    for byte in bytes_list[1:]:
                        temp_file.write(f"{' ' * 7} {byte:<3}\n")
            else:
                # Handle lines without byte code
                if col3 or col4:
                    temp_file.write(f"{' ' * 7} {' ' * 3} {col3} {col4}\n")
                else:
                    temp_file.write(f"{' ' * 7}\n")

def generate_final_output(temp_filename, final_output_filename, lookup_data):
    """Generate the final output file with lookup data on the left and expanded lines on the right."""
    with open(temp_filename, 'r') as temp_file, open(final_output_filename, 'w') as final_outfile:
        for line in temp_file:
            # Extract the address from the expanded line
            address_match = re.match(r'^([0-9A-F]{6})', line.strip())
            if address_match:
                address = address_match.group(1)
                lookup_text = lookup_data.get(address, '                 ;                                    ')
                final_outfile.write(f"{lookup_text:<54} {line.strip()}\n")
            else:
                final_outfile.write(f"{'                 ;                                                   '} {line.strip()}\n")  # Pad unmatched lines on the left

def expand_multibyte_lines(input_filename, lookup_filename, final_output_filename):
    """Main function to coordinate expanding lines and generating final output."""
    # Step 1: Load lookup data
    lookup_data = load_lookup_data(lookup_filename)

    # Step 2: Create a temporary file to store expanded lines
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_file:
        temp_filename = temp_file.name

    try:
        # Step 3: Expand lines and write to temporary file
        expand_lines(input_filename, temp_filename)

        # Step 4: Generate final output file
        generate_final_output(temp_filename, final_output_filename, lookup_data)
    finally:
        # Step 5: Clean up the temporary file
        os.remove(temp_filename)

if __name__ == "__main__":
    input_filename = 'utils/dif/bbcbasic24ez.lst'
    lookup_filename = 'utils/dif/bbcbasic24ez.inc'
    final_output_filename = 'utils/dif/bbcbasic24ez_final.inc'
    expand_multibyte_lines(input_filename, lookup_filename, final_output_filename)
