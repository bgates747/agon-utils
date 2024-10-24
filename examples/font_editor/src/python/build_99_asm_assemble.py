import subprocess
import sys
import os
import shutil
from build_91c_asm_font import build_fonts_asm, make_cfg

def write_autoexec(file_path, tgt_dir, bin_file):
    """
    Creates a text file containing commands for the emulator, with CRLF line endings.

    :param file_path: Path where the script file will be saved
    :param tgt_dir: Directory path for the emulator target directory
    :param bin_file: The filename of the assembled binary file
    """
    # Define the lines for the emulator script
    script_lines = [
        'SET KEYBOARD 1',
        f'cd {tgt_dir}',
        f'load {bin_file}',
        'run'
    ]

    # Open the file in write mode with newline set to '\r\n'
    with open(file_path, 'w') as f:
        # Write each line with explicit CRLF line endings
        for line in script_lines:
            f.write(line + '\r\n')

def build_and_deploy_fonts(
    font_filename,
    screen_mode,
    asm_dir,
    asm_file,
    tgt_bin_dir,
    tgt_bin_file,
    emulator_dir,
    emulator_tgt_dir,
    sdcard_tgt_dir,
    emulator_exec,
    build_fonts,
    assemble,
    copy_emulator,
    copy_sdcard,
    run_emulator
):
    """
    Assembles font files, copies to emulator and SD card directories, and runs the emulator.

    :param asm_dir: Directory containing the assembly source file
    :param asm_file: Assembly source file name
    :param tgt_bin_file: Output binary file (created in asm_dir, then moved)
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

    def run_ez80asm():
        success = False  # Initialize success flag
        try:
            # Change working directory to the assembly directory
            os.chdir(asm_dir)

            # Define the output file local to the assembly directory
            local_output_file = os.path.join(asm_dir, tgt_bin_file)

            # Build the ez80asm command
            command = [
                "ez80asm",
                asm_file,          # Input assembly file
                "-l",              # Option to generate listing file
                tgt_bin_file       # Output local binary file
            ]

            print(f"Assembling with command: {' '.join(command)}")

            # Execute the command
            result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(result.stdout.decode())

            # Set success flag if assembly is successful
            success = True

        except subprocess.CalledProcessError as e:
            print(f'Assembly failed with error: {e.stderr.decode()}')
            sys.exit(1)
        except Exception as e:
            print(f'An error occurred during assembly: {e}')
            sys.exit(1)
        finally:
            # Restore the original working directory
            os.chdir(original_dir)

        # Move the assembled file to the target directory if successful
        if success:
            tgt_full_path = os.path.join(tgt_bin_dir, tgt_bin_file)
            shutil.move(local_output_file, tgt_full_path)
            print(f'Successfully assembled and moved to {tgt_full_path}')

    def copy_to_directory(src_dir, tgt_dir):
        try:
            if os.path.exists(tgt_dir):
                shutil.rmtree(tgt_dir)
            shutil.copytree(src_dir, tgt_dir, dirs_exist_ok=True)
            print(f'Successfully copied files from {src_dir} to {tgt_dir}')

        except Exception as e:
            print(f'An error occurred while copying files: {e}')
            sys.exit(1)

    def run_fab_emulator():
        autoexec_file = os.path.join(emulator_dir, 'sdcard', 'autoexec.txt')
        write_autoexec(autoexec_file, emulator_tgt_dir, tgt_bin_file)
        try:
            os.chdir(emulator_dir)

            command = [os.path.basename(emulator_exec)]
            
            # Start the emulator as a separate process, suppressing its I/O
            with open(os.devnull, 'wb') as devnull:
                process = subprocess.Popen(
                    command,
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


    # Execute functions based on parameters
    if build_fonts:
        make_cfg(font_filename, screen_mode, asm_dir)
        build_fonts_asm(asm_dir, tgt_bin_dir)
    if assemble:
        run_ez80asm()
    if copy_emulator:
        print("Copying emulator files disabled.")
        # copy_to_directory(emulator_dir, emulator_tgt_dir)
    if copy_sdcard:
        print("Copying SD card files disabled.")
        # copy_to_directory(emulator_dir, sdcard_tgt_dir)
    if run_emulator:
        run_fab_emulator()

# Example of calling the function with parameters
if __name__ == '__main__':
    font_filename = 'Apple Chancery_Narrow_16x32.font'
    screen_mode = 19
    asm_dir = 'examples/font_editor/src/asm'
    asm_file = 'app.asm'
    tgt_bin_dir = 'examples/font_editor/tgt'
    tgt_bin_file = f'font.bin'
    emulator_dir = '/home/smith/Agon/.emulator'
    emulator_tgt_dir = f'/mystuff/agon-utils/{tgt_bin_dir}'
    sdcard_tgt_dir = '/media/smith/AGON/mystuff/fonts/tgt'
    emulator_exec = './fab-agon-emulator'

    build_fonts = True
    assemble = True
    copy_emulator = False
    copy_sdcard = False
    run_emulator = True

    build_and_deploy_fonts(
        font_filename,
        screen_mode,
        asm_dir,
        asm_file,
        tgt_bin_dir,
        tgt_bin_file,
        emulator_dir,
        emulator_tgt_dir,
        sdcard_tgt_dir,
        emulator_exec,
        build_fonts,
        assemble,
        copy_emulator,
        copy_sdcard,
        run_emulator
    )