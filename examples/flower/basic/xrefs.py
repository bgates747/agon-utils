import re
import os

# Regular expression patterns to match XREF, XDEF, and local label lines
xref_pattern = re.compile(r"^\s*;\s*XREF\t(\w+)")
xdef_pattern = re.compile(r"^\s*;\s*XDEF\s+(\w+)")
label_pattern = re.compile(r"^\s*(\w+):")  # Match local labels ending with a colon

# Placeholder for the output assembly template
assembly_template = """{label}:
	call printInline
	asciz "{file_name} called {label}!"
	ret
"""

def load_files_to_dict(file_list):
    """Load the content of each file into a dictionary."""
    files_dict = {}
    for filename in file_list:
        with open(filename, 'r') as file:
            files_dict[filename] = file.readlines()
    return files_dict

def label_exists_in_includes(label, includes_dict):
    """Check if a label exists in any of the include files."""
    label_pattern = re.compile(rf'^\s*{label}:\s')
    for lines in includes_dict.values():
        if any(label_pattern.match(line) for line in lines):
            return True
    return False

def extract_xdefs(input_file):
    """Extract XDEF labels from the input file."""
    xdef_labels = set()
    with open(input_file, 'r') as infile:
        for line in infile:
            match = xdef_pattern.search(line)
            if match:
                xdef_labels.add(match.group(1))
    return xdef_labels

def extract_local_labels(input_file):
    """Extract locally defined labels from the input file itself."""
    local_labels = set()
    with open(input_file, 'r') as infile:
        for line in infile:
            match = label_pattern.match(line)
            if match:
                local_labels.add(match.group(1))
    return local_labels

def generate_xref_assembly(input_file, output_file, include_files):
    # Extract file name without path
    file_name = os.path.basename(input_file)
    
    # Load include files into a dictionary
    includes_dict = load_files_to_dict(include_files)
    
    # Extract XDEF and local labels from the input file
    xdef_labels = extract_xdefs(input_file)
    local_labels = extract_local_labels(input_file)
    
    # Read the input file and extract matching XREF lines
    with open(input_file, 'r') as infile:
        xref_lines = [match.group(1) for line in infile for match in [xref_pattern.search(line)] if match]
    
    # Sort the XREF labels alphabetically
    xref_lines = sorted(xref_lines)
    
    # Generate assembly code for each XREF not found in XDEFs, local labels, or include files
    with open(output_file, 'w') as outfile:
        outfile.write("; ===== STUB FUNCTIONS =====\r\n")
        outfile.write("printInline:\r\n")
        outfile.write("    ret\r\n\r\n")
	
        for i, label in enumerate(xref_lines):
            if (label not in xdef_labels and label not in local_labels and 
                not label_exists_in_includes(label, includes_dict)):
                
                assembly_code = assembly_template.format(label=label, file_name=file_name).replace("\r\n\"", "\"")
                outfile.write(assembly_code)
                if i < len(xref_lines) - 1:
                    outfile.write("\n")

if __name__ == "__main__":
    # File paths
    input_file = "basic/interrupts.asm"
    output_file = "basic/xrefs.asm"

    # List of include files to check for existing labels
    include_files = [
        "basic/mos_api.inc",
        "basic/macros.inc",
        "basic/equs.inc",
        "basic/ram.asm",
    ]
    
    generate_xref_assembly(input_file, output_file, include_files)
    print(f"Generated assembly code written to {output_file}")
