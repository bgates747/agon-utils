#!/usr/bin/env python3
import agonutils as au
import os
from PIL import Image

def main():

    for base_file in base_files:
        base_file = os.path.abspath(base_file)
        image = Image.open(base_file)
        image_width, image_height = image.size
        base_file = os.path.splitext(base_file)[0]

        src_png_file = f"{base_file}.png"
        tgt_png_file = f"{base_file}_{palette_conversion_method}.png"
        tgt_rgba2_file = f"{base_file}_{palette_conversion_method}.rgba2"
        
        # Convert PNG to palette-mapped PNG
        au.convert_to_palette(src_png_file, tgt_png_file, palette_file, palette_conversion_method, transparent_color)

        # Convert PNG to RGBA2
        au.img_to_rgba2(src_png_file, tgt_rgba2_file, palette_file, palette_conversion_method, transparent_color)

        # Convert RGBA2 back to PNG for verification
        au.rgba2_to_img(tgt_rgba2_file, f"{base_file}_check.png", image_width, image_height)


if __name__ == '__main__':
    palette_conversion_method = 'bayer'
    transparent_color = (0, 0, 0, 0)  # Alpha 0 means NO transparent color
    palette_file = '/home/smith/Agon/mystuff/agon-utils/examples/palettes/Agon64.gpl'

    base_files = [
        'tests/images/rainbow_320x240.png',
        'tests/images/rainbow_512x384.png',
        'tests/images/rainbow_640x480.png'
    ]

    main()
