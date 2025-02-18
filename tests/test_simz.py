#!/usr/bin/env python3
import agonutils as au
import os

if __name__ == '__main__':
    # Set file paths
    in_file = 'utils/rngcod13/frame_00005.rgba2'
    out_file = f'{in_file}.simz'
    un_zipped_file = f'{in_file}.rgba2'  # Decompressed file

    print("=== Testing file-based simz_encode/simz_decode ===")

    # Compress the file
    au.simz_encode(in_file, out_file)

    # Decompress the file
    au.simz_decode(out_file, un_zipped_file)

    # Compute compression percentage
    compressed_size = os.path.getsize(out_file)
    uncompressed_size = os.path.getsize(un_zipped_file)
    compression_percentage = (compressed_size / uncompressed_size) * 100
    print(f'Compression percentage: {compression_percentage:.2f}%')

    # Compare original and decompressed files using diff
    diff_result = os.system(f'diff {un_zipped_file} {in_file}')
    print("File-based encode/decode:", "PASS" if diff_result == 0 else "FAIL")

    print("\n=== Testing in-memory simz_encode_bytes/simz_decode_bytes ===")

    # Read input file into a bytes buffer
    with open(in_file, "rb") as f:
        input_bytes = f.read()

    # Compress in-memory
    compressed_bytes = au.simz_encode_bytes(input_bytes)

    # Read compressed file and compare with in-memory compression output
    with open(out_file, "rb") as f:
        file_compressed_bytes = f.read()

    if compressed_bytes == file_compressed_bytes:
        print("In-memory compression matches file compression: PASS")
    else:
        print("In-memory compression differs from file compression: FAIL")

    # Decompress in-memory
    decompressed_bytes = au.simz_decode_bytes(compressed_bytes)

    # Read original input file again to compare
    if decompressed_bytes == input_bytes:
        print("In-memory decompression matches original input: PASS")
    else:
        print("In-memory decompression differs from original input: FAIL")
