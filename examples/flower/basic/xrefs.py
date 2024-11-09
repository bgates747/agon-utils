import re

# File paths
input_file = "basic/main.asm"
output_file = "basic/xrefs.asm"

# Regular expression pattern to match lines of the format: "; XREF\t<name>"
xref_pattern = re.compile(r"^\s*;\s*XREF\t(\w+)")

# Placeholder for the output assembly template
assembly_template = """{label}:
	call printInline
	asciz "{file_name} called {label}!"
	ret
"""

def generate_xref_assembly(input_file, output_file):
    # Extract file name without path
    file_name = input_file.split('/')[-1]
    
    # Read the input file and extract matching XREF lines
    with open(input_file, 'r') as infile:
        xref_lines = [match.group(1) for line in infile for match in [xref_pattern.search(line)] if match]
    
    # Generate assembly code for each XREF
    with open(output_file, 'w') as outfile:
        for i, label in enumerate(xref_lines):
            assembly_code = assembly_template.format(label=label, file_name=file_name).replace("\r\n\"", "\"")
            outfile.write(assembly_code)
            if i < len(xref_lines) - 1:
                outfile.write("\n")

if __name__ == "__main__":
    generate_xref_assembly(input_file, output_file)
    print(f"Generated assembly code written to {output_file}")
