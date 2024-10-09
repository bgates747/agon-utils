from PIL import Image
import math

# =============================================================================
# Helper functions
# =============================================================================
def pad_to_byte(value):
    """Rounds up the given value to the nearest multiple of 8."""
    return (value + 7) // 8 * 8

def byteify(pixels):
    """ Converts a list of 8 pixels (0 or 255) to a single byte. """
    byte = 0
    for i in range(len(pixels)):
        if pixels[i] == 255:  # White pixel
            byte |= (1 << (7 - i))  # Set the corresponding bit for the white pixel
    return byte

# =============================================================================
# Font to png functions
# =============================================================================
def read_font_file(font_filepath, font_config):
    """
    Reads a .font file and returns a list of character images.
    Each byte in the file represents 8 horizontal pixels.
    
    :param font_filepath: Path to the .font file
    :param font_config: Dictionary with font configuration
    :return: A list of PIL images representing each character
    """
    char_width = font_config['font_width']
    char_height = font_config['font_height']
    ascii_range = (font_config['ascii_range_start'], font_config['ascii_range_end'])
    
    # Round the true width up to the nearest multiple of 8 (padded width)
    padded_width = pad_to_byte(char_width)
    bytes_per_row = padded_width // 8  # Number of bytes per row of the character
    bytes_per_character = bytes_per_row * char_height

    # Calculate the start and end character indices in the file
    start_char = ascii_range[0]
    num_chars = ascii_range[1] - start_char + 1  # Number of characters to read

    # Calculate the starting byte offset for the specified ASCII range
    start_offset = start_char * bytes_per_character

    char_images = []

    # Read the font data starting from the calculated offset
    with open(font_filepath, 'rb') as f:
        f.seek(start_offset)  # Move to the starting position in the file
        font_data = f.read(num_chars * bytes_per_character)

    for i in range(num_chars):
        # Create an image for each character with the padded width
        char_img = Image.new('L', (padded_width, char_height), color=0)  # 'L' mode for grayscale (1 byte per pixel)
        pixels = char_img.load()
        
        # Extract character data from the font data
        for y in range(char_height):
            row_start = i * bytes_per_character + y * bytes_per_row
            row_data = font_data[row_start:row_start + bytes_per_row]
            
            for byte_idx, byte in enumerate(row_data):
                for bit in range(8):
                    x = byte_idx * 8 + bit
                    if x < padded_width:  # Render the padded width (including the padded bits)
                        if byte & (1 << (7 - bit)):
                            pixels[x, y] = 255  # Set pixel to white (255) if the bit is set

        char_images.append(char_img)

    return char_images

