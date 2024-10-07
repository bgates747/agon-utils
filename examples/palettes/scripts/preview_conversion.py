import agonutils as au
import time
import os

if __name__ == '__main__':
    input_image = 'examples/palettes/assets/me_toon.png'
    output_dir = 'examples/palettes/outputs'
    palette_filepath = 'examples/palettes/VRGB2222.gpl'
    base_name = os.path.basename(input_image)
    file_name, ext = os.path.splitext(base_name)
    palette_name = os.path.splitext(os.path.basename(palette_filepath))[0]

    start_time = time.perf_counter()

    # Transparent color (optional) set to None
    transparent_rgb = (0, 0, 0, 0)

    # # No dithering RGB565
    # output_image_rgb = f"{output_dir}/RGB565{ext}"
    # au.convert_to_rgb565(input_image, output_image_rgb)

    # No dithering RGB
    output_image_rgb = f"{output_dir}/RGB{ext}"
    au.convert_to_palette(input_image, output_image_rgb, palette_filepath, 'RGB', transparent_rgb)

    # # No dithering HSV
    # output_image_hsv = f"{output_dir}/HSV{ext}"
    # au.convert_to_palette(input_image, output_image_hsv, palette_filepath, 'HSV', transparent_rgb)

    # # No dithering CMYK
    # output_image_cmyk = f"{output_dir}/CMYK{ext}"
    # au.convert_to_palette(input_image, output_image_cmyk, palette_filepath, 'CMYK', transparent_rgb)

    # Atkinson dithering
    output_image_atkinson = f"{output_dir}/atkinson{ext}"
    au.convert_to_palette(input_image, output_image_atkinson, palette_filepath, 'atkinson', transparent_rgb)

    # Bayer dithering
    output_image_bayer = f"{output_dir}/bayer{ext}"
    au.convert_to_palette(input_image, output_image_bayer, palette_filepath, 'bayer', transparent_rgb)

    # Floyd-Steinberg dithering
    output_image_floyd = f"{output_dir}/floyd{ext}"
    au.convert_to_palette(input_image, output_image_floyd, palette_filepath, 'floyd', transparent_rgb)

    end_time = time.perf_counter()
    print(f"Conversion took {end_time - start_time} seconds")