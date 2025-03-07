import time
import os
import shutil
import re
from PIL import Image
import agonutils as au


def prepare_directories(*dirs):
    """
    Ensure that all specified directories are empty and recreated.
    """
    for dir_path in dirs:
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)
        os.makedirs(dir_path)


def convert_to_png(originals_dir):
    """
    Convert non-.png files (.jpeg, .jpg, .gif) to .png in the originals directory.
    """
    for root, _, files in os.walk(originals_dir):
        for file in files:
            input_image_path = os.path.join(root, file)
            if file.endswith(('.jpeg', '.jpg', '.gif')):
                img = Image.open(input_image_path)
                png_path = os.path.splitext(input_image_path)[0] + '.png'
                img.save(png_path, 'PNG')
                os.remove(input_image_path)


def convert_to_palette(originals_dir, output_dir_processed, palette_filepath, palete_conversion_method, transparent_rgb):
    """
    Convert .png files to the Agon palette and save them in the processed directory.
    """
    for root, _, files in os.walk(originals_dir):
        for file in files:
            if file.endswith('.png'):
                input_image_path = os.path.join(root, file)
                output_image_path = os.path.join(output_dir_processed, os.path.relpath(input_image_path, originals_dir))
                os.makedirs(os.path.dirname(output_image_path), exist_ok=True)

                with Image.open(input_image_path) as img:
                    if "icc_profile" in img.info:
                        img.info.pop("icc_profile")
                    img.save(input_image_path, 'PNG')  # Ensure PNG is valid for processing
                au.convert_to_palette(
                    input_image_path, output_image_path, palette_filepath, palete_conversion_method, transparent_rgb
                )


def convert_to_rgba(output_dir_processed, output_dir_rgba, image_type):
    """
    Convert palette-converted .png files to .rgba2 or .rgba8 format.
    """
    for root, _, files in os.walk(output_dir_processed):
        for file in files:
            if file.endswith('.png'):
                input_image_path = os.path.join(root, file)
                output_image_path = os.path.join(output_dir_rgba, os.path.relpath(input_image_path, output_dir_processed))
                os.makedirs(os.path.dirname(output_image_path), exist_ok=True)

                if image_type == 1:
                    au.img_to_rgba2(input_image_path, output_image_path)
                else:
                    au.img_to_rgba8(input_image_path, output_image_path)


def write_assembly_files(output_dir_rgba, asm_base_dir):
    """
    Write assembly files for the processed images in each directory.
    """
    files_by_dir = {}
    for root, _, files in os.walk(output_dir_rgba):
        for file in files:
            if file.endswith('.rgba2') or file.endswith('.rgba8'):
                rel_path = os.path.relpath(os.path.join(root, file), output_dir_rgba)
                dir_path = os.path.dirname(rel_path)
                files_by_dir.setdefault(dir_path, []).append(rel_path)

    for dir_path, rel_files in sorted(files_by_dir.items()):
        buffer_id = 256
        num_images = 0
        image_list = []
        files_list = []
        buffer_ids = []

        image_dir = f'images/{dir_path}'
        files_list.append(f'image_dir: db "{image_dir}",0\n\n')

        for rel_path in sorted(rel_files):
            input_image_path = os.path.join(output_dir_rgba, rel_path)
            file_name, _ = os.path.splitext(os.path.basename(rel_path))
            image_width, image_height = Image.open(input_image_path).size
            image_filesize = os.path.getsize(input_image_path)

            buffer_ids.append(f'buf_{file_name}: equ {buffer_id}\n')
            image_list.append(
                f'\tdl 1, {image_width}, {image_height}, {image_filesize}, fn_{file_name}\n'
            )
            files_list.append(
                f'fn_{file_name}: db "{file_name}.rgba2",0 \n'
            )

            buffer_id += 1
            num_images += 1

        asm_file_path = os.path.join(asm_base_dir, 'images_' + dir_path.replace('/', '_') + '.inc')
        os.makedirs(os.path.dirname(asm_file_path), exist_ok=True)

        with open(asm_file_path, 'w') as f:
            f.write('; Generated by make_images.py\n\n')
            f.write('image_type: equ 0\n')
            f.write('image_width: equ image_type+3\n')
            f.write('image_height: equ image_width+3\n')
            f.write('image_filesize: equ image_height+3\n')
            f.write('image_filename: equ image_filesize+3\n')
            f.write('image_record_size: equ image_filename+3\n\n')
            f.write(f'num_images: equ {num_images}\n\n')
            f.write('; buffer_ids:\n')
            f.write(''.join(buffer_ids))
            f.write('\n')
            f.write('image_list:\n')
            f.write(''.join(image_list))
            f.write('\n')
            f.write('; files_list: ; filename:\n')
            f.write(''.join(files_list))

