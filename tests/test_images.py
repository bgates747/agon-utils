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

def main():
    # Palette convert PNG image to validation PNG image
    au.convert_to_palette(src_png_file, tgt_png_file, palette_file, palette_conversion_method, transparent_color)

    # Convert PNG to RGBA2 file
    au.img_to_rgba2(src_png_file, tgt_rgba2_file, palette_file, palette_conversion_method, transparent_color)

    # Convert RGBA2 to back to PNG to verify
    au.rgba2_to_img(tgt_rgba2_file, f"{base_file}_check.png", image_width, image_height)

    subprocess.run(["szip", tgt_rgba2_file, tgt_szip_file], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    report_compression("SZIP", tgt_rgba2_file, tgt_szip_file)

    # Compress files using PC command-line tools
    subprocess.run(["simz", "-c", tgt_rgba2_file, tgt_simz_file], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    report_compression("SIMZ", tgt_rgba2_file, tgt_simz_file)

    subprocess.run(["tvcompress", tgt_rgba2_file, tgt_tvc_file], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    report_compression("TVC", tgt_rgba2_file, tgt_tvc_file)
    
    subprocess.run(["rlecompress", tgt_rgba2_file, f"{tgt_rgba2_file}.rle"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    report_compression("RLE", tgt_rgba2_file, f"{tgt_rgba2_file}.rle")

if __name__ == '__main__':
    palette_conversion_method = 'floyd'
    transparent_color = (0,0,0,0) # Alpha 0 means NO transparent color
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