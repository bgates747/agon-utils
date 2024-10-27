
import os
import re
import shutil
import subprocess
import sys


def write_autoexec(autoexec_file, autoexec_text):
    """
    Creates a text file containing commands for the emulator, with CRLF line endings.
    :param autoexec_file: Path where the autoexec.txt file will be modified
    :param autoexec_text: List of strings to write to the file
    """

    # Open the file in write mode with newline set to '\r\n'
    with open(autoexec_file, 'w') as f:
        # Write each line with explicit CRLF line endings
        for line in autoexec_text:
            f.write(line + '\r\n')

def build_and_deploy_fonts(
        asm_src_dir,
        emulator_dir,
        assemble,
        copy_sdcard,
        run_emulator
):
    """
    Assembles font files, copies to emulator and SD card directories, and runs the emulator.

    :param asm_src_dir: Directory containing the assembly source file
    :param asm_src_filename: Assembly source file name
    :param tgt_bin_filename: Output binary file (created in asm_src_dir, then moved)
    ;param tgt_font_dir: Target directory for font files
    :param emulator_dir: Source directory for emulator files
    :param emulator_tgt_dir: Target directory in the emulator
    :param sdcard_tgt_dir: Target directory on the SD card
    :param emulator_exec: Path to the emulator executable
    :param assemble: Flag to run the assembler
    :param copy_emulator: Flag to copy files to emulator
    :param copy_sdcard: Flag to copy files to SD card
    :param run_emulator: Flag to run the emulator
    """
    original_dir = os.getcwd()

    sdcard_tgt_dir = f'/media/smith/AGON/{tgt_dir}'
    tgt_emulator_bin_dir = f'{emulator_dir}/sdcard/{tgt_dir}'
    asm_src_filename = f'{app_name}.asm'
    tgt_bin_filename = f'{app_name}.bin'

    def run_ez80asm():
        # Change working directory to the assembly directory
        os.chdir(asm_src_dir)

        # Build the ez80asm command
        command = [
            "ez80asm",
            asm_src_filename,
            f'{tgt_emulator_bin_dir}/{tgt_bin_filename}' 
        ]

        print(f"Assembling with command: {' '.join(command)}")

        # Execute the command
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(result.stdout.decode())

        # Restore the original working directory
        os.chdir(original_dir)

    def copy_to_directory(src_dir, tgt_dir, include_pattern=None):
        """
        Copies files from src_dir to tgt_dir, optionally filtering by a regex pattern.

        :param src_dir: Source directory to copy from
        :param tgt_dir: Target directory to copy to
        :param include_pattern: Optional regex pattern to filter files (default: None)
        """
        try:
            if os.path.exists(tgt_dir):
                shutil.rmtree(tgt_dir)
            os.makedirs(tgt_dir, exist_ok=True)

            # Walk through the source directory
            for root, _, files in os.walk(src_dir):
                for file in files:
                    # If a pattern is provided, check if the file matches the pattern
                    if include_pattern is None or re.match(include_pattern, file):
                        src_file = os.path.join(root, file)
                        rel_path = os.path.relpath(src_file, src_dir)
                        tgt_file = os.path.join(tgt_dir, rel_path)

                        os.makedirs(os.path.dirname(tgt_file), exist_ok=True)
                        shutil.copy2(src_file, tgt_file)

            print(f'Successfully copied files from {src_dir} to {tgt_dir}')

        except Exception as e:
            print(f'An error occurred while copying files: {e}')
            sys.exit(1)

    def run_fab_emulator():
        autoexec_file = os.path.join(emulator_dir, 'autoexec.txt')
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


    # Execute functions based on parameters
    if assemble:
        run_ez80asm()
    if copy_sdcard:
        if os.path.exists(sdcard_tgt_dir):
            copy_to_directory(tgt_emulator_bin_dir, sdcard_tgt_dir, include_pattern=r'.*\.(bin)$')
        else:
            print(f"SD card target directory not found: {sdcard_tgt_dir}")
    if run_emulator:
        run_fab_emulator()

if __name__ == '__main__':
    # Define the source and target directories
    tgt_dir = 'mos'
    app_name = 'mymoslet'
    emulator_dir = '/home/smith/Agon/emulator'
    asm_src_dir = 'examples/moslets'
    autoexec_text = [
        'SET KEYBOARD 1',
        f'cd /{tgt_dir}',
        # f'load {tgt_bin_filename}',
        # 'run'
    ]
    assemble = True
    copy_sdcard = False
    run_emulator = True

    build_and_deploy_fonts(
        asm_src_dir,
        emulator_dir,
        assemble,
        copy_sdcard,
        run_emulator
    )