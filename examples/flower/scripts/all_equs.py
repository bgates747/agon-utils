# import os
# import re

# def extract_equ_lines():
#     output_filename = 'all_equs.inc'
#     current_directory = '.'
#     valid_extensions = ('.inc', '.asm')  # Only process files with these extensions

#     with open(output_filename, 'w') as output_file:
#         # Loop through files in the current directory (non-recursive)
#         for filename in sorted(os.listdir(current_directory)):
#             if os.path.isfile(filename) and filename.lower().endswith(valid_extensions):
#                 equ_lines = []
#                 with open(filename, 'r') as input_file:
#                     lines = input_file.readlines()
#                     for line in lines:
#                         line = line.rstrip('\n')
#                         # Split line at first ';' to separate code and comment
#                         code_part = line.split(';', 1)[0]
#                         code_part = code_part.rstrip()
#                         if not code_part:
#                             continue  # Skip empty lines or lines with only comments
#                         # Check if line starts with a label (no leading whitespace)
#                         if code_part[0].isspace():
#                             continue  # Skip lines where the first character is whitespace
#                         # Match label followed by ':', optional whitespace, then EQU
#                         match = re.match(r'^(\w+):\s*\bEQU\b', code_part, re.IGNORECASE)
#                         if match:
#                             equ_lines.append(line)
#                     if equ_lines:
#                         # Write header with file name
#                         output_file.write(f'; --- Begin {filename} ---\n')
#                         # Write EQU lines in the same order as in the file
#                         for equ_line in equ_lines:
#                             output_file.write(equ_line + '\n')
#                         output_file.write(f'; --- End {filename} ---\n\n')
#         print(f"Extracted EQU lines written to {output_filename}")

# if __name__ == '__main__':
#     extract_equ_lines()

import os
import re
import shutil

def comment_out_equ_lines():
    output_filename = 'all_equs.inc'
    current_directory = '.'
    valid_extensions = ('.inc', '.asm')  # Only process files with these extensions
    equ_pattern = re.compile(r'^(\w+):\s*\bEQU\b', re.IGNORECASE)

    # Loop through files in the current directory (non-recursive)
    for filename in sorted(os.listdir(current_directory)):
        if (os.path.isfile(filename)
                and filename.lower().endswith(valid_extensions)
                and filename != output_filename):
            # Read the original file lines
            with open(filename, 'r') as input_file:
                lines = input_file.readlines()

            modified = False  # Flag to check if the file was modified
            new_lines = []
            for line in lines:
                original_line = line  # Keep the original line for comparison
                stripped_line = line.rstrip('\n')

                # Split line at first ';' to separate code and comment
                code_part = stripped_line.split(';', 1)[0]
                code_part = code_part.rstrip()

                # Check if line is empty or a comment-only line
                if not code_part or code_part.startswith(';'):
                    new_lines.append(line)
                    continue

                # Check if line starts with a label (no leading whitespace)
                if code_part[0].isspace():
                    new_lines.append(line)
                    continue

                # Check if the line matches the EQU pattern
                if equ_pattern.match(code_part):
                    # The line is an EQU line that is not commented out
                    # Comment it out
                    modified = True
                    commented_line = '; ' + line
                    new_lines.append(commented_line)
                else:
                    # Leave the line as is
                    new_lines.append(line)

            if modified:
                # Backup the original file
                backup_filename = filename + '.bak'
                shutil.copyfile(filename, backup_filename)
                print(f"Created backup of {filename} as {backup_filename}")

                # Write the modified lines back to the file
                with open(filename, 'w') as output_file:
                    output_file.writelines(new_lines)
                print(f"Commented out EQU lines in {filename}")
            else:
                print(f"No changes made to {filename}")

    print("Processing complete.")

if __name__ == '__main__':
    comment_out_equ_lines()
