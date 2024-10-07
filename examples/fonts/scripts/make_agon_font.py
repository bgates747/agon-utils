
import os
from PIL import Image, ImageOps
import math

def byteify(pixels):
    """ Converts a list of 8 pixels (0 or 255) to a single byte. """
    byte = 0
    for i in range(len(pixels)):
        if pixels[i] == 255:  # White pixel
            byte |= (1 << (7 - i))  # Set the corresponding bit for the white pixel
    return byte

def image_to_bitstream(padded_img):
    """ Converts the cropped and padded image into a bitstream (bytearray). """
    bitstream = bytearray()
    width, height = padded_img.size
    
    # Convert image row by row into the bitstream
    for row in range(height):
        row_pixels = [padded_img.getpixel((col, row)) for col in range(width)]
        
        # Convert pixels to bytes (8 pixels per byte)
        for i in range(0, len(row_pixels), 8):
            byte = byteify(row_pixels[i:i+8])
            bitstream.append(byte)
    
    return bitstream

def precomputations(font_width, font_height, offset_width, offset_height, ascii_range, src_img_filepath):
    font_width_mod = font_width + offset_width
    font_height_mod = font_height + offset_height
    font_width_padded = math.ceil(font_width_mod / 8) * 8
    sample_width = font_width if offset_width >= 0 else font_width_mod
    sample_height = font_height if offset_height >= 0 else font_height
    
    # Open the source image
    src_img = Image.open(src_img_filepath)

    # Create a new source image the size of a full 256 character grid (16x16 grid of characters)
    src_img_new = Image.new('L', (font_width * 16, font_height * 16), color=0)

    # Paste the cropped image into the correct position in the new source image
    src_img_new.paste(src_img, (0, (ascii_range[0] // 16) * font_height))

    # Return necessary values
    return font_width_padded, font_height_mod, sample_width, sample_height, src_img_new

def sample_char_image(ascii_code, font_width, font_height, sample_width, sample_height, src_img_new):
    # Calculate the character's x and y coordinates in the grid
    chars_per_row = 16
    char_x = (ascii_code % chars_per_row) * font_width
    char_y = (ascii_code // chars_per_row) * font_height

    # Calculate the cropping box for the character
    crop_box = (char_x, char_y, char_x + sample_width, char_y + sample_height)

    # Crop and return the character image
    char_img = src_img_new.crop(crop_box)

    return char_img

def make_font(src_img_filepath, tgt_font_filepath, metadata_filepath, font_name, font_variant, font_width, font_height, offset_left, offset_top, offset_width, offset_height, ascii_range, sources_dir, tgt_dir):
    # Precompute offsets and image
    font_width_padded, font_height_mod, sample_width, sample_height, src_img_new = precomputations(font_width, font_height, offset_width, offset_height, ascii_range, src_img_filepath)

    font_data = bytearray()

    for ascii_code in range(0,256):
        char_img = Image.new('L', (font_width_padded, font_height_mod), color=0)
        char_img.paste(sample_char_image(ascii_code, font_width, font_height, sample_width, sample_height, src_img_new), (offset_left, offset_top))
        font_data.extend(image_to_bitstream(char_img))

    with open(tgt_font_filepath, 'wb') as f:
        f.write(font_data)

    # Save the final font image
    # tgt_font_img.show() 

                      
if __name__ == "__main__":
    font_name = 'computer_pixel_7'
    font_variant = 'Regular'
    font_width = 8
    font_height = 17
    offset_left = 0
    offset_top = 0
    offset_width = 0
    offset_height = 0

    ascii_range = (32, 127)
    sources_dir = 'src/ttf'
    tgt_dir = 'tgt/ttf'
    src_base_filename = f'{font_name}_{font_width}x{font_height}'
    tgt_base_filename = f'{font_name}_{font_variant}_{font_width}x{font_height}'
    src_img_filename = f'{src_base_filename}.png'
    tgt_font_filename = f'{tgt_base_filename}.font'
    src_img_filepath = f'{sources_dir}/{font_name}/{font_variant}/{src_img_filename}'
    tgt_font_filepath = f'{tgt_dir}/{tgt_font_filename}'
    metadata_dir = f'{sources_dir}/{font_name}/{font_variant}'
    metadata_filepath = f'{sources_dir}/{font_name}/{font_variant}/data.txt'

    make_font(src_img_filepath, tgt_font_filepath, metadata_filepath, font_name, font_variant, font_width, font_height, offset_left, offset_top, offset_width, offset_height, ascii_range, sources_dir, tgt_dir)
        


    # make_font(src_img_filepath, tgt_font_filepath, metadata_filepath, font_name, font_variant, font_width, font_height, offset_left, offset_top, offset_width, offset_height, ascii_range, sources_dir, tgt_dir)