def create_tilesheets(input_dir, tile_width, tile_height, target_width, target_height, starting_index=0):
    """
    Combine .png images from the input directory into tilesheets without resizing.
    
    Parameters:
    - input_dir (str): Directory containing .png images.
    - tile_width (int): Width of each individual tile.
    - tile_height (int): Height of each individual tile.
    - target_width (int): Width of the tilesheet in pixels.
    - target_height (int): Height of the tilesheet in pixels.
    """
    png_files = sorted(
        [
            os.path.join(root, file)
            for root, _, files in os.walk(input_dir)
            for file in files if file.endswith('.png')
        ]
    )

    # Calculate number of tiles per sheet
    tiles_per_row = target_width // tile_width
    tiles_per_col = target_height // tile_height
    tiles_per_sheet = tiles_per_row * tiles_per_col

    # Prepare the output directory
    base_name = os.path.basename(os.path.normpath(input_dir))
    output_dir = input_dir  # Save tilesheets in the same directory
    os.makedirs(output_dir, exist_ok=True)

    tilesheet_index = starting_index
    current_tile_index = 0
    tilesheet_image = Image.new("RGBA", (target_width, target_height), (0, 0, 0, 0))

    for png_file in png_files:
        with Image.open(png_file) as img:
            # Ensure the image matches the tile size
            if img.width != tile_width or img.height != tile_height:
                print(f"Skipping {png_file}: size {img.size} does not match tile size ({tile_width}, {tile_height})")
                continue

            # Calculate position on the current tilesheet
            x = (current_tile_index % tiles_per_row) * tile_width
            y = (current_tile_index // tiles_per_row) * tile_height

            # Paste the tile onto the tilesheet
            tilesheet_image.paste(img, (x, y))
            current_tile_index += 1

            # If the current tilesheet is full, save it and start a new one
            if current_tile_index >= tiles_per_sheet:
                tilesheet_path = os.path.join(output_dir, f"{base_name}_{tilesheet_index:02d}.png")
                tilesheet_image.save(tilesheet_path, "PNG")
                tilesheet_index += 1
                current_tile_index = 0
                tilesheet_image = Image.new("RGBA", (target_width, target_height), (0, 0, 0, 0))

    # Save the last tilesheet if it has any tiles
    if current_tile_index > 0:
        tilesheet_path = os.path.join(output_dir, f"{base_name}_{tilesheet_index:02d}.png")
        tilesheet_image.save(tilesheet_path, "PNG")

if __name__ == '__main__':
    # Define parameters
    originals_dir = 'examples/tiles/assets/orig/denzi'
    output_dir_processed = 'examples/tiles/assets/processed/denzi'
    output_dir_rgba = 'examples/tiles/tgt/images/denzi'
    asm_base_dir = 'examples/tiles/src'
    palette_filepath = 'examples/tiles/palettes/Agon64.gpl'
    transparent_rgb = (0, 0, 0, 0)
    palete_conversion_method = 'rgb'
    image_type = 1  # RGBA2222


    # tile_width = 32
    # tile_height = 48
    # target_width = 512
    # target_height = 384
    # starting_index = 7

    # # Create tilesheets
    # create_tilesheets(originals_dir, tile_width, tile_height, target_width, target_height, starting_index)


    # Prepare directories
    prepare_directories(output_dir_processed, output_dir_rgba)

    # Convert non-PNG files to PNG
    convert_to_png(originals_dir)

    # Convert original PNGs to Agon palette
    convert_to_palette(originals_dir, output_dir_processed, palette_filepath, palete_conversion_method, transparent_rgb)

    # Convert palette PNGs to RGBA format
    convert_to_rgba(output_dir_processed, output_dir_rgba, image_type)

    # Write assembly files
    write_assembly_files(output_dir_rgba, asm_base_dir)