def create_font_image(char_images, font_config, chars_per_row=16):
    """
    Creates a PNG image from the list of character images and arranges them in a grid.
    
    :param char_images: List of PIL Images representing each character
    :param font_config: Dictionary with font configuration
    :param chars_per_row: Number of characters per row in the final image
    :return: A PIL Image object with all characters arranged in a grid
    """
    char_width = font_config['font_width']
    char_height = font_config['font_height']
    num_chars = len(char_images)
    rows = (num_chars + chars_per_row - 1) // chars_per_row
    
    # Create an empty image to hold the font grid
    font_img = Image.new('L', (chars_per_row * char_width, rows * char_height), color=0)
    
    # Paste each character into the final image
    for i, char_img in enumerate(char_images):
        x = (i % chars_per_row) * char_width
        y = (i // chars_per_row) * char_height
        font_img.paste(char_img, (x, y))
    
    return font_img

# =============================================================================
# png to font functions
# =============================================================================

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

def precomputations(font_config, src_img):
    font_width = font_config['font_width']
    font_height = font_config['font_height']
    offset_width = font_config['offset_width']
    offset_height = font_config['offset_height']
    ascii_range = (font_config['ascii_range_start'], font_config['ascii_range_end'])
    
    font_width_mod = font_width + offset_width
    font_height_mod = font_height + offset_height
    font_width_padded = math.ceil(font_width_mod / 8) * 8
    sample_width = font_width if offset_width >= 0 else font_width_mod
    sample_height = font_height if offset_height >= 0 else font_height

    # Create a new source image the size of a full 256 character grid (16x16 grid of characters)
    src_img_new = Image.new('L', (font_width * 16, font_height * 16), color=0)

    # Paste the cropped image into the correct position in the new source image
    src_img_new.paste(src_img, (0, (ascii_range[0] // 16) * font_height))

    # Return necessary values
    return font_width_padded, font_height_mod, sample_width, sample_height, src_img_new

def sample_char_image(ascii_code, font_config, src_img_new):
    font_width = font_config['font_width']
    font_height = font_config['font_height']
    sample_width = font_config['font_width']
    sample_height = font_config['font_height']

    # Calculate the character's x and y coordinates in the grid
    chars_per_row = 16
    char_x = (ascii_code % chars_per_row) * font_width
    char_y = (ascii_code // chars_per_row) * font_height

    # Calculate the cropping box for the character
    crop_box = (char_x, char_y, char_x + sample_width, char_y + sample_height)

    # Crop and return the character image
    char_img = src_img_new.crop(crop_box)

    return char_img

def make_font(font_config, src_image, tgt_font_filepath):
    # Precompute offsets and image
    font_width_padded, font_height_mod, sample_width, sample_height, src_img_new = precomputations(font_config, src_image)

    font_data = bytearray()

    for ascii_code in range(0, 256):
        char_img = Image.new('L', (font_width_padded, font_height_mod), color=0)
        char_img.paste(sample_char_image(ascii_code, font_config, src_img_new), (font_config['offset_left'], font_config['offset_top']))
        font_data.extend(image_to_bitstream(char_img))

    with open(tgt_font_filepath, 'wb') as f:
        f.write(font_data)

# =============================================================================
# Modify font config functions
# =============================================================================

def resample_image(curr_config, mod_config, original_image):
    """
    Resample the original image to fit the modified configuration, handling offsets, padding, and ASCII range overlap.
    
    :param curr_config: Dictionary with the current font configuration.
    :param mod_config: Dictionary with the modified font configuration.
    :param original_image: The original PIL image to be resampled.
    :return: A new PIL image resampled to fit the modified configuration.
    """
    
    # Step 1: Prepare `adjusted_image` with offsets and padding applied to `original_image`
    adjusted_image = Image.new("L", original_image.size, color=0)
    crop_x1 = max(0, curr_config['offset_left'])
    crop_y1 = max(0, curr_config['offset_top'])
    crop_x2 = min(original_image.width, original_image.width + curr_config['offset_left'])
    crop_y2 = min(original_image.height, original_image.height + curr_config['offset_top'])
    cropped_original = original_image.crop((crop_x1, crop_y1, crop_x2, crop_y2))
    paste_x = max(0, -curr_config['offset_left'])
    paste_y = max(0, -curr_config['offset_top'])
    adjusted_image.paste(cropped_original, (paste_x, paste_y))

    # Step 2: Determine dimensions for the modified image
    mod_ascii_range_start = mod_config['ascii_range_start']
    mod_ascii_range_end = mod_config['ascii_range_end']
    mod_width = mod_config['font_width'] * 16  # Width for a 16-character row
    mod_height = mod_config['font_height'] * ((mod_ascii_range_end - mod_ascii_range_start + 1) // 16 + 1)
    mod_image = Image.new('L', (mod_width, mod_height), color=0)

    # Step 3: Determine the overlap of ASCII ranges
    curr_ascii_start = curr_config['ascii_range_start']
    curr_ascii_end = curr_config['ascii_range_end']
    overlap_start = max(curr_ascii_start, mod_ascii_range_start)
    overlap_end = min(curr_ascii_end, mod_ascii_range_end)

    # If no overlap exists, return a blank image
    if overlap_start > overlap_end:
        return mod_image

    # Step 4: Copy overlapping characters from `adjusted_image` to `mod_image`
    for ascii_code in range(overlap_start, overlap_end + 1):
        # Character's location in the current configuration
        char_x = (ascii_code - curr_ascii_start) % 16 * curr_config['font_width']
        char_y = (ascii_code - curr_ascii_start) // 16 * curr_config['font_height']
        char_crop_box = (char_x, char_y, char_x + curr_config['font_width'], char_y + curr_config['font_height'])
        char_img = adjusted_image.crop(char_crop_box)

        # Determine the position for the character in the modified image, with any offsets
        mod_char_x = (ascii_code - mod_ascii_range_start) % 16 * mod_config['font_width'] + mod_config['offset_left']
        mod_char_y = (ascii_code - mod_ascii_range_start) // 16 * mod_config['font_height'] + mod_config['offset_top']

        # Ensure we don’t paste out of bounds in `mod_image`
        mod_char_x = max(0, mod_char_x)
        mod_char_y = max(0, mod_char_y)

        # Paste character onto `mod_image` at the computed position
        mod_image.paste(char_img, (mod_char_x, mod_char_y))

    return mod_image
