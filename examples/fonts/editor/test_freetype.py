from AgonFont import read_freetype_font
from PIL import ImageFont

# Load a TrueType font with PIL.ImageFont
font_path = "/home/smith/Agon/mystuff/mac/ttf/Arial Black.ttf"
point_size = 32
font = ImageFont.truetype(font_path, size=point_size)

# Font configuration dictionary
font_config = {
    'point_size': 32,            # Size of the font in points
    'ascii_range_start': 32,      # Start of ASCII range to render
    'ascii_range_end': 127,       # End of ASCII range to render
    'raster_type': 'quantized', # Rendering type: 'thresholded', 'quantized', or 'palette'
    
    # Threshold settings (for 'thresholded' raster_type)
    'threshold': 128,             # Threshold value for binary conversion (0-255)

    # Quantization settings (for 'quantized' raster_type)
    # No additional config needed; uses default of 4 colors

    # Palette settings (for 'palette' raster_type)
    'fg_color': 255,              # Foreground color (usually white or a custom grayscale value)
    'bg_color': 0,                # Background color (usually black)

    # Configurations to be updated after rendering (automatically populated)
    'font_width': None,           # Calculated max width of rendered characters
    'font_height': None,          # Calculated max height of rendered characters
}


# Generate the font image using the FreeType-specific functions
font_config_out, font_img = read_freetype_font(font_path, font_config)  # Unpack the tuple
font_img.show()  # Now font_img is the image object, so this should work

