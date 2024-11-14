import re
import os
import json

# Regular expression pattern to match symbols at the start of a line with a trailing colon
label_pattern = re.compile(r"^(\w+):")  # Match only symbols at the start of a line with a trailing colon

def load_files_to_dict(file_list):
    """Load the content of each file into a dictionary."""
    files_dict = {}
    for filename in file_list:
        with open(filename, 'r') as file:
            files_dict[filename] = file.readlines()
    return files_dict

def extract_label_definitions(files_dict):
    """Extract symbol definitions from all files and structure by symbol name."""
    label_dict = {}
    for filename, lines in files_dict.items():
        file_name = os.path.basename(filename)

        for line_num, line in enumerate(lines):
            # Check for label definitions that start with a symbol and end with a colon
            label_match = label_pattern.match(line)
            if label_match:
                symbol = label_match.group(1)
                
                # Store label definition information as the entire line content
                if symbol not in label_dict:
                    label_dict[symbol] = []
                label_dict[symbol].append({
                    "def_file": file_name,
                    "def_line": line_num + 1,
                    "def_content": line.strip()
                })

    # Sort the label dictionary by symbol name, then by def_file
    for symbol in label_dict:
        label_dict[symbol] = sorted(label_dict[symbol], key=lambda x: x['def_file'])
    label_dict = dict(sorted(label_dict.items()))
    return label_dict

def extract_label_references(files_dict, label_dict):
    """Extract references to each symbol across all files."""
    references_dict = {}
    for symbol, definitions in label_dict.items():
        references_dict[symbol] = []

        # Scan all files for references to the symbol
        for filename, lines in files_dict.items():
            file_name = os.path.basename(filename)
            for line_num, line in enumerate(lines):
                # Ignore commented portions of the line
                line_content = line.split(';')[0]
                # Ensure exact match of the symbol in the line, excluding its own definition line
                if symbol in line_content.split() and not is_definition_line(symbol, file_name, line_num + 1, definitions):
                    references_dict[symbol].append({
                        "ref_file": file_name,
                        "ref_line": line_num + 1,
                        "ref_content": line.strip()
                    })

    # Sort references dictionary by symbol and then by ref_file
    for symbol in references_dict:
        references_dict[symbol] = sorted(references_dict[symbol], key=lambda x: x['ref_file'])
    references_dict = dict(sorted(references_dict.items()))
    return references_dict

def is_definition_line(symbol, file_name, line_num, definitions):
    """Check if a given line is the definition line for a symbol."""
    for definition in definitions:
        if definition["def_file"] == file_name and definition["def_line"] == line_num:
            return True
    return False

def save_dict_to_file(dictionary, path):
    """Save a dictionary to a file in JSON format."""
    with open(path, 'w') as f:
        json.dump(dictionary, f, indent=4)

if __name__ == "__main__":
    # List of files to scan for symbol definitions and references
    source_files = [
        "mos_api.inc",
        "macros.inc",
        "ram.asm",
        "equs_top.inc",

        "agon_graphics.asm",
        "agon_sound.asm",
        "basic.asm",
        "eval.asm",
        "exec.asm",
        "fpp.asm",
        "gpio.asm",
        "init.asm",
        "interrupts.asm",
        "main.asm",
        "misc.asm",
        "patch.asm",
        "sorry.asm",
        "user.asm",
        "equs_bottom.inc",
    ]

    # Paths for the saved dictionaries
    LABEL_DEFS_PATH = "utils/label_defs.json"
    LABEL_REFS_PATH = "utils/label_refs.json"

    # Load files and extract symbol definitions
    files_dict = load_files_to_dict(source_files)
    label_dict = extract_label_definitions(files_dict)
    references_dict = extract_label_references(files_dict, label_dict)

    # Save both dictionaries to files
    save_dict_to_file(label_dict, LABEL_DEFS_PATH)
    save_dict_to_file(references_dict, LABEL_REFS_PATH)

    print(f"Symbol definitions saved to {LABEL_DEFS_PATH}")
    print(f"Symbol references saved to {LABEL_REFS_PATH}")
