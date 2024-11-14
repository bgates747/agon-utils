
import os
import json
import subprocess
import tempfile

# Load JSON data from a file
def load_json(path):
    """Load JSON data from a file."""
    with open(path, 'r') as f:
        return json.load(f)

# Ensure output directory exists
def create_output_dir(directory):
    """Create output directory if it doesn't exist."""
    os.makedirs(directory, exist_ok=True)

def write_combined_file(base_name, symbols_to_include, api_includes_top, api_includes_bottom, OUTPUT_DIR):
    output_path = os.path.join(OUTPUT_DIR, base_name)
    with open(output_path, 'w') as f:
        # Write the custom header with SKIP_AHEAD and two line breaks
        f.write("SKIP_AHEAD: JP BEGIN_HEREISH-0x040000\n\n")

        # Write API includes at the top (copy their contents)
        for api_include in api_includes_top:
            api_include_path = os.path.join("./", api_include)
            f.write(f"; Begin {api_include}\n")
            with open(api_include_path, 'r') as inc_file:
                inc_content = inc_file.read()
                f.write(inc_content)
                f.write("\n")
            f.write(f"; End {api_include}\n\n")

        # Write symbols as specified (use placeholders for non-EQU symbols)
        for symbol in symbols_to_include:
            # Write the comment indicating the source file of the definition
            f.write(f"; Defined in {symbol['def_file']}\n")
            if "EQU" in symbol["def_content"]:
                f.write(f"{symbol['def_content']}\n")
            else:
                # Use placeholder for non-EQU symbols
                symbol_name = symbol['def_content'].split(':')[0]
                f.write(f"{symbol_name}: DL 0x040000\n")
        f.write("\n")
        
        # Footer with BEGIN_HEREISH: $
        f.write("BEGIN_HEREISH:\n\n")

        # Copy the contents of the file we're processing into the output file
        source_file_path = os.path.join("./", base_name)
        with open(source_file_path, 'r') as source_file:
            source_content = source_file.read()
            f.write(source_content)
            f.write("\n")

        # Append the contents of additional files at the bottom
        for additional_file in api_includes_bottom:
            f.write(f"; Begin {os.path.basename(additional_file)}\n")
            additional_file_path = additional_file  # Paths are already relative
            with open(additional_file_path, 'r') as add_file:
                add_content = add_file.read()
                f.write(add_content)
                f.write("\n")
            f.write(f"; End {os.path.basename(additional_file)}\n\n")

    print(f"Written combined file to {output_path}")

# Process files to collect and write symbols
def process_files(source_files, label_defs, label_refs, api_includes_top, api_includes_bottom, api_includes_combined, OUTPUT_DIR):
    api_files_combined = set(os.path.basename(path) for path in api_includes_combined)  # Base names of API include files

    for file_name in source_files:
        base_name = os.path.basename(file_name)

        # Collect needed symbol definitions for this file, excluding self-defined and API-defined symbols
        symbols_to_include = []
        included_symbol_names = set()  # To avoid duplicate symbol definitions

        # Iterate over all symbols referenced in the file
        for symbol_name, references in label_refs.items():
            # Check if this file references the symbol
            if any(ref["ref_file"] == base_name for ref in references):
                if symbol_name in label_defs:
                    # Find definitions of the symbol
                    for definition in label_defs[symbol_name]:
                        def_file = definition["def_file"]
                        if def_file != base_name and def_file not in api_files_combined:
                            # Exclude symbols already included
                            if symbol_name not in included_symbol_names:
                                symbols_to_include.append(definition)
                                included_symbol_names.add(symbol_name)

        # Write the combined file with API includes, external symbol definitions, and the original source include
        write_combined_file(base_name, symbols_to_include, api_includes_top, api_includes_bottom, OUTPUT_DIR)

