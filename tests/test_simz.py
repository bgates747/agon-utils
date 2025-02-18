#!/usr/bin/env python3
import agonutils as au
import os

if __name__ == '__main__':
    # Set file paths
    in_file = 'utils/rngcod13/frame_00005.rgba2'
    out_file = f'{in_file}.simz'
    un_zipped_file = f'{in_file}.rgba2'  # Use a proper name for the decompressed file

    # Compress the file
    au.simz_encode(in_file, out_file)

    # Decompress the file
    au.simz_decode(out_file, un_zipped_file)  # FIXED ARGUMENT ORDER

    # Compute compression percentage (compressed/uncompressed*100)
    compressed_size = os.path.getsize(out_file)
    uncompressed_size = os.path.getsize(un_zipped_file)
    compression_percentage = (compressed_size / uncompressed_size) * 100
    print(f'Compression percentage: {compression_percentage:.2f}%')

    # Compare the original and decompressed files using diff
    os.system(f'diff {un_zipped_file} {in_file}')
