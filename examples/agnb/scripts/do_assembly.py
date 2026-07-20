import subprocess
import sys
import os
import shutil
import argparse

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
AGNB_DIR = os.path.dirname(SCRIPT_DIR)

def run_ez80asm():
    try:
        # Store the current working directory
        original_dir = os.getcwd()

        # Define the directory containing the .asm file
        asm_directory = os.path.join(AGNB_DIR, "src", "asm")
        asm_file = "app.asm"
        output_file = os.path.join(AGNB_DIR, "tgt", "app.bin")
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        # Change working directory to the directory containing the .asm file
        os.chdir(asm_directory)

        # Define the command with relative paths from the new working directory
        command = [
            "ez80asm",
            "-l",              # Option to generate listing file
            asm_file,          # Input assembly file
            output_file        # Output binary file (relative path from the new directory)
        ]

        # Execute the command
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Print the output
        print(result.stdout.decode())
        
    except subprocess.CalledProcessError as e:
        # Print the error message if the command fails
        print(f"Command failed with error: {e.stderr.decode()}")
        sys.exit(1)
    except Exception as e:
        # Handle other exceptions (e.g., if directory change fails)
        print(f"An error occurred: {e}")
        sys.exit(1)
    finally:
        # Restore the original working directory
        os.chdir(original_dir)

def copy_to_emulator():
    try:
        # Store the current working directory
        original_dir = os.getcwd()

        # Define the source and target directories
        src_directory = os.path.join(AGNB_DIR, "tgt")
        tgt_directory = os.path.join(
            AGNB_DIR, ".emulator", "sdcard", "mystuff", "agon-utils",
            "examples", "agnb", "tgt",
        )

        # Change working directory to the original directory to ensure correct paths
        os.chdir(original_dir)

        # Check if the target directory exists, if so, delete it recursively
        if os.path.exists(tgt_directory):
            shutil.rmtree(tgt_directory)  # Remove the target directory and its contents

        # Recreate the target directory
        os.makedirs(tgt_directory)

        # Copy everything from the source directory to the target directory
        shutil.copytree(src_directory, tgt_directory, dirs_exist_ok=True)

        print(f"Successfully copied files from {src_directory} to {tgt_directory}")

    except Exception as e:
        print(f"An error occurred while copying files: {e}")
        sys.exit(1)

def copy_to_sdcard():
    try:
        # Define the source and target directories
        src_directory = os.path.join(AGNB_DIR, "tgt")
        tgt_directory = "/media/smith/AGON/mystuff/agon-utils/examples/agnb/tgt"

        # Check if the target directory exists, if so, delete it recursively
        if os.path.exists(tgt_directory):
            shutil.rmtree(tgt_directory)  # Remove the target directory and its contents

        # Recreate the target directory
        os.makedirs(tgt_directory)

        # Copy everything from the source directory to the target directory
        shutil.copytree(src_directory, tgt_directory, dirs_exist_ok=True)

        print(f"Successfully copied files from {src_directory} to {tgt_directory}")

    except Exception as e:
        print(f"An error occurred while copying files: {e}")
        sys.exit(1)

def run_fab_agon_emulator():
    try:
        emulator_directory = os.path.join(AGNB_DIR, ".emulator")
        emulator_executable = os.path.join(
            emulator_directory, "fab-agon-emulator"
        )

        if not os.path.isfile(emulator_executable):
            raise FileNotFoundError(
                f"Emulator executable not found: {emulator_executable}"
            )

        process = subprocess.Popen(
            [emulator_executable],
            cwd=emulator_directory,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        print(f"Launched fab-agon-emulator in background (PID {process.pid})")

    except Exception as e:
        print(f"An error occurred while launching the emulator: {e}")
        sys.exit(1)


def main():
    # Create an argument parser
    parser = argparse.ArgumentParser(description="Run assembly, copy, and emulator commands.")
    
    # Add optional switches for each function
    parser.add_argument('-a', action='store_true', help="Run ez80asm assembly")
    parser.add_argument('-c', action='store_true', help="Copy files to emulator")
    parser.add_argument('-e', action='store_true', help="Run fab-agon-emulator")
    parser.add_argument('-sd', action='store_true', help="Copy files to SD card")

    # Parse the arguments
    args = parser.parse_args()

    # If no options are given, run all functions
    if not args.a and not args.c and not args.e and not args.sd:
        run_ez80asm()
        copy_to_emulator()
        copy_to_sdcard()
        run_fab_agon_emulator()
    else:
        if args.a:
            run_ez80asm()
        if args.c:
            copy_to_emulator()
        if args.sd:
            copy_to_sdcard()
        if args.e:
            run_fab_agon_emulator()

if __name__ == "__main__":
    main()
