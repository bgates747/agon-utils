import os
import subprocess
import re

def concatenate_files(include_files, source_dir, combined_src_filenamename):
    with open(combined_src_filenamename, 'w') as outfile:
        for filename in include_files:
            include_filename = os.path.join(source_dir, filename)
            if os.path.isfile(include_filename):
                with open(include_filename, 'r') as infile:
                    content = infile.read()
                    # Write a header comment indicating the start of the file
                    outfile.write(f'; --- Begin {filename} ---\n')
                    outfile.write(content)
                    # Write a footer comment indicating the end of the file
                    outfile.write(f'; --- End {filename} ---\n\n')
                print(f"Included {filename}")
            else:
                print(f"Warning: {include_filename} not found.")

if __name__ == '__main__':
    # List of include statements as provided
    include_files = [
        'mos_api.inc',
        'macros.inc',
        'equs.inc',
        'init.asm',
        'eval.asm',
        'exec.asm',
        'fpp.asm',
        'gpio.asm',
        'main.asm',
        'misc.asm',
        'patch.asm',
        'sorry.asm',
        'agon_graphics.asm',
        'agon_sound.asm',
        'interrupts.asm',
        'ram.asm',
    ]

    source_dir = 'src'
    tgt_bin_dir = 'utils/bin'
    dif_dir = 'utils/dif'
    emulator_dir = '~/Agon/emulator/sdcard/bin'

    # Output filename
    src_base_filename = 'bbcbasic24ez'
    src_filepath = f'{source_dir}/{src_base_filename}.asm'
    symb_filepath = f'{source_dir}/{src_base_filename}.symbols'

    concatenate_files(include_files, source_dir, src_filepath)
    print(f"\nAll files have been concatenated into {src_filepath}")

    # Assemble the output file
    subprocess.run(f'(cd {source_dir} && ez80asm -l -s -b FF {src_base_filename}.asm)', shell=True, check=True)
    # Open the symbols file and find the address of the end_binary label
    with open(symb_filepath, 'r') as f:
        lines = f.readlines()
    for line in lines:
        if 'end_binary' in line:
            address = int(line.split()[1][1:], 16) - 0x040000
            break
    # Truncate the binary file to the end_binary address
    subprocess.run(f'head -c {address} {source_dir}/{src_base_filename}.bin > {source_dir}/{src_base_filename}.bin.tmp', shell=True, check=True)
    subprocess.run(f'mv {source_dir}/{src_base_filename}.bin.tmp {source_dir}/{src_base_filename}.bin', shell=True, check=True)
    print(f"Binary file truncated to address {address:06X}")
    # Copy the generated binary to the emulator directory
    subprocess.run(f'cp {source_dir}/{src_base_filename}.bin {emulator_dir}', shell=True, check=True)
    # Move the generated binary to the target directory
    subprocess.run(f'mv {source_dir}/{src_base_filename}.bin {tgt_bin_dir}', shell=True, check=True)
    # Move the generated listing file to the diff directory
    subprocess.run(f'mv {source_dir}/{src_base_filename}.lst {dif_dir}', shell=True, check=True)