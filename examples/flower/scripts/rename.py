import re
import os

# File paths
input_file = "fpp.asm"
output_file = "fpp.asm"  # Write changes back to the original file

# Input multiline text with the list of labels following DW24
dw24_label_list = """
				DW24  ABSV            ;ABS
        		DW24  ACS             ;ACS
        		DW24  ASN             ;ASN
        		DW24  ATN             ;ATN
        		DW24  COS             ;COS
        		DW24  DEG             ;DEG
        		DW24  EXP             ;EXP
        		DW24  INT_            ;INT
        		DW24  LN              ;LN
        		DW24  LOG             ;LOG
        		DW24  NOTK            ;NOT
        		DW24  RAD             ;RAD
        		DW24  SGN             ;SGN
        		DW24  SIN             ;SIN
        		DW24  SQR             ;SQR
        		DW24  TAN             ;TAN
		        DW24  ZERO            ;ZERO
        		DW24  FONE            ;FONE
        		DW24  TRUE            ;TRUE
        		DW24  PI              ;PI
		        DW24  VAL             ;VAL
        		DW24  STR             ;STR$
        		DW24  SFIX            ;FIX
        		DW24  SFLOAT          ;FLOAT
		        DW24  FTEST           ;TEST
        		DW24  FCOMP           ;COMPARE
"""

# Regular expression to extract labels from the DW24 list
label_pattern = re.compile(r'^\s*DW24\s+(\w+)\b', re.MULTILINE)
label_usage_pattern = r'\b{}\b'  # Pattern for whole-word replacements
local_definition_pattern = re.compile(r'^(\w+):')  # Pattern for local label definitions

def extract_labels_from_text(text):
    """Extract labels from a provided multiline text."""
    return {match.group(1) for match in label_pattern.finditer(text)}

def extract_local_definitions(file_path):
    """Extracts locally defined labels within the specified file."""
    local_labels = set()
    with open(file_path, 'r') as file:
        for line in file:
            # Ignore comments
            if line.strip().startswith(';'):
                continue
            # Look for labels defined at the beginning of a line
            match = local_definition_pattern.match(line)
            if match:
                local_labels.add(match.group(1))
    return local_labels

def replace_labels_with_suffix(file_path, labels, local_definitions):
    """Replace each occurrence of specified labels with '_FP' suffix in the file,
       excluding text after comment markers and without altering other line content,
       only if the label is defined locally within the file."""
    
    # Read the file content
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Process each line, replacing specified labels only in non-commented portions
    with open(file_path, 'w') as file:
        for line in lines:
            # Split line by the first comment marker, if any
            if ';' in line:
                code, comment = line.split(';', 1)
                updated_code = code  # Start with the original code portion
            else:
                code, comment = line, ''
                updated_code = code
            
            # Replace each label with the modified version in the non-comment portion only
            for label in labels:
                if label in local_definitions:  # Only modify if label is locally defined
                    updated_code = re.sub(label_usage_pattern.format(label), f"{label}_FP", updated_code)

            # Write the line with any modifications back to the original file
            file.write(f"{updated_code}{';' + comment if comment else ''}")

    print(f"Replacements completed. Modifications saved in {file_path}")

if __name__ == "__main__":
    # Extract labels from the provided DW24 list
    dw24_labels = extract_labels_from_text(dw24_label_list)
    
    # Extract local definitions within the file
    local_definitions = extract_local_definitions(input_file)

    # Perform replacements directly in the original file for labels that are locally defined
    replace_labels_with_suffix(input_file, dw24_labels, local_definitions)
