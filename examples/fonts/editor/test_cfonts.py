from AgonFont import read_psf_font, generate_psf_font_image

# Example font configuration dictionary
font_config = {
    'ascii_range_start': 0,      # Start of ASCII range (for PSF, usually 0)
    'ascii_range_end': 255,      # End of ASCII range
    'raster_type': 'thresholded' # Optional rasterization type if needed
}

# Path to the PSF font file (PSF1 or PSF2)
psf_file_path = '/home/smith/Agon/mystuff/agon-utils/examples/fonts/src/fonts/cfonts/Lat2-VGA16.psf'

# Read the PSF font and retrieve metadata and glyphs
psf_data = read_psf_font(psf_file_path, font_config)

# Generate a master image of all glyphs in a grid
master_font_image = generate_psf_font_image(psf_data, font_config, chars_per_row=16)

# Optional: Display or save the master font image
master_font_image.show()  # Show the master font image in a viewer

# Font metadata (similar structure to TrueType metadata)
font_metadata = {
    'font_width': psf_data['width'],
    'font_height': psf_data['height'],
    'num_glyphs': psf_data['num_glyphs'],
    'glyph_size': psf_data.get('glyph_size', None),
    'unicode_table': psf_data.get('unicode_table', {})
}

# Example: Print out font metadata
print(font_metadata)
