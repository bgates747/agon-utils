from PIL import Image, ImageDraw, ImageFont
import math
import struct
import os

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

def create_blank_font_image(font_config):
    """
    Creates a blank PNG image with dimensions to fit all characters in the specified ASCII range.
    
    :param font_config: Dictionary with font configuration
    :return: A blank PIL Image object with the font dimensions to fit the ASCII range
    """
    font_width = font_config['font_width']
    font_height = font_config['font_height']
    ascii_start = font_config.get('ascii_range_start', 32)
    ascii_end = font_config.get('ascii_range_end', 127)
    
    # Calculate the number of characters and arrange them in a grid with 16 characters per row
    num_chars = ascii_end - ascii_start + 1
    chars_per_row = 16
    num_rows = (num_chars + chars_per_row - 1) // chars_per_row  # Round up to account for partial rows

    # Determine the overall image dimensions
    image_width = chars_per_row * font_width
    image_height = num_rows * font_height
    
    return Image.new('L', (image_width, image_height), color=0)


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
    # Step 1: Apply offsets by directly pasting onto `adjusted_image`
    adjusted_image = Image.new("L", original_image.size, color=0)
    adjusted_image.paste(original_image, (mod_config['offset_left'], mod_config['offset_top']))

    # Step 2: Determine the overlap of ASCII ranges
    curr_ascii_start = curr_config['ascii_range_start']
    curr_ascii_end = curr_config['ascii_range_end']
    mod_ascii_start = mod_config['ascii_range_start']
    mod_ascii_end = mod_config['ascii_range_end']
    overlap_start = max(curr_ascii_start, mod_ascii_start)
    overlap_end = min(curr_ascii_end, mod_ascii_end)

    # If no overlap exists, return a blank modified image
    if overlap_start > overlap_end:
        return create_blank_font_image(mod_config)

    # Step 3: Collect character images from `adjusted_image` within the overlapping ASCII range
    char_images = []
    for ascii_code in range(overlap_start, overlap_end + 1):
        # Determine character's position in `adjusted_image`
        char_x = (ascii_code - curr_ascii_start) % 16 * curr_config['font_width']
        char_y = (ascii_code - curr_ascii_start) // 16 * curr_config['font_height']
        char_crop_box = (char_x, char_y, char_x + curr_config['font_width'], char_y + curr_config['font_height'])
        char_img = adjusted_image.crop(char_crop_box)
        char_images.append(char_img)

    # Step 4: Use `create_font_image` to arrange the characters in a grid with modified configuration
    return create_font_image(char_images, mod_config)

# =============================================================================
# FreeTypeFont Functions
# =============================================================================

def generate_font_image(font, font_config_input):
    char_images, max_width, max_height = render_characters(font, font_config_input)
    
    # Check the raster_type directly
    raster_type = font_config_input.get('raster_type', 'thresholded')
    if raster_type == 'thresholded':
        threshold = font_config_input.get('threshold', 128)
        char_images = [apply_threshold(img, threshold) for img in char_images.values()]
    elif raster_type == 'quantized':
        char_images = [quantize_image(img) for img in char_images.values()]
    elif raster_type == 'palette':
        fg_color = font_config_input.get('fg_color', 255)
        bg_color = font_config_input.get('bg_color', 0)
        # TODO: Implement palette rendering
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
    ascii_range = (font_config_input.get('ascii_range_start', 32), font_config_input.get('ascii_range_end', 127))

    # First Pass: Render each character and calculate max width and height without altering the original images
    for char_code in range(ascii_range[0], ascii_range[1] + 1):
        char = chr(char_code)
        char_img = Image.new("L", (64, 64), color=0)  # Black background
        draw = ImageDraw.Draw(char_img)
        draw.text((0, 0), char, font=font, fill=255)  # White character
        bbox = char_img.getbbox()

        if bbox:
            width, height = bbox[2], bbox[3]
            max_width = max(max_width, width)
            max_height = max(max_height, height)

        # Store the original unaltered image for the second pass
        char_images[char_code] = char_img

    # Second Pass: Crop each image to max width and height determined from the first pass
    cropped_images = {}
    for char_code, char_img in char_images.items():
        cropped_img = char_img.crop((0, 0, max_width, max_height))
        cropped_images[char_code] = cropped_img

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

# PSF1 and PSF2 magic numbers
PSF1_MAGIC = b'\x36\x04'
PSF2_MAGIC = b'\x72\xb5\x4a\x86'
PSF1_MODE512 = 1

