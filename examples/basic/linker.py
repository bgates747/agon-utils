import re
import os

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


def extract_labels(files_dict):
    """Extracts labels from the files and returns a dictionary of label definitions.

    Args:
        files_dict (dict): A dictionary with filenames as keys and lists of lines as values.

    Returns:
        dict: A dictionary where keys are labels and values are lists of dictionaries with 'file' and 'line'.
    """
    labels = {}
    for filename, lines in files_dict.items():
        for line_num, line in enumerate(lines, start=1):
            # Skip EQU definitions and fully commented lines
            if re.match(r'^\w+:\s*EQU\b', line, re.IGNORECASE) or line.strip().startswith(';'):
                continue

            # Exclude any comments from consideration
            code_part = line.split(';', 1)[0]

            # Match labels ending with a colon (e.g., LABEL:) only in the code part
            label_match = re.match(r'^(\w+):', code_part)
            if label_match:
                label = label_match.group(1)
                if label not in labels:
                    labels[label] = []
                labels[label].append({'file': filename, 'line': line_num})
    return labels



def extract_equ_definitions(files_dict):
    """Extracts EQU definitions and returns a dictionary of EQU labels.

    Args:
        files_dict (dict): A dictionary with filenames as keys and lists of lines as values.

    Returns:
        dict: A dictionary where keys are EQU labels and values are lists of dictionaries,
              each with 'file' and 'definition' for each instance.
    """
    equs = {}
    for filename, lines in files_dict.items():
        for line in lines:
            # Skip fully commented lines
            if line.strip().startswith(';'):
                continue

            # Exclude comments from the line
            code_part = line.split(';', 1)[0]

            # Match EQU definitions, ignoring case, only in the code part
            equ_match = re.match(r'^(\w+):\s*EQU\b', code_part, re.IGNORECASE)
            if equ_match:
                label = equ_match.group(1)
                if label not in equs:
                    equs[label] = []
                equs[label].append({'file': filename, 'definition': line.strip()})
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
            # Skip commented lines
            if line.strip().startswith(';'):
                continue

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


def write_equ_labels_to_file(equs, labels, output_file):
    """Writes EQU definitions and labels to a file in a combined, sorted list.
    
    Args:
        equs (dict): A dictionary of EQU definitions.
        labels (dict): A dictionary of label definitions.
        output_file (str): The file path where the list should be written.
    """
    # Combine EQU and label dictionaries into a single list for sorting
    combined_entries = []

    for equ, instances in equs.items():
        for info in instances:
            combined_entries.append({
                'name': equ,
                'type': 'EQU',
                'file': info['file'],
                'details': info['definition']
            })

    for label, instances in labels.items():
        for info in instances:
            combined_entries.append({
                'name': label,
                'type': 'label',
                'file': info['file'],
                'details': f"Line {info['line']}"
            })

    # Sort entries by name
    combined_entries.sort(key=lambda x: x['name'])

    # Write to file
    with open(output_file, 'w') as file:
        file.write("Combined EQU and Label Definitions:\n")
        for entry in combined_entries:
            if entry['type'] == 'EQU':
                file.write(f"{entry['name']} (EQU) in {entry['file']}: {entry['details']}\n")
            elif entry['type'] == 'label':
                file.write(f"{entry['name']} (label) in {entry['file']}: {entry['details']}\n")
    print(f"EQUs and labels written to {output_file}")


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
    for label, instances in labels.items():
        for info in instances:
            combined.setdefault(label, []).append({
                'type': 'label',
                'file': info['file'],
                'line': info['line']
            })

    # Add EQU definitions to combined dictionary
    for equ, instances in equs.items():
        for info in instances:
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
    """Writes the namespace collisions to a file, sorted by label and filename.
    
    Args:
        collisions (dict): A dictionary of namespace collisions.
        output_file (str): The file path where collisions should be written.
    """
    # Sort collisions by label name
    sorted_collisions = sorted(collisions.items(), key=lambda item: item[0])

    with open(output_file, 'w') as file:
        file.write("Namespace Collisions:\n")
        for label, occurrences in sorted_collisions:
            file.write(f"\nCollision for '{label}':\n")
            # Sort occurrences by filename
            sorted_occurrences = sorted(occurrences, key=lambda x: x['file'])
            for occurrence in sorted_occurrences:
                if occurrence['type'] == 'label':
                    file.write(f"  Defined as label in {occurrence['file']} at line {occurrence['line']}\n")
                elif occurrence['type'] == 'equ':
                    file.write(f"  Defined as EQU in {occurrence['file']}: {occurrence['definition']}\n")
    print(f"Collisions written to {output_file}")

def make_unique_label(label, filename):
    """Generate a unique label name by appending an underscore and the base filename."""
    base_name = os.path.splitext(filename)[0]
    return f"{label}_{base_name}"

