
import os
import re
import shutil
import subprocess
import sys

def copy_to_directory(src_dir, tgt_dir, include_pattern=None, recursive=False, delete_first=False):
    """
    Copies files from src_dir to tgt_dir, optionally filtering by a regex pattern.
    Supports deleting the target directory first and recursive copying.

    :param src_dir: Source directory to copy from
    :param tgt_dir: Target directory to copy to
    :param include_pattern: Optional regex pattern to filter files (default: None)
    :param recursive: Whether to copy files recursively (default: False)
    :param delete_first: Whether to delete the target directory before copying (default: False)
    """
    try:
        # Delete the target directory if specified
        if delete_first and os.path.exists(tgt_dir):
            shutil.rmtree(tgt_dir)

        # Recreate the target directory if it doesn't exist
        os.makedirs(tgt_dir, exist_ok=True)

        # Walk through the source directory
        for root, _, files in os.walk(src_dir):
            # Skip subdirectories if not in recursive mode
            if not recursive and root != src_dir:
                continue

            for file in files:
                # If a pattern is provided, check if the file matches the pattern
                if include_pattern is None or re.match(include_pattern, file, re.IGNORECASE):
                    src_file = os.path.join(root, file)
                    rel_path = os.path.relpath(src_file, src_dir)
                    tgt_file = os.path.join(tgt_dir, rel_path)

                    # Ensure the target directory exists before copying
                    os.makedirs(os.path.dirname(tgt_file), exist_ok=True)
                    shutil.copy2(src_file, tgt_file)

        print(f'Successfully copied files from {src_dir} to {tgt_dir}')

    except Exception as e:
        print(f'An error occurred while copying files: {e}')
        sys.exit(1)
        
def run_ez80asm(asm_src_dir,asm_src_filename,tgt_bin_dir,tgt_emulator_bin_dir,tgt_bin_filename,original_dir):
    os.chdir(asm_src_dir)
    command = ["ez80asm","-l",asm_src_filename,tgt_bin_filename]
    print(f"Assembling with command: {' '.join(command)}")
    try:
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(result.stdout.decode())
    except subprocess.CalledProcessError as e:
        print(e.output.decode(errors='ignore'))
        return False
    shutil.move(tgt_bin_filename, f'{tgt_bin_dir}/{tgt_bin_filename}')
    shutil.copy2(f'{tgt_bin_dir}/{tgt_bin_filename}', f'{tgt_emulator_bin_dir}/{tgt_bin_filename}')
    os.chdir(original_dir)

def run_fab_emulator(emulator_dir,autoexec_text,original_dir):
    autoexec_file = os.path.join(emulator_dir, 'sdcard/autoexec.txt')
    write_autoexec(autoexec_file, autoexec_text)
    
    if not os.path.exists(emulator_dir):
        print(f'Error: Directory {emulator_dir} does not exist.')
        sys.exit(1)

    if not os.path.exists(autoexec_file):
        print(f'Error: File {autoexec_file} does not exist.')
        sys.exit(1)
    
    command = os.path.join(emulator_dir, 'fab-agon-emulator')
    if not os.path.exists(command):
        print(f'Error: Emulator executable {command} does not exist.')
        sys.exit(1)
    
    try:
        os.chdir(emulator_dir)
        print(f'Changed to directory: {os.getcwd()}')

        # Start the emulator as a separate process, suppressing its I/O
        with open(os.devnull, 'wb') as devnull:
            process = subprocess.Popen(
                [command],
                stdout=devnull,
                stderr=devnull,
                stdin=devnull
            )
        print(f'Emulator started with PID {process.pid}')

    except Exception as e:
        print(f'An error occurred while starting the emulator: {e}')
        sys.exit(1)
    
    finally:
        os.chdir(original_dir)
        print(f'Returned to original directory: {os.getcwd()}')

def write_autoexec(autoexec_file, autoexec_text):
    print(f'Autoexec file: {autoexec_file} with text:\r\n{autoexec_text}')
    if autoexec_text:
        with open(autoexec_file, 'w') as f:
            # Write each line with explicit CRLF line endings
            for line in autoexec_text:
                f.write(line + '\r\n')

