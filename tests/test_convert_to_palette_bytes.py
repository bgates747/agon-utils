#!/usr/bin/env python3
import agonutils as au
import agonImages as ai
from PIL import Image

if __name__ == '__main__':
    method = 'floyd'
    transparent_color = None 
    palette_file = 'src/palettes/Agon64.gpl'

    base_file = "tests/rainbow_swirl"
    rgba2_file = f"{base_file}_{method}.rgba2"
    png_file = f"{base_file}.png"
    pil_img = Image.open(png_file).convert('RGBA')
    input_data = pil_img.tobytes()
    height = pil_img.height
    width = pil_img.width

    converted_bytes = agonutils.convert_to_palette_bytes(input_data, width, height, palette_file, method, transparent_color)

    pil_img2 = Image.frombytes('RGBA', (width, height), converted_bytes)
    pil_img2.save(f"{base_file}_{method}_bytes.png")

    agonutils.convert_to_palette(png_file, f"{base_file}_{method}_file.png", palette_file, method, transparent_color)