import re
import os

def extract_labels(files_dict):
    """Extracts labels from the files and returns a dictionary of label definitions.

    Args:
        files_dict (dict): A dictionary with filenames as keys and lists of lines as values.

    Returns:
        dict: A dictionary where keys are labels and values are dictionaries with 'file' and 'line' (line number).
    """
    labels = {}
    for filename, lines in files_dict.items():
        for line_num, line in enumerate(lines, start=1):
            # Match labels ending with a colon (e.g., LABEL:)
            label_match = re.match(r'^(\w+):', line)
            if label_match:
                label = label_match.group(1)
                labels[label] = {'file': filename, 'line': line_num}
    return labels

def extract_equ_definitions(files_dict):
    """Extracts EQU definitions and returns a dictionary of EQU labels.

    Args:
        files_dict (dict): A dictionary with filenames as keys and lists of lines as values.

    Returns:
        dict: A dictionary where keys are EQU labels and values are dictionaries with 'file' and 'definition' (full line).
    """
    equs = {}
    for filename, lines in files_dict.items():
        for line in lines:
            # Match EQU definitions, ignoring case
            equ_match = re.match(r'^(\w+):\s*EQU\b', line, re.IGNORECASE)
            if equ_match:
                label = equ_match.group(1)
                equs[label] = {'file': filename, 'definition': line.strip()}
    return equs

def extract_macros(files_dict):
    """Extracts macros and returns a dictionary of macro definitions.

    Args:
        files_dict (dict): A dictionary with filenames as keys and lists of lines as values.

    Returns:
        dict: A dictionary where keys are macro names and values are dictionaries with 'file' and 'lines' (macro lines).
    """
    macros = {}
    for filename, lines in files_dict.items():
        macro_def = None
        for line in lines:
            # Start of a macro definition
            macro_start = re.match(r'^\s*MACRO\s+(\w+)', line, re.IGNORECASE)
            if macro_start:
                macro_name = macro_start.group(1)
                macro_def = {
                    'file': filename,
                    'lines': [line.strip()]
                }
                continue

            # Capture macro content
            if macro_def:
                macro_def['lines'].append(line.strip())
                if re.match(r'^\s*ENDMACRO', line, re.IGNORECASE):
                    macros[macro_name] = macro_def
                    macro_def = None  # Reset for next macro
                continue
    return macros

def load_files_to_dict(directory, file_list):
    """Load the content of each file into a dictionary.
    
    Args:
        directory (str): The directory containing the files.
        file_list (list): List of filenames to read.
        
    Returns:
        dict: A dictionary with filenames as keys and lists of lines as values.
    """
    files_dict = {}
    for filename in file_list:
        filepath = os.path.join(directory, filename)
        with open(filepath, 'r') as file:
            files_dict[filename] = file.readlines()
    return files_dict

def extract_xdefs_xrefs(files_dict):
    """Extract XDEF and XREF labels from a dictionary of file contents.
    
    Args:
        files_dict (dict): A dictionary with filenames as keys and lists of lines as values.
        
    Returns:
        tuple: Two dictionaries, one for XDEFs and one for XREFs, each with label names as keys and filenames as values.
    """
    xdefs = {}
    xrefs = {}

    for filename, lines in files_dict.items():
        for line in lines:
            # Match XDEF and XREF lines
            xdef_match = re.match(r'^\s*XDEF\s+(\w+)', line, re.IGNORECASE)
            xref_match = re.match(r'^\s*XREF\s+(\w+)', line, re.IGNORECASE)

            if xdef_match:
                label = xdef_match.group(1)
                xdefs[label] = filename  # Store label with its source file

            if xref_match:
                label = xref_match.group(1)
                xrefs[label] = filename  # Store label with its source file

    return xdefs, xrefs

def find_namespace_collisions(labels, equs):
    """Finds global namespace collisions between labels and EQU definitions.
    
    Args:
        labels (dict): A dictionary of label definitions with label names as keys.
        equs (dict): A dictionary of EQU definitions with EQU names as keys.
        
    Returns:
        dict: A dictionary of collisions, where each key is a duplicate label and
              the value is a list of dictionaries containing 'type', 'file', and 'line' or 'definition'.
    """
    combined = {}
    collisions = {}

    # Add labels to combined dictionary
    for label, info in labels.items():
        combined.setdefault(label, []).append({
            'type': 'label',
            'file': info['file'],
            'line': info['line']
        })

    # Add EQU definitions to combined dictionary
    for equ, info in equs.items():
        combined.setdefault(equ, []).append({
            'type': 'equ',
            'file': info['file'],
            'definition': info['definition']
        })

    # Identify collisions
    for label, entries in combined.items():
        if len(entries) > 1:  # More than one entry for the same label indicates a collision
            collisions[label] = entries

    return collisions

def write_collisions_to_file(collisions, output_file):
    """Writes the namespace collisions to a file.
    
    Args:
        collisions (dict): A dictionary of namespace collisions.
        output_file (str): The file path where collisions should be written.
    """
    with open(output_file, 'w') as file:
        file.write("Namespace Collisions:\n")
        for label, occurrences in collisions.items():
            file.write(f"\nCollision for '{label}':\n")
            for occurrence in occurrences:
                if occurrence['type'] == 'label':
                    file.write(f"  Defined as label in {occurrence['file']} at line {occurrence['line']}\n")
                elif occurrence['type'] == 'equ':
                    file.write(f"  Defined as EQU in {occurrence['file']}: {occurrence['definition']}\n")
    print(f"Collisions written to {output_file}")



if __name__ == "__main__":
    # Define the directory and list of include files
    directory = "examples/basic"
    file_list = [
        "mos_api.inc",
        "macros.inc",
        "ram.asm",
        "equs.inc",
        "init.asm",
        "eval.asm",
        "exec.asm",
        "fpp.asm",
        "gpio.asm",
        "interrupts.asm",
        "patch.asm",
        "sorry.asm"
    ]

    # Load files into a dictionary
    files_dict = load_files_to_dict(directory, file_list)
    
    # Extract XDEFs and XREFs
    xdefs, xrefs = extract_xdefs_xrefs(files_dict)

    # Extract labels
    labels = extract_labels(files_dict)

    # Extract EQU definitions
    equs = extract_equ_definitions(files_dict)

    # Extract macros
    macros = extract_macros(files_dict)

    # Find namespace collisions
    collisions = find_namespace_collisions(labels, equs)

    # Write the collisions to a file
    collisions_output_file = f"{directory}/namespace_collisions.txt"
    write_collisions_to_file(collisions, collisions_output_file)