def expand_lst(input_filename, output_filename, exclude_comments=False):
    """Read input lines, expand multibyte lines, and write to the output file.
       If exclude_comments is True, lines where the first non-whitespace character
       in column 4 (if exists) is a semicolon are not output."""
    # Read all lines from the input file and close it
    with open(input_filename, 'r') as infile:
        lines = infile.readlines()

    current_address = None  # Tracks the current address

    # Open the output file for writing
    with open(output_filename, 'w') as output_file:
        for line in lines:
            # Splitting the line based on fixed-width columns
            col1 = line[:7].strip()       # Address (7 chars)
            col2 = line[7:19].strip()     # Byte code (12 chars)
            col3_and_4 = line[19:].rstrip()  # Line number and source code (rest of the line)

            # Separate the line number and source code
            col3_split = col3_and_4.split(maxsplit=1)
            col3 = col3_split[0].strip().rjust(8) if col3_split else ""
            col4 = col3_split[1] if len(col3_split) > 1 else ""

            # Check for comment lines in col4 if exclude_comments is True
            if exclude_comments and col4 and col4.lstrip().startswith(';'):
                continue  # Skip this line

            # Update the current address if available
            if col1:
                try:
                    current_address = int(col1, 16)
                except ValueError:
                    current_address = None

            # Expand byte code if present
            if col2:
                bytes_list = col2.split()

                # Write the first byte with source line details
                if current_address is not None:
                    output_file.write(f"{current_address:06X} {bytes_list[0]:<3} {col3} {col4}\n")
                    for byte in bytes_list[1:]:
                        current_address += 1
                        output_file.write(f"{current_address:06X} {byte:<3}\n")
                else:
                    output_file.write(f"{' ' * 7} {bytes_list[0]:<3} {col3} {col4}\n")
                    for byte in bytes_list[1:]:
                        output_file.write(f"{' ' * 7} {byte:<3}\n")
            else:
                # Handle lines without byte code
                if col3 or col4:
                    output_file.write(f"{' ' * 7} {' ' * 2} {col3} {col4}\n")
                else:
                    output_file.write(f"{' ' * 7}\n")

def build_and_run(
    asm_src_dir,
    tgt_bin_dir,
    emulator_dir,
    mos_dir,
    assemble,
    copy_sdcard,
    copy_sdcard_include_pattern,
    run_emulator,
    autoexec_text,
    app_name,
    tgt_bin_filename
):
    original_dir = os.getcwd()

    sdcard_tgt_dir = f'/media/smith/AGON/{mos_dir}'
    tgt_emulator_bin_dir = f'{emulator_dir}/sdcard/{mos_dir}'
    asm_src_filename = f'{app_name}.asm'

    # Execute functions based on parameters
    if assemble:
        run_ez80asm(asm_src_dir,asm_src_filename,tgt_bin_dir,tgt_emulator_bin_dir,tgt_bin_filename,original_dir)
    if copy_sdcard:
        if os.path.exists(sdcard_tgt_dir):
            copy_to_directory(tgt_emulator_bin_dir, sdcard_tgt_dir, copy_sdcard_include_pattern)
        else:
            print(f"SD card target directory not found: {sdcard_tgt_dir}")
    if run_emulator:
        run_fab_emulator(emulator_dir,autoexec_text,original_dir)

if __name__ == '__main__':
    emulator_dir = os.path.expanduser('~/Agon/emulator')
    asm_src_dir = os.path.expanduser('~/Agon/emulator/sdcard/mystuff/agon-utils/examples/flower/src')
    tgt_bin_dir = os.path.expanduser('~/Agon/emulator/sdcard/mystuff/agon-utils/examples/flower/tgt')
    mos_dir = 'mos'

    if True:
        app_name = 'flower'
        tgt_bin_filename = f'{app_name}.bin'
        copy_sdcard_include_pattern = f'{re.escape(app_name)}\\.bin'
        autoexec_text = []
        assemble = True
        copy_sdcard = False
        run_emulator = False
        build_and_run(asm_src_dir,tgt_bin_dir,emulator_dir,mos_dir,assemble,copy_sdcard,copy_sdcard_include_pattern,run_emulator,autoexec_text,app_name,tgt_bin_filename)
        lst_filepath = f'{asm_src_dir}/{app_name}.lst'
        expand_lst(lst_filepath, lst_filepath, exclude_comments=False)
        shutil.move(lst_filepath, f'{tgt_bin_dir}/{app_name}.lst')

    if False:
        app_name = 'evalbas'
        tgt_bin_filename = f'{app_name}.bin'
        copy_sdcard_include_pattern = f'{re.escape(app_name)}\\.bin'
        autoexec_text = []
        assemble = True
        copy_sdcard = False
        run_emulator = False
        build_and_run(asm_src_dir,tgt_bin_dir,emulator_dir,mos_dir,assemble,copy_sdcard,copy_sdcard_include_pattern,run_emulator,autoexec_text,app_name,tgt_bin_filename)
        lst_filepath = f'{asm_src_dir}/{app_name}.lst'
        expand_lst(lst_filepath, lst_filepath, exclude_comments=False)
        shutil.move(lst_filepath, f'{tgt_bin_dir}/{app_name}.lst')

    if False:
        app_name = 'calcbas'
        tgt_bin_filename = f'{app_name}.bin'
        copy_sdcard_include_pattern = f'{re.escape(app_name)}\\.bin'
        autoexec_text = []
        assemble = True
        copy_sdcard = False
        run_emulator = False
        build_and_run(asm_src_dir,tgt_bin_dir,emulator_dir,mos_dir,assemble,copy_sdcard,copy_sdcard_include_pattern,run_emulator,autoexec_text,app_name,tgt_bin_filename)
        lst_filepath = f'{asm_src_dir}/{app_name}.lst'
        expand_lst(lst_filepath, lst_filepath, exclude_comments=False)
        shutil.move(lst_filepath, f'{tgt_bin_dir}/{app_name}.lst')
