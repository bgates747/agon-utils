import os
import json

# Load JSON data from a file
def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

# Ensure output directory exists
def create_output_dir(directory):
    os.makedirs(directory, exist_ok=True)

# Write symbols and include directives to the output file in the specified order
def write_combined_file(filename, symbols, api_includes, output_dir):
    output_path = os.path.join(output_dir, filename)
    with open(output_path, 'w') as f:
        # Write API includes at the top
        for api_include in api_includes:
            f.write(f'    include "../src/{api_include}"\n')
        f.write("\n")
        
        # Split symbols into regular symbols and those defined in user.asm
        regular_symbols = [s for s in symbols if s["def_file"] != "user.asm"]
        user_symbols = [s for s in symbols if s["def_file"] == "user.asm"]
        
        # Write each non-user.asm symbol definition with a source file comment
        for symbol in regular_symbols:
            f.write(f"; Defined in {symbol['def_file']}\n")
            f.write(f"{symbol['def_content']}\n")
        f.write("\n")
        
        # Include directive to the original file
        include_line = f'    include "../src/{filename}"\n'
        f.write(include_line)
        
        # Write user.asm symbols after the include line
        if user_symbols:
            f.write("\n")
            for symbol in user_symbols:
                f.write(f"; Defined in {symbol['def_file']}\n")
                f.write(f"{symbol['def_content']}\n")
                
    print(f"Written combined file to {output_path}")

# Process each source file to create combined files with references and includes
def process_files(source_files, label_defs, label_refs, api_includes, output_dir):
    api_files = set(os.path.basename(path) for path in api_includes)  # Base names of API include files

    for file_name in source_files:
        base_name = os.path.basename(file_name)

        # Collect needed symbol definitions for this file, excluding self-defined and API-defined symbols
        symbols_to_include = []
        for symbol_name, references in label_refs.items():
            # Check if this file references the symbol and if it's not self-defined or defined in an API include
            if any(ref["ref_file"] == base_name for ref in references):
                # Only include symbols defined in other files, excluding those from API includes
                if symbol_name in label_defs:
                    symbols_to_include.extend([
                        definition for definition in label_defs[symbol_name]
                        if definition["def_file"] != base_name and definition["def_file"] not in api_files
                    ])

        # Write the combined file with API includes, external symbol definitions, and the original source include
        write_combined_file(base_name, symbols_to_include, api_includes, output_dir)

if __name__ == "__main__":
    # List of files to scan for symbol definitions and references
    source_files = [
        "utils/src/agon_graphics.asm",
        # "utils/src/agon_sound.asm",
        # "utils/src/basic.asm",
        # "utils/src/equs.inc",
        # "utils/src/eval.asm",
        # "utils/src/exec.asm",
        # "utils/src/fpp.asm",
        # "utils/src/gpio.asm",
        # "utils/src/init.asm",
        # "utils/src/interrupts.asm",
        # "utils/src/macros.inc",
        # "utils/src/main.asm",
        # "utils/src/misc.asm",
        # "utils/src/mos_api.inc",
        # "utils/src/patch.asm",
        # "utils/src/ram.asm",
        # "utils/src/sorry.asm",
        # "utils/src/user.asm",
    ]

    # Paths for the saved dictionaries
    LABEL_DEFS_PATH = "utils/label_defs.json"
    LABEL_REFS_PATH = "utils/label_refs.json"
    OUTPUT_DIR = "utils/mod"

    # List of API includes to add at the top of each output file
    api_includes = [
        "mos_api.inc",
        "macros.inc",
        # "init.asm",
        "ram.asm",
        "equs.inc",
    ]

    # Load label definitions and references
    label_defs = load_json(LABEL_DEFS_PATH)
    label_refs = load_json(LABEL_REFS_PATH)

    # Ensure output directory exists
    create_output_dir(OUTPUT_DIR)

    # Process each file to generate combined files
    process_files(source_files, label_defs, label_refs, api_includes, OUTPUT_DIR)

    print("All combined files generated.")
