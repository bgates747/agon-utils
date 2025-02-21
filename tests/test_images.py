#!/usr/bin/env python3
import agonutils as au
import os
from PIL import Image
import subprocess


def report_compression(compression_type, original_file, compressed_file):
    """Report the compression percentage for a file."""
    compressed_size = os.path.getsize(compressed_file)
    uncompressed_size = os.path.getsize(original_file)
    compression_percentage = (compressed_size / uncompressed_size) * 100
    print(f'{compression_type} percentage: {compression_percentage:.2f}%')


def diff_files(file1, file2):
    """Compare two files and return whether they are the same."""
    result = subprocess.run(["diff", "-q", file1, file2], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if result.returncode == 0:
        return f"{file1} is the same as {file2}"
    else:
        return f"{file1} is NOT the same as {file2}"


def main():
    # Convert PNG to palette-mapped PNG
    au.convert_to_palette(src_png_file, tgt_png_file, palette_file, palette_conversion_method, transparent_color)

    # Convert PNG to RGBA2
    au.img_to_rgba2(src_png_file, tgt_rgba2_file, palette_file, palette_conversion_method, transparent_color)

    # Convert RGBA2 back to PNG for verification
    au.rgba2_to_img(tgt_rgba2_file, f"{base_file}_check.png", image_width, image_height)

    # Compression & Decompression Tests
    tests = [
        ("SZIP", ["szip", tgt_rgba2_file, tgt_szip_file], ["szip", "-d", tgt_szip_file, "temp"]),
        ("SIMZ", ["simz", "-c", tgt_rgba2_file, tgt_simz_file], ["simz", "-d", tgt_simz_file, "temp"]),
        # ("TVC", ["tvcompress", tgt_rgba2_file, tgt_tvc_file], ["tvdecompress", tgt_tvc_file, "temp"]),
        ("RLE", ["rlecompress", tgt_rgba2_file, f"{tgt_rgba2_file}.rle"], ["rledecompress", f"{tgt_rgba2_file}.rle", "temp"]),
        ("MSKZ", ["mskz", "-c", tgt_rgba2_file, f"{tgt_rgba2_file}.mskz"], ["mskz", "-d", f"{tgt_rgba2_file}.mskz", "temp"]),
    ]

    for compression_type, compress_cmd, decompress_cmd in tests:
        # Compress
        subprocess.run(compress_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        report_compression(compression_type, tgt_rgba2_file, compress_cmd[-1])

        # Decompress
        subprocess.run(decompress_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # Compare with original
        print(diff_files(tgt_rgba2_file, "temp"))

        # Remove temp file
        os.remove("temp")


if __name__ == '__main__':
    palette_conversion_method = 'floyd'
    transparent_color = (0, 0, 0, 0)  # Alpha 0 means NO transparent color
    palette_file = '/home/smith/Agon/mystuff/agon-utils/examples/palettes/Agon64.gpl'
    base_file = "/home/smith/Agon/mystuff/AgonJukebox/tgt/images/rainbow_swirl"

    src_png_file = f"{base_file}.png"
    tgt_png_file = f"{base_file}_{palette_conversion_method}.png"
    tgt_rgba2_file = f"{base_file}.rgba2"
    tgt_tvc_file = f"{tgt_rgba2_file}.tvc"
    tgt_szip_file = f"{tgt_rgba2_file}.szip"
    tgt_simz_file = f"{tgt_rgba2_file}.simz"

    src_img = Image.open(src_png_file)
    image_width, image_height = src_img.size
    print(f"Image width: {image_width}, height: {image_height}")

    main()
