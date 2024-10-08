
import os
from PIL import Image

def round_up_to_multiple_of_8(value):
    """Rounds up the given value to the nearest multiple of 8."""
    return (value + 7) // 8 * 8

def byteify(pixels):
    """ Converts a list of 8 pixels (0 or 255) to a single byte. """
    byte = 0
    for i in range(len(pixels)):
        if pixels[i] == 255:  # White pixel
            byte |= (1 << (7 - i))  # Set the corresponding bit for the white pixel
    return byte

def read_font_file(font_filepath, char_width, char_height, num_chars=256):
    """
    Reads a .font file and returns a list of character images.
    Each byte in the file represents 8 horizontal pixels.
    
    :param font_filepath: Path to the .font file
    :param char_width: True width of each character in pixels
    :param char_height: Height of each character in pixels
    :param num_chars: Total number of characters in the font file (default: 256)
    :return: A list of PIL images representing each character
    """
    # Round the true width up to the nearest multiple of 8 (padded width)
    padded_width = round_up_to_multiple_of_8(char_width)

    with open(font_filepath, 'rb') as f:
        font_data = f.read()

    char_images = []
    bytes_per_row = padded_width // 8  # Number of bytes per row of the character

    for i in range(num_chars):
        # Now, we use the padded width to create the image, not the true width
        char_img = Image.new('L', (padded_width, char_height), color=0)  # 'L' mode for grayscale (1 byte per pixel)
        pixels = char_img.load()
        
        # Extract character data from the font file
        for y in range(char_height):
            row_byte_start = i * char_height * bytes_per_row + y * bytes_per_row
            row_data = font_data[row_byte_start:row_byte_start + bytes_per_row]
            
            for byte_idx, byte in enumerate(row_data):
                for bit in range(8):
                    x = byte_idx * 8 + bit
                    if x < padded_width:  # Render the padded width (including the padded bits)
                        if byte & (1 << (7 - bit)):
                            pixels[x, y] = 255  # Set pixel to white (255) if the bit is set

        char_images.append(char_img)

    return char_images

def create_font_image(char_images, padded_width, char_height, chars_per_row=16):
    """
    Creates a PNG image from the list of character images and arranges them in a grid.
    
    :param char_images: List of PIL Images representing each character
    :param padded_width: Padded width of each character (nearest multiple of 8)
    :param char_height: Height of each character
    :param chars_per_row: Number of characters per row in the final image
    :return: A PIL Image object with all characters arranged in a grid
    """
    num_chars = len(char_images)
    rows = (num_chars + chars_per_row - 1) // chars_per_row
    
    # Create an empty image to hold the font grid
    font_img = Image.new('L', (chars_per_row * padded_width, rows * char_height), color=0)
    
    # Paste each character into the final image
    for i, char_img in enumerate(char_images):
        x = (i % chars_per_row) * padded_width
        y = (i // chars_per_row) * char_height
        font_img.paste(char_img, (x, y))
    
    return font_img

def display_font_image(font_img):
    """ Displays the final font image. """
    font_img.show()

if __name__ == "__main__":
    font_filepath = 'examples/fonts/tgt/ttf/8_bit_fortress_Regular_9x8.font'
    char_width = 9  # True character width
    char_height = 8  # Character height
    
    # Round up the width to the nearest multiple of 8 for rendering
    padded_width = round_up_to_multiple_of_8(char_width)
    
    # Read the .font file and get individual character images (padded width for rendering)
    char_images = read_font_file(font_filepath, char_width, char_height)
    
    # Create a single PNG image of the font with padded width
    # font_img = create_font_image(char_images, padded_width, char_height)
    font_img = create_font_image(char_images, char_width, char_height)
    
    # Display the PNG image
    display_font_image(font_img)