def read_psf_font(file_path, font_config_input):
    """Detects PSF version, reads the PSF font file, and returns font config and font image."""
    with open(file_path, 'rb') as f:
        magic = f.read(4)
        
        # Read the appropriate PSF file type and get glyph data
        if magic[:2] == PSF1_MAGIC:
            psf_data = read_psf1(file_path)
        elif magic == PSF2_MAGIC:
            psf_data = read_psf2(file_path)
        else:
            raise ValueError(f"Not a valid PSF1 or PSF2 file: {file_path}")

    # Set up the font configuration based on the provided font_config_input and PSF data
    font_config = font_config_input.copy()
    font_config.update({
        'font_width': psf_data['width'],
        'font_height': psf_data['height'],
        'num_glyphs': psf_data['num_glyphs']
    })

    # Generate the master font image from glyph images
    font_image = generate_psf_font_image(psf_data, font_config, chars_per_row=16)
    
    return font_config, font_image

def render_psf_glyphs(psf_data):
    """
    Render each glyph from PSF font data as images and return images and max dimensions.
    """
    glyph_images = []
    max_width = psf_data['width']
    max_height = psf_data['height']

    for glyph_data in psf_data['glyphs']:
        glyph_img = Image.new('1', (max_width, max_height), color=0)  # Black background
        bytes_per_row = (max_width + 7) // 8
        
        for y in range(max_height):
            row_data = glyph_data[y * bytes_per_row:(y + 1) * bytes_per_row]
            for byte_index, byte in enumerate(row_data):
                for bit in range(8):
                    pixel_x = byte_index * 8 + bit
                    if pixel_x < max_width and (byte & (0x80 >> bit)):
                        glyph_img.putpixel((pixel_x, y), 1)  # White pixel
        
        glyph_images.append(glyph_img)
    
    return glyph_images, max_width, max_height

def generate_psf_font_image(psf_data, font_config, chars_per_row=16):
    """
    Generate a master image from PSF glyph images in a grid.
    """
    glyph_images, max_width, max_height = render_psf_glyphs(psf_data)
    num_glyphs = len(glyph_images)
    rows = (num_glyphs + chars_per_row - 1) // chars_per_row
    font_image = Image.new('1', (chars_per_row * max_width, rows * max_height), color=1)  # White background

    for i, glyph_img in enumerate(glyph_images):
        x = (i % chars_per_row) * max_width
        y = (i // chars_per_row) * max_height
        font_image.paste(glyph_img, (x, y))
    
    return font_image

def read_psf1(file_path):
    """Reads a PSF1 font file and returns glyph bitmaps and metadata."""
    with open(file_path, 'rb') as f:
        magic, mode, charsize = struct.unpack('2sBB', f.read(4))
        if magic != PSF1_MAGIC:
            raise ValueError(f"Not a valid PSF1 file: {file_path}")
        
        num_glyphs = 512 if mode & PSF1_MODE512 else 256
        glyphs = [f.read(charsize) for _ in range(num_glyphs)]
        
        return {
            'glyphs': glyphs,
            'num_glyphs': num_glyphs,
            'charsize': charsize,
            'height': charsize,
            'width': 8
        }
    
def read_psf2(file_path):
    """Reads a PSF2 font file and returns glyph bitmaps and metadata."""
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
            'unicode_table': unicode_table
        }

def extract_unicode_table(file_obj):
    """Extracts the Unicode table from a PSF2 file if present."""
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
# PNG Font Functions
# =============================================================================

def open_png_image(file_path, font_config):
    font_image = Image.open(file_path)
    return font_config, font_image

# =============================================================================
# Agon .font File Functions
# =============================================================================

def open_font_file(file_path, font_config):
    char_images = read_font_file(file_path, font_config)
    font_image = create_font_image(char_images, font_config)
    return font_config, font_image

# =============================================================================
# Master Font Functions
# =============================================================================

def read_font(file_path, font_config_input):
    # Determine the font type based on the file extension
    _, file_extension = os.path.splitext(file_path)
    point_size = font_config_input.get('point_size', 16)

    # Load the appropriate font object
    if file_extension.lower() in ['.ttf', '.otf']:  # TrueType or OpenType font
        font = ImageFont.truetype(file_path, point_size)
        font_config, font_image = generate_font_image(font, font_config_input)
    elif file_extension.lower() == '.ttc':  # TrueType Collection
        # In case of font collections, use index for specific font face if needed
        font_index = font_config_input.get('font_index', 0)
        font = ImageFont.truetype(file_path, point_size, index=font_index)
        font_config, font_image = generate_font_image(font, font_config_input)
    elif file_extension == '.psf':
        font_config, font_image = read_psf_font(file_path, font_config_input)
    elif file_extension == '.png':
        font_config, font_image = open_png_image(file_path, font_config)
    elif file_extension == '.font':
        font_config, font_image = open_font_file(file_path, font_config)
    else:
        raise ValueError(f"Unsupported font file type: {file_extension}")

    # Generate font image and configuration metadata
    return font_config, font_image