from PIL import Image, ImageDraw, ImageFont
import agonutils as au
import struct
import os
from config_manager import load_font_metadata_from_xml, save_font_metadata_to_xml, dict_to_text

# =============================================================================
# Master Font Functions
# =============================================================================

def read_font(file_path, font_config_input):
    """
    Entry point for reading and rendering fonts based on file type. Supports
    different formats like TTF, OTF, PSF, PNG, and custom font files.
    Applies position and size offsets, as well as scaling, to the final output.
    """
    # Determine the font type based on the file extension
    _, file_extension = os.path.splitext(file_path)
    file_extension = file_extension.lower()

    # Load the appropriate font object
    if file_extension in ['.ttf', '.otf']:  # TrueType or OpenType font
        font_config, font_image = read_ttf_font(file_path, font_config_input)
    elif file_extension == '.psf':
        font_config, font_image = read_psf_font(file_path, font_config_input)
    elif file_extension == '.png':
        font_config, font_image = read_png_font(file_path, font_config_input)
    elif file_extension == '.font':
        font_config_filepath = file_path + '.xml'
        if os.path.exists(font_config_filepath):
            font_config_input = load_font_metadata_from_xml(font_config_filepath)
        font_config, font_image = read_agon_font(file_path, font_config_input)
    elif file_extension == '.xml':
        font_config = load_font_metadata_from_xml(file_path)
        file_path = font_config.get('original_font_path', '')
        font_config, font_image = read_font(file_path, font_config)
    else:
        raise ValueError(f"Unsupported font file type: {file_extension}")

    font_config, font_image = resample_and_scale_image(font_config, font_image)
    return font_config, font_image

