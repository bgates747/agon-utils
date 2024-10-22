from PIL import Image, ImageDraw, ImageFont
import math
import struct
import os
from config_manager import load_font_metadata_from_xml

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
        font = ImageFont.truetype(file_path, font_config_input['point_size'])
        font_config, font_image = generate_font_image(font, font_config_input)
    elif file_extension == '.psf':
        font_config, font_image = read_psf_font(file_path, font_config_input)
    elif file_extension == '.png':
        font_config, font_image = open_png_image(file_path, font_config_input)
    elif file_extension == '.font':
        font_config, font_image = open_font_file(file_path, font_config_input)
    elif file_extension == '.xml':
        font_config = load_font_metadata_from_xml(file_path)
        file_path = font_config.get('original_font_path', '')
        font_config, font_image = read_font(file_path, font_config)
    else:
        raise ValueError(f"Unsupported font file type: {file_extension}")

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

    return font_image

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
    ascii_range = (font_config['ascii_start'], font_config['ascii_end'])
    
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
        char_img = Image.new('RGBA', (padded_width, char_height), color=(0,0,0,0))
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
    Creates a PNG image from the list of character images and arranges them in a grid.
    
    :param char_images: List of PIL Images representing each character
    :param font_config: Dictionary with font configuration
    :return: A PIL Image object with all characters arranged in a grid
    """
    char_width = font_config['font_width']
    char_height = font_config['font_height']
    chars_per_row = font_config['chars_per_row']
    
    # Create an empty image to hold the font grid
    font_image = create_blank_font_image(font_config)
    
    # Paste each character into the final image
    for i, char_img in enumerate(char_images):
        x = (i % chars_per_row) * char_width
        y = (i // chars_per_row) * char_height
        font_image.paste(char_img, (x, y))
    
    return font_image

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
    ascii_range = (font_config['ascii_start'], font_config['ascii_end'])
    chars_per_row = font_config['chars_per_row']
    bg_color = parse_rgba_color(font_config['bg_color'])
    num_rows = math.ceil(256 / chars_per_row)
    
    font_width_mod = font_width + offset_width
    font_height_mod = font_height + offset_height
    font_width_padded = math.ceil(font_width_mod / 8) * 8
    sample_width = font_width if offset_width >= 0 else font_width_mod
    sample_height = font_height if offset_height >= 0 else font_height

    # Create a new source image the size of a full 256 character grid
    src_img_new = Image.new('RGBA', (font_width * chars_per_row, font_height * num_rows), bg_color)

    # Paste the cropped image into the correct position in the new source image
    src_img_new.paste(src_img, (0, (ascii_range[0] // chars_per_row) * font_height))

    # Return necessary values
    return font_width_padded, font_height_mod, sample_width, sample_height, src_img_new

def sample_char_image(ascii_code, font_config, src_img_new):
    font_width = font_config['font_width']
    font_height = font_config['font_height']
    sample_width = font_config['font_width']
    sample_height = font_config['font_height']

    # Calculate the character's x and y coordinates in the grid
    chars_per_row = font_config['chars_per_row']
    tgt_x = (ascii_code % chars_per_row) * font_width
    tgt_y = (ascii_code // chars_per_row) * font_height

    # Calculate the cropping box for the character
    crop_box = (tgt_x, tgt_y, tgt_x + sample_width, tgt_y + sample_height)

    # Crop and return the character image
    char_img = src_img_new.crop(crop_box)

    return char_img

def make_font(font_config, src_image, tgt_font_filepath):
    bg_color = parse_rgba_color(font_config['bg_color'])
    # Precompute offsets and image
    font_width_padded, font_height_mod, sample_width, sample_height, src_img_new = precomputations(font_config, src_image)

    font_data = bytearray()

    for ascii_code in range(0, 256):
        char_img = Image.new('RGBA', (font_width_padded, font_height_mod), bg_color)
        char_img.paste(sample_char_image(ascii_code, font_config, src_img_new), (font_config['offset_left'], font_config['offset_top']))
        font_data.extend(image_to_bitstream(char_img))

    with open(tgt_font_filepath, 'wb') as f:
        f.write(font_data)

# =============================================================================
# FreeTypeFont Functions
# =============================================================================
def generate_font_image(font, font_config_input):
    char_images, max_width, max_height = render_characters(font, font_config_input)
    
    # Check the raster_type directly
    raster_type = font_config_input['raster_type']
    if raster_type == 'thresholded':
        threshold = font_config_input['threshold']
        char_images = [apply_threshold(img, threshold) for img in char_images.values()]
    elif raster_type == 'quantized':
        char_images = [quantize_image(img) for img in char_images.values()]
    elif raster_type == 'palette':
        char_images = list(char_images.values())
    else:
        char_images = list(char_images.values())

    # Update the font configuration
    font_config = font_config_input.copy()
    font_config.update({
        'font_width': max_width,
        'font_height': max_height,
    })

    # Generate the master image
    font_image = create_font_image(char_images, font_config)
    
    return font_config, font_image

def render_characters(font, font_config_input):
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

def apply_threshold(image, threshold=128):
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
        'font_variant': psf_data['variant'],
        'font_width': psf_data['width'],
        'font_height': psf_data['height'],
        'num_glyphs': psf_data['num_glyphs'],
        'ascii_start': ascii_start,
        'ascii_end': ascii_end
    })

    # Generate the master font image from the glyph images
    font_image = generate_psf_font_image(psf_data, font_config)

    return font_config, font_image

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

def generate_psf_font_image(psf_data, font_config):
    """
    Generates a master image from PSF glyph images arranged in a grid.
    """
    glyph_images, max_width, max_height = render_psf_glyphs(psf_data, font_config)
    num_glyphs = len(glyph_images)
    chars_per_row = font_config['chars_per_row']
    bg_color = parse_rgba_color(font_config['bg_color'])
    rows = (num_glyphs + chars_per_row - 1) // chars_per_row

    font_image = Image.new('RGBA', (chars_per_row * max_width, rows * max_height), bg_color)

    for i, glyph_img in enumerate(glyph_images):
        x = (i % chars_per_row) * max_width
        y = (i // chars_per_row) * max_height
        font_image.paste(glyph_img, (x, y))

    return font_image

def render_psf_glyphs(psf_data, font_config):
    """
    Renders each glyph from PSF font data as images, returning the images and dimensions.
    """
    glyph_images = []
    max_width, max_height = psf_data['width'], psf_data['height']
    
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
        
        glyph_images.append(glyph_img)

    return glyph_images, max_width, max_height

# =============================================================================
# Open PNG Font
# =============================================================================

def open_png_image(file_path, font_config):
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
# =============================================================================

def open_font_file(file_path, font_config):
    char_images = read_font_file(file_path, font_config)
    font_image = create_font_image(char_images, font_config)
    return font_config, font_image