def replace_duplicate_labels(files_dict, collisions, xdefs, xrefs):
    """Rename duplicate labels in each file to make them unique, respecting XDEF and XREF declarations.
    
    Args:
        files_dict (dict): The original dictionary of files with code lines.
        collisions (dict): A dictionary of collisions, where each key is a duplicate label 
                           and the value is a list of occurrences (file, type).
        xdefs (dict): Dictionary where keys are XDEF labels and values are filenames.
        xrefs (dict): Dictionary where keys are XREF labels and values are filenames.
    
    Returns:
        dict: A new dictionary with modified lines to reflect unique label names.
    """
    modified_files_dict = {filename: lines[:] for filename, lines in files_dict.items()}  # Deep copy of files_dict

    for label, occurrences in collisions.items():
        # Track which files to leave unchanged
        global_files = set()
        
        # Identify files that should not change the label (those with XDEF or XREF)
        if label in xdefs:
            global_files.add(xdefs[label])  # File defining the label as global
        if label in xrefs:
            global_files.update(xrefs[label])  # Files referencing the label externally

        # For each file in occurrences, decide whether to replace or keep the label
        label_replacements = {}
        for occurrence in occurrences:
            file = occurrence['file']
            if file not in global_files:
                # Generate a unique version for the file to avoid collisions
                label_replacements[file] = make_unique_label(label, file)

        # Perform replacement in each affected file
        for filename, unique_label in label_replacements.items():
            new_lines = []
            for line in modified_files_dict[filename]:
                # Ignore lines fully commented out
                if line.strip().startswith(';'):
                    new_lines.append(line)
                    continue

                # Match whole words only, skipping occurrences in comments
                def replace_match(match):
                    start, end = match.span()
                    preceding_text = line[:start].rstrip()
                    if preceding_text.endswith(';'):
                        # Ignore if this is in a comment
                        return match.group(0)
                    return unique_label

                # Replace label with unique version in the current line
                updated_line = re.sub(rf'\b{label}\b', replace_match, line)
                new_lines.append(updated_line)
            
            # Update the modified dictionary with new lines
            modified_files_dict[filename] = new_lines

    return modified_files_dict

def write_master_assembly(modified_files_dict, output_file):
    """Writes the modified code from each file into a single master assembly file,
    preserving file and line order, adding a header for each file, and commenting out XDEF/XREF lines.
    
    Args:
        modified_files_dict (dict): The dictionary with modified lines of code.
        output_file (str): The path to the master output file.
    """
    with open(output_file, 'w') as file:
        for filename, lines in modified_files_dict.items():
            # Write a header for each file
            file.write(f"; ========================================\n")
            file.write(f"; FROM {filename}\n")
            file.write(f"; ----------------------------------------\n\n")

            # Write each line from the file, commenting out any XDEF or XREF lines
            for line in lines:
                if line.strip().startswith(('XDEF', 'XREF')):
                    # Comment out XDEF and XREF lines
                    file.write(f"; {line}")
                else:
                    file.write(line)
            file.write("\n")  # Separate files with an extra newline for readability

    print(f"Master assembly file written to {output_file}")


file_list = [
    "mos_api.inc",
    "macros.inc",
    "ram.asm",
    "equs.inc",
    "init.asm",
    "agon_graphics.asm",
    "agon_sound.asm",
    "eval.asm",
    "exec.asm",
    "fpp.asm",
    # "gpio.asm",
    "interrupts.asm",
    "misc.asm",
    "patch.asm",
    "sorry.asm",
    "main.asm"
]

if __name__ == "__main__":
    # Define the directory and list of include files
    directory = "examples/basic"

    # Load files into a dictionary
    files_dict = load_files_to_dict(directory, file_list)
    
    # Extract XDEFs and XREFs
    xdefs, xrefs = extract_xdefs_xrefs(files_dict)

    # Extract labels and EQU definitions
    labels = extract_labels(files_dict)
    equs = extract_equ_definitions(files_dict)

    # Extract macros (though they are not part of the collision check)
    macros = extract_macros(files_dict)

    # Write EQU definitions and labels to a file
    output_file = f"{directory}/symbols.txt"
    write_equ_labels_to_file(equs, labels, output_file)

    # Find global namespace collisions between labels and EQU definitions
    collisions = find_namespace_collisions(labels, equs)

    # Write the collisions to a file
    collisions_output_file = f"{directory}/namespace_collisions.txt"
    write_collisions_to_file(collisions, collisions_output_file)

    # Debug print statements for verification
    print(f"EQUs and labels written to {output_file}")
    print(f"Collisions written to {collisions_output_file}")

    # Create modified files with unique labels, respecting XDEF and XREF declarations
    modified_files_dict = replace_duplicate_labels(files_dict, collisions, xdefs, xrefs)

    # Write the final master assembly file, commenting out XDEF and XREF lines
    master_output_file = f"{directory}/master_assembly.asm"
    write_master_assembly(modified_files_dict, master_output_file)