def adjust_addresses(input_path, output_path, offset):
    """Adjust address comments in the disassembly output by adding an offset."""
    with open(input_path, 'r') as infile, open(output_path, 'w') as outfile:
        for line in infile:
            # Remove newline characters
            line = line.rstrip('\n')
            # Split the line into code and comment
            parts = line.split(';', 1)
            code_part = parts[0].rstrip()
            if len(parts) > 1:
                # Extract the existing address from the comment
                comment_part = parts[1].strip()
                # Try to parse the address in the comment
                try:
                    # Assume the address is in hexadecimal
                    address = int(comment_part, 16)
                    # Add the offset to the address
                    adjusted_address = address + offset
                    # Format the new address comment
                    new_comment_part = f"; {adjusted_address:06X}"
                except ValueError:
                    # If parsing fails, keep the original comment
                    new_comment_part = f"; {comment_part}"
            else:
                # No comment present
                new_comment_part = ''
            # Calculate padding to align the address comments at a specific column (e.g., 32)
            padding = max(1, 32 - len(code_part))
            # Combine code and new comment
            padded_line = f"{code_part}{' ' * padding}{new_comment_part}\n"
            # Write the adjusted line to the output file
            outfile.write(padded_line)

if __name__ == "__main__":
    # List of files to scan for symbol definitions and references
    source_files = [
        # "agon_graphics.asm", # done
        # "agon_sound.asm", # Macro [VDU] in "macros.inc" line 36 - Unknown label, invalid number 'OSWRCH' CALL    OSWRCH Invoked from "agon_sound.asm" line 85 as VDU     23                      ; Send the sound command
        # "eval.asm", # done
        # "exec.asm", # done
        # "fpp.asm", # done
        # "gpio.asm", # done
        # "init.asm", # done
        # "interrupts.asm", # done
        # "main.asm", # done
        # "misc.asm", # done
        "patch.asm", # done
        # "sorry.asm", # done
        # "bbcbasic24.asm",
    ]

    # Paths for the saved dictionaries
    LABEL_DEFS_PATH = "utils/label_defs.json"
    LABEL_REFS_PATH = "utils/label_refs.json"
    OUTPUT_DIR = "utils/mod"

    # List of API includes to add at the top of each output file
    api_includes_top = [
        "mos_api.inc",
        "macros.inc",
        "equs_top.inc",
    ]

    api_includes_bottom = [
        "ram.asm",
        "user.asm",
        "equs_bottom.inc"
    ]

    api_includes_combined = api_includes_top + api_includes_bottom

    if False:
        # Load label definitions and references
        label_defs = load_json(LABEL_DEFS_PATH)
        label_refs = load_json(LABEL_REFS_PATH)

        # Ensure output directory exists
        create_output_dir(OUTPUT_DIR)

        # Process each file to generate combined files
        process_files(source_files, label_defs, label_refs, api_includes_top, api_includes_bottom, api_includes_combined, OUTPUT_DIR)

        print("All combined files generated.")

    if True:
        # Call to assemble the output file
        for file_name in source_files:
            base_name = os.path.basename(file_name)
            asm_path = os.path.join(OUTPUT_DIR, base_name)
            bin_path = os.path.join("..", "bin", os.path.splitext(base_name)[0] + ".bin")

            # Run the assembler command in the utils/mod directory
            subprocess.run(f"(cd {OUTPUT_DIR} && ez80asm -l {base_name} {bin_path})", shell=True, check=True)

    # Call to disassemble the output binary file and adjust addresses
    for file_name in source_files:
        base_name = os.path.basename(file_name)
        bin_path = os.path.join("utils", "bin", os.path.splitext(base_name)[0] + ".bin")
        adjusted_disasm_path = os.path.join(OUTPUT_DIR, os.path.splitext(base_name)[0] + ".dis.asm")

        # Create a temporary file for the unadjusted disassembly output
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_disasm_file:
            temp_disasm_path = temp_disasm_file.name

        try:
            # Run the disassembler command and write output to the temporary file
            subprocess.run(f"zdis --start 0x040000 --lowercase --explicit-dest --ez80 --hex {bin_path} > {temp_disasm_path}", shell=True, check=True)
            
            # Call adjust_addresses to add padding and correct addresses in the disassembly output
            adjust_addresses(temp_disasm_path, adjusted_disasm_path, 0x040000)
            
            print(f"Disassembly with adjusted addresses written to {adjusted_disasm_path}")
        finally:
            # Remove the temporary file
            os.remove(temp_disasm_path)