# =============================================================================
# Helper functions
# =============================================================================
def resample_and_scale_image(font_config, original_image):
    """
    Resample the original image to fit the modified configuration, handling
    position offsets once at the beginning, and applying scaling to each character individually.
    """
    # Extract relevant font configuration parameters
    orig_width = font_config['font_width']
    orig_height = font_config['font_height']
    offset_width = font_config['offset_width']
    offset_height = font_config['offset_height']
    scale_width = font_config['scale_width']
    scale_height = font_config['scale_height']
    chars_per_row = font_config['chars_per_row']
    ascii_start = font_config['ascii_start']
    ascii_end = font_config['ascii_end']

    # Calculate modified width and height, including offsets and scaling
    mod_width = orig_width + offset_width + scale_width
    mod_height = orig_height + offset_height + scale_height

    # Calculate the dimensions for the final image
    total_chars = ascii_end - ascii_start + 1
    rows = (total_chars + chars_per_row - 1) // chars_per_row  # Round up for rows
    new_image_width = chars_per_row * mod_width
    new_image_height = rows * mod_height

    # Create an adjusted image with position offsets applied
    bg_color = parse_rgba_color(font_config['bg_color'])
    src_image = Image.new("RGBA", original_image.size, bg_color)
    src_image.paste(original_image, (font_config['offset_left'], font_config['offset_top']))

    # Create a final image to hold the characters in a grid with modified dimensions
    font_image = Image.new("RGBA", (new_image_width, new_image_height), bg_color)

    # Collect, resample, and paste each character into the final image
    for ascii_code in range(ascii_start, ascii_end + 1):
        char_index = ascii_code - ascii_start
        tgt_x = (char_index % chars_per_row) * mod_width
        tgt_y = (char_index // chars_per_row) * mod_height
        
        # Crop the character image from the original image
        src_x = (char_index % chars_per_row) * orig_width
        src_y = (char_index // chars_per_row) * orig_height
        char_crop_box = (src_x, src_y, src_x + orig_width, src_y + orig_height)
        char_img = src_image.crop(char_crop_box)

        # Apply scaling to the character image
        if scale_width or scale_height:
            char_img = char_img.resize((orig_width + scale_width, orig_height + scale_height), Image.BICUBIC)

        # Paste the resampled character image into the final font image
        font_image.paste(char_img, (tgt_x, tgt_y))

    if font_config['raster_type'] == 'threshold':
        threshold = font_config['threshold']
        font_image = font_image.convert("L")
        font_image = apply_threshold(font_image, threshold)
        font_image = font_image.convert("RGBA")
    elif font_config['raster_type'] == 'palette':
        palette_fileame = f"colors/{font_config['palette']}.gpl"
        palette_filepath = os.path.join(os.path.dirname(__file__), palette_fileame)
        temp_img_filepath = os.path.join(os.path.dirname(__file__), 'temp.png')
        font_image.save(temp_img_filepath)
        au.convert_to_palette(temp_img_filepath, temp_img_filepath, palette_filepath, 'RGB')
        font_image = Image.open(temp_img_filepath)

    return font_config, font_image

def get_chars_from_image(font_config, font_image):
    """
    Extracts individual character images from a font image based on the font configuration.
    """
    # Extract relevant font configuration parameters
    font_width_mod = font_config['font_width_mod']
    font_height_mod = font_config['font_height_mod']
    chars_per_row = font_config['chars_per_row']
    ascii_start = font_config['ascii_start']
    ascii_end = font_config['ascii_end']

    # Crop the character images from the original image
    char_images = {}
    for ascii_code in range(ascii_start, ascii_end + 1):
        char_index = ascii_code - ascii_start
        src_x = (char_index % chars_per_row) * font_width_mod
        src_y = (char_index // chars_per_row) * font_height_mod
        char_crop_box = (src_x, src_y, src_x + font_width_mod, src_y + font_height_mod)
        char_image = font_image.crop(char_crop_box)
        char_images[ascii_code] = char_image

    return char_images

def parse_rgba_color(color_string):
    """
    Converts an RGBA color string to a tuple suitable for PIL, removing any extra whitespace.
    """
    try:
        rgba = tuple(int(part.strip()) for part in color_string.split(','))
        if len(rgba) == 4:
            return rgba
        else:
            raise ValueError("RGBA color string must have exactly four components.")
    except ValueError as e:
        print(f"Error parsing RGBA color: {e}")
        return (0, 0, 0, 255)  # Default to black, fully opaque
    
def rgba_to_hex(rgba):
    """Convert an RGBA tuple to a Tkinter-compatible hex color string (ignoring the alpha)."""
    return f"#{rgba[0]:02x}{rgba[1]:02x}{rgba[2]:02x}"

def hex_to_rgba(hex_color):
    """Convert a Tkinter-compatible hex color string to an RGBA tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4)) + (255,)

def create_blank_font_image(font_config):
    """
    Creates a blank PNG image with dimensions to fit all characters in the specified ASCII range.
    
    :param font_config: Dictionary with font configuration
    :return: A blank PIL Image object with the font dimensions to fit the ASCII range
    """
    font_width = font_config['font_width']
    font_height = font_config['font_height']
    ascii_start = font_config['ascii_start']
    ascii_end = font_config['ascii_end']
    bg_color = parse_rgba_color(font_config['bg_color'])
    
    # Calculate the number of characters and arrange them in a grid
    num_chars = ascii_end - ascii_start + 1
    chars_per_row = font_config['chars_per_row']
    num_rows = (num_chars + chars_per_row - 1) // chars_per_row

    # Determine the overall image dimensions
    image_width = chars_per_row * font_width
    image_height = num_rows * font_height
    
    return Image.new('RGBA', (image_width, image_height), bg_color)

def create_font_image(char_images, font_config):
    """
    Creates a PIL image from the dictionary of character images and arranges them in a grid.
    
    :param char_images: Dictionary of PIL Images representing each character, with ASCII codes as keys
    :param font_config: Dictionary with font configuration
    :return: A PIL Image object with all characters arranged in a grid
    """
    char_width = font_config['font_width']
    char_height = font_config['font_height']
    chars_per_row = font_config['chars_per_row']
    ascii_start = font_config['ascii_start']
    ascii_end = font_config['ascii_end']

    # Create an empty image to hold the font grid
    font_image = create_blank_font_image(font_config)
    
    # Paste each character into the final image
    for ascii_code in range(ascii_start, ascii_end + 1):
        if ascii_code in char_images:
            char_img = char_images[ascii_code]
            index = ascii_code - ascii_start
            x = (index % chars_per_row) * char_width
            y = (index // chars_per_row) * char_height
            font_image.paste(char_img, (x, y))
    
    return font_image

# =============================================================================
# FreeTypeFont Functions
# =============================================================================

def read_ttf_font(file_path, font_config_input):
    """
    Reads a TTF font and generates a dictionary of character images along with the font image.
    
    :param file_path: Path to the TTF font file
    :param font_config_input: Dictionary with initial font configuration
    :return: Updated font configuration and a PIL image representing the combined character set
    """
    font = ImageFont.truetype(file_path, font_config_input['point_size'])

    # Render TTF characters and get char_images as a dictionary
    char_images, max_width, max_height = render_ttf_chars(font, font_config_input)

    # Update the font configuration
    font_config = font_config_input.copy()
    font_config.update({
        'font_width': max_width,
        'font_height': max_height,
    })

    # Generate the master image from the dictionary of character images
    font_image = create_font_image(char_images, font_config)
    
    return font_config, font_image

def render_ttf_chars(font, font_config_input):
    """
    Render each character within the specified ASCII range and return images cropped to max dimensions.
    """
    char_images = {}
    max_width, max_height = 0, 0
    ascii_range = (font_config_input['ascii_start'], font_config_input['ascii_end'])
    
    # Parse colors from font_config_input
    bg_color = parse_rgba_color(font_config_input['bg_color'])
    fg_color = parse_rgba_color(font_config_input['fg_color'])

    # First Pass: Render each character on a transparent background and calculate max bounding box size
    for char_code in range(ascii_range[0], ascii_range[1] + 1):
        char = chr(char_code)
        # Create a transparent image for bounding box calculation
        char_img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))  # Fully transparent background
        draw = ImageDraw.Draw(char_img)
        draw.text((0, 0), char, font=font, fill=fg_color)

        # Calculate the bounding box for the character
        bbox = char_img.getbbox()
        
        if bbox:
            width, height = bbox[2], bbox[3]
            max_width = max(max_width, width)
            max_height = max(max_height, height)

        # Store the original unaltered image for the second pass
        char_images[char_code] = char_img

    # Second Pass: Crop each and scale image from the top-left corner to the max bounding box dimensions
    cropped_images = {}
    for char_code, char_img in char_images.items():
        # Crop to max bounding box dimensions from the top-left corner
        cropped_img = char_img.crop((0, 0, max_width, max_height))
        # Create a new image with bg_color and the max bounding box dimensions
        final_img = Image.new("RGBA", (max_width, max_height), bg_color)
        # Paste the cropped character into the background-colored image
        final_img.paste(cropped_img, (0, 0), cropped_img)
        cropped_images[char_code] = final_img

    return cropped_images, max_width, max_height

def apply_threshold(image, threshold):
    """Apply a threshold to a grayscale image to convert it to binary (black and white)."""
    return image.point(lambda p: 255 if p > threshold else 0, mode="1")

def quantize_image(image):
    """Quantize a grayscale image to a 4-level palette."""
    return image.quantize(colors=4)

# =============================================================================
# PSF Font Functions
# =============================================================================
# Constants for PSF1 and PSF2 Magic Numbers
PSF1_MAGIC = b'\x36\x04'
PSF2_MAGIC = b'\x72\xb5\x4a\x86'
PSF1_MODE512 = 1

def read_psf_font(file_path, font_config_input):
    """
    Detects the PSF version, reads the PSF font file, and returns standardized font config and font image.
    
    :param file_path: Path to the PSF font file
    :param font_config_input: Dictionary with initial font configuration
    :return: Updated font configuration and a PIL image representing the combined character set
    """
    psf_data = detect_and_read_psf(file_path)
    font_name = os.path.splitext(os.path.basename(file_path))[0]

    # Determine ASCII range from PSF data
    computed_ascii_start = 0
    computed_ascii_end = psf_data['num_glyphs'] - 1

    ascii_start = font_config_input.get('ascii_start', computed_ascii_start)
    ascii_end = font_config_input.get('ascii_end', computed_ascii_end)

    # Adjust ASCII range to ensure overlap with the computed range
    ascii_start = max(computed_ascii_start, min(ascii_start, computed_ascii_end))
    ascii_end = min(computed_ascii_end, max(ascii_end, computed_ascii_start))

    # Update font configuration
    font_config = font_config_input.copy()
    font_config.update({
        'font_name': font_name,
        'font_width': psf_data['width'],
        'font_height': psf_data['height'],
        'num_glyphs': psf_data['num_glyphs'],
        'ascii_start': ascii_start,
        'ascii_end': ascii_end
    })

    # Render PSF glyphs as a dictionary of character images
    char_images, max_width, max_height = render_psf_glyphs(psf_data, font_config)

    # Generate the master image from the dictionary of character images
    font_image = create_font_image(char_images, font_config)

    return font_config, font_image

def render_psf_glyphs(psf_data, font_config):
    """
    Renders each glyph from PSF font data as RGBA images, using specified foreground and background colors.
    Returns a dictionary of character images with ASCII codes as keys.
    
    :param psf_data: Dictionary containing PSF font data
    :param font_config: Dictionary with font configuration
    :return: Dictionary of character images, max width, and max height
    """
    char_images = {}
    max_width, max_height = psf_data['width'], psf_data['height']
    
    # Get foreground and background colors from the config
    fg_color = parse_rgba_color(font_config['fg_color'])
    bg_color = parse_rgba_color(font_config['bg_color'])

    ascii_start = font_config['ascii_start']
    ascii_end = font_config['ascii_end']

    for char_index in range(ascii_start, ascii_end + 1):
        glyph_data = psf_data['glyphs'][char_index]

        # Create a new RGBA image with the specified background color
        glyph_img = Image.new('RGBA', (max_width, max_height), bg_color)
        bytes_per_row = (max_width + 7) // 8

        for y in range(max_height):
            row_data = glyph_data[y * bytes_per_row:(y + 1) * bytes_per_row]
            for byte_index, byte in enumerate(row_data):
                for bit in range(8):
                    pixel_x = byte_index * 8 + bit
                    if pixel_x < max_width and (byte & (0x80 >> bit)):
                        glyph_img.putpixel((pixel_x, y), fg_color)

        # Store the image in the dictionary with the ASCII code as the key
        char_images[char_index] = glyph_img

    return char_images, max_width, max_height

def detect_and_read_psf(file_path):
    """
    Helper function to detect the PSF version and read the corresponding PSF font data.
    """
    with open(file_path, 'rb') as f:
        magic = f.read(4)

    if magic[:2] == PSF1_MAGIC:
        return read_psf1(file_path)
    elif magic == PSF2_MAGIC:
        return read_psf2(file_path)
    else:
        raise ValueError(f"Not a valid PSF file: {file_path}")

def read_psf1(file_path):
    """
    Reads a PSF1 font file and returns glyph bitmaps and standardized metadata.
    """
    with open(file_path, 'rb') as f:
        magic, mode, charsize = struct.unpack('2sBB', f.read(4))

        if magic != PSF1_MAGIC:
            raise ValueError(f"Not a valid PSF1 file: {file_path}")

        num_glyphs = 512 if mode & PSF1_MODE512 else 256
        glyphs = [f.read(charsize) for _ in range(num_glyphs)]

        return {
            'glyphs': glyphs,
            'num_glyphs': num_glyphs,
            'height': charsize,
            'width': 8,  # PSF1 glyphs have a fixed width of 8 pixels
            'variant': 'PSF1'
        }

def read_psf2(file_path):
    """
    Reads a PSF2 font file and returns glyph bitmaps and standardized metadata.
    """
    with open(file_path, 'rb') as f:
        header = f.read(32)
        magic, version, header_size, flags, num_glyphs, glyph_size, height, width = struct.unpack('Iiiiiiii', header[:32])

        if magic != 0x864ab572:
            raise ValueError(f"Not a valid PSF2 file: {file_path}")

        glyphs = [f.read(glyph_size) for _ in range(num_glyphs)]
        unicode_table = extract_unicode_table(f) if flags & 0x01 else {}

        return {
            'glyphs': glyphs,
            'num_glyphs': num_glyphs,
            'glyph_size': glyph_size,
            'height': height,
            'width': width,
            'unicode_table': unicode_table,
            'variant': 'PSF2'
        }

def extract_unicode_table(file_obj):
    """
    Extracts the Unicode table from a PSF2 file if present.
    """
    unicode_table = {}
    while True:
        byte = file_obj.read(1)
        if not byte or byte == b'\xFF':
            break
        glyph_index = struct.unpack('B', byte)[0]
        unicodes = []

        while True:
            codepoint_data = file_obj.read(2)
            if len(codepoint_data) < 2:
                break
            codepoint = struct.unpack('H', codepoint_data)[0]
            if codepoint == 0xFFFF:
                break
            unicodes.append(codepoint)

        unicode_table[glyph_index] = unicodes

    return unicode_table

# =============================================================================
# Open PNG Font
# =============================================================================

def read_png_font(file_path, font_config):
    """
    Opens a PNG image as a font and returns the rendered image.
    """
    font_image = Image.open(file_path)

    # Update font configuration based on the PNG image size
    font_config['font_width'] = font_image.width // font_config['chars_per_row']
    font_config['font_height'] = font_image.height // (
        (font_config['ascii_end'] - font_config['ascii_start'] + 1) // font_config['chars_per_row']
    )

    return font_config, font_image

# =============================================================================
# Agon .font File Functions
# -----------------------------------------------------------------------------
# Read .font File Functions
# -----------------------------------------------------------------------------
def read_agon_font(font_filepath, font_config):
    """
    Reads a .font file and returns a dictionary of character images.
    Each byte in the file represents 8 horizontal pixels.
    
    :param font_filepath: Path to the .font file
    :param font_config: Dictionary with font configuration
    :return: Updated font_config and a PIL image representing the combined character set
    """
    char_width = font_config['font_width_mod']
    char_height = font_config['font_height_mod']
    ascii_start = font_config['ascii_start']
    ascii_end = font_config['ascii_end']
    num_chars = ascii_end - ascii_start + 1
    
    # Round the true width up to the nearest multiple of 8 (padded width)
    padded_width = pad_to_byte(char_width)
    bytes_per_row = padded_width // 8  # Number of bytes per row of the character
    bytes_per_character = bytes_per_row * char_height

    # Calculate the starting byte offset for the specified ASCII range
    start_offset = ascii_start * bytes_per_character

    char_images = {}

    # Read the font data starting from the calculated offset
    with open(font_filepath, 'rb') as f:
        f.seek(start_offset)  # Move to the starting position in the file
        font_data = f.read(num_chars * bytes_per_character)

    # Iterate over the specified ASCII range
    for ascii_code in range(ascii_start, ascii_end + 1):
        i = ascii_code - ascii_start  # Adjust index based on ASCII start
        
        # Create an image for each character with the padded width
        char_img = Image.new('L', (padded_width, char_height), color=0)
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

        # Store the character image in the dictionary with ASCII code as the key
        char_images[ascii_code] = char_img

    # char_images[ord('A')].show()

    font_config_temp = font_config.copy()
    font_config_temp.update({
        'font_width': char_width,
        'font_height': char_height,
    })
    font_image = create_font_image(char_images, font_config_temp)
    return font_config, font_image

# -----------------------------------------------------------------------------
# Write .font File Functions
# -----------------------------------------------------------------------------

def write_agon_font(font_config, font_image, tgt_font_filepath):
    # font_image.show()
    """
    Writes a .font file based on the provided font image and configuration.
    
    :param font_config: Dictionary with font configuration
    :param font_image: PIL image containing all character images
    :param tgt_font_filepath: Target path for the output .font file
    """
    # Extract font dimensions and padding
    font_width_mod = font_config['font_width_mod']
    font_height_mod = font_config['font_height_mod']
    font_width_padded = pad_to_byte(font_width_mod)
    ascii_start = font_config['ascii_start']
    ascii_end = font_config['ascii_end']

    # Extract individual character images from the font image
    char_images = get_chars_from_image(font_config, font_image)

    # Apply threshold to each character image within the ASCII range
    threshold = font_config['threshold']

    for ascii_code in range(ascii_start, ascii_end + 1):
        char_image = char_images.get(ascii_code)
        if char_image:
            # Convert the image to grayscale
            gray_image = char_image.convert('L')
            
            # Apply thresholding to the grayscale image
            thresholded_image = gray_image.point(lambda p: 255 if p > threshold else 0)
            
            # Create a new PIL image with the padded width
            padded_image = Image.new('L', (font_width_padded, font_height_mod), 0)

            # Paste the thresholded image into the padded image
            padded_image.paste(thresholded_image, (0, 0))

            # Update the processed image in the dictionary
            char_images[ascii_code] = padded_image

    # Prepare blank data for characters outside the ASCII range
    blank_image = Image.new('L', (font_width_padded, font_height_mod), 0)
    blank_data = image_to_bitstream(blank_image)

    # Write the processed font data to a new .font file
    font_data = bytearray()

    for ascii_code in range(256):
        if ascii_code < ascii_start or ascii_code > ascii_end:
            # Use pre-generated blank data for characters outside the range
            font_data.extend(blank_data)
        else:
            char_data = image_to_bitstream(char_images[ascii_code])
            font_data.extend(char_data)

    with open(tgt_font_filepath, 'wb') as f:
        f.write(font_data)

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

def byteify(pixels):
    """ Converts a list of 8 pixels (0 or 255) to a single byte. """
    byte = 0
    for i, pixel in enumerate(pixels):
        if pixel == 255:  # White pixel
            byte |= (1 << (7 - i))  # Set the corresponding bit for the white pixel
    return byte

def pad_to_byte(value):
    """Rounds up the given value to the nearest multiple of 8."""
    return (value + 7) // 8 * 8

def bin_to_text(filepath, hexdump=False):
    """
    Converts the binary data of a file to a .txt file.
    Each row in the text file will contain 16 bytes in hex format, separated by spaces.
    If hexdump is True, ASCII representation of the binary data is also added to the right side.

    :param filepath: Path to the binary file
    :param hexdump: Boolean indicating whether to include ASCII representation (default: False)
    """
    # Append .txt to the original filename to create the output filepath
    txt_filepath = f"{filepath}.txt"
    
    with open(filepath, 'rb') as f:
        binary_data = f.read()
    
    with open(txt_filepath, 'w') as f:
        for i in range(0, len(binary_data), 16):
            # Get 16 bytes from the data
            row_data = binary_data[i:i + 16]
            # Convert each byte to 2-digit hex format with leading zeroes
            hex_row = ' '.join(f'{byte:02X}' for byte in row_data)

            if hexdump:
                # Create ASCII representation (printable characters or dot)
                ascii_row = ''.join(chr(byte) if 32 <= byte <= 126 else '.' for byte in row_data)
                # Add ASCII representation to the right side
                output_row = f"{hex_row:<48}  |{ascii_row}|"
            else:
                output_row = hex_row

            # Write the row to the text file
            f.write(output_row + '\n')

if __name__ == '__main__':
    font_source_dir = 'examples/font_editor/tgt'
    font_filename = 'Arial Black_Regular_12x12.xml'
    font_filepath = os.path.join(font_source_dir, font_filename)
    
    # Load the font configuration from XML
    font_config = load_font_metadata_from_xml(font_filepath)
    file_path = font_config.get('original_font_path', '')
    file_name = os.path.basename(file_path)
    target_font_file_name = font_filename.replace('.xml', '.font')
    tgt_font_filepath = os.path.join(font_source_dir, target_font_file_name)
    tgt_font_config_filepath = f'{tgt_font_filepath}.xml'

    # Read the TTF font and generate char_images as a dictionary
    font = ImageFont.truetype(file_path, font_config['point_size'])
    char_images, max_width, max_height = render_ttf_chars(font, font_config)

    # Update the font configuration
    font_config.update({
        'font_width': max_width,
        'font_height': max_height,
    })

    # Generate the master image from the dictionary of character images
    font_image = create_font_image(char_images, font_config)
    font_config, font_image = resample_and_scale_image(font_config, font_image)

    # Update font_config with the modified dimensions
    font_config.update({
        'font_width': font_config['font_width_mod'],
        'font_height': font_config['font_height_mod'],
        'offset_left': 0,
        'offset_top': 0,
        'offset_width': 0,
        'offset_height': 0,
        'scale_width': 0,
        'scale_height': 0,
        'raster_type': 'threshold',
        'fg_color': '255, 255, 255, 255',
        'bg_color': '0, 0, 0, 255',
    })
    # Write the .font file and the corresponding XML metadata file
    write_agon_font(font_config, font_image, tgt_font_filepath)
    save_font_metadata_to_xml(font_config, tgt_font_config_filepath)

    # Read the .font file back to verify
    font_config, font_image = read_agon_font(tgt_font_filepath, font_config)

    # Convert the font data to text for inspection
    font_config_text = dict_to_text(font_config)
    print(font_config_text)

    # # Generate a hex dump of the written .font file
    # bin_to_text(tgt_font_filepath, hexdump=True)
