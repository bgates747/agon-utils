import re
import os
import json
import time

# Regular expression patterns
label_pattern = re.compile(r"^\s*(\w+):")  # Match any label ending with a colon
equ_pattern = re.compile(r"^\s*(\w+):\s+EQU\s+(.+)", re.IGNORECASE)  # Match EQU statements with case-insensitive 'EQU'
xref_pattern = re.compile(r"\b(\w+)\b")  # Match label references within lines of code

# Paths for the saved dictionaries
LABEL_DEFS_PATH = "label_defs.json"
LABEL_REFS_PATH = "label_refs.json"


def load_files_to_dict(file_list):
    """Load the content of each file into a dictionary."""
    files_dict = {}
    for filename in file_list:
        with open(filename, 'r') as file:
            files_dict[filename] = file.readlines()
    return files_dict


def extract_labels(files_dict):
    """Extract label definitions from all files and save them in a dictionary."""
    label_dict = {}
    for filename, lines in files_dict.items():
        file_name = os.path.basename(filename)
        line_num = 0
        while line_num < len(lines):
            line = lines[line_num]

            # Check for EQU labels
            equ_match = equ_pattern.match(line)
            if equ_match:
                label = equ_match.group(1)
                value = equ_match.group(2).strip()
                resolved_value = resolve_label_reference(value, label_dict)  # Resolve recursively if needed
                label_dict[label] = f"{line.strip()} ; defined in {file_name}"
            else:
                # Check if it is an address label
                label_match = label_pattern.match(line)
                if label_match:
                    label = label_match.group(1)
                    full_line = line.strip()
                    while not is_code_line(full_line) and line_num + 1 < len(lines):
                        line_num += 1
                        full_line = lines[line_num].strip()
                    label_dict[label] = f"{full_line} ; defined in {file_name}"

            line_num += 1
    return label_dict


def extract_references(files_dict):
    """Extract references to labels from all files and save them in a dictionary."""
    references_dict = {}
    for filename, lines in files_dict.items():
        file_name = os.path.basename(filename)
        for line_num, line in enumerate(lines):
            line_content = line.split(';')[0]  # Ignore comments
            for match in xref_pattern.finditer(line_content):
                label = match.group(1)
                if label not in references_dict:
                    references_dict[label] = []
                references_dict[label].append({"file": file_name, "line": line_num + 1, "content": line.strip()})
    return references_dict


def resolve_label_reference(value, label_dict):
    """Recursively resolve label references within EQU definitions."""
    while value in label_dict:
        match = equ_pattern.match(label_dict[value])
        if match:
            value = match.group(2).strip()
        else:
            break
    return value


def is_code_line(line):
    """Determine if a line contains actual code (not just whitespace or comments)."""
    stripped_line = line.strip()
    return bool(stripped_line and not stripped_line.startswith(';'))


def save_dict_to_file(dictionary, path):
    """Save a dictionary to a file in JSON format."""
    with open(path, 'w') as f:
        json.dump(dictionary, f, indent=4)


def load_dict_from_file(path):
    """Load a dictionary from a JSON file."""
    with open(path, 'r') as f:
        return json.load(f)


def generate_label_and_reference_dictionaries(source_files, include_files):
    """Generate label definitions and references dictionaries and save them for reuse."""
    files_dict = load_files_to_dict(include_files)
    label_dict = extract_labels(files_dict)
    references_dict = extract_references(files_dict)

    # Save both dictionaries to files
    save_dict_to_file(label_dict, LABEL_DEFS_PATH)
    save_dict_to_file(references_dict, LABEL_REFS_PATH)

    return label_dict, references_dict


def load_or_generate_dictionaries(source_files, include_files):
    """Load existing dictionaries or generate new ones if necessary."""
    if os.path.exists(LABEL_DEFS_PATH) and os.path.exists(LABEL_REFS_PATH):
        label_dict = load_dict_from_file(LABEL_DEFS_PATH)
        references_dict = load_dict_from_file(LABEL_REFS_PATH)
    else:
        label_dict, references_dict = generate_label_and_reference_dictionaries(source_files, include_files)
    return label_dict, references_dict


def process_files(source_files, label_dict, references_dict):
    """Process each source file, resolving any missing label definitions."""
    for input_file in source_files:
        print(f"Processing {input_file}...")

        with open(input_file, 'r') as infile:
            original_lines = infile.readlines()

        # Remove previously added labels and extract label references
        original_lines = remove_previous_additions(original_lines)
        references = extract_references({"dummy": original_lines})  # Single file references

        missing_labels = {
            label: label_dict[label]
            for label in references
            if label not in label_dict and label in references_dict
        }

        # Generate code for missing labels
        added_assembly_code = generate_assembly_code(missing_labels)

        # Write updated content with added labels at the beginning
        with open(input_file, 'w') as outfile:
            outfile.writelines(added_assembly_code + original_lines)

        print(f"Updated {input_file} with missing label definitions.")


def remove_previous_additions(lines):
    """Remove previously added labels from the file."""
    inside_added_section = False
    filtered_lines = []
    for line in lines:
        if line.startswith("; ===== BEGIN ADDED LABELS ====="):
            inside_added_section = True
        elif line.startswith("; ===== END ADDED LABELS ====="):
            inside_added_section = False
            continue
        if not inside_added_section:
            filtered_lines.append(line)
    return filtered_lines


def generate_assembly_code(labels):
    """Generate assembly code for each missing label."""
    assembly_code = ["; ===== BEGIN ADDED LABELS =====\n"]
    for label, full_line in labels.items():
        assembly_code.append(full_line + "\n")
    assembly_code.append("; ===== END ADDED LABELS =====\n")
    return assembly_code


if __name__ == "__main__":
    # List of source files to process
    source_files = [
        "utils/src/agon_graphics.asm",
        # More source files
    ]

    # List of include files to scan for label definitions
    include_files = [
        "utils/src/agon_graphics.asm",
        "utils/src/agon_sound.asm",
        # More include files
    ]

    # Load or generate dictionaries
    label_dict, references_dict = load_or_generate_dictionaries(source_files, include_files)

    # Process each source file to add missing label definitions
    process_files(source_files, label_dict, references_dict)
    print("Processing complete.")
