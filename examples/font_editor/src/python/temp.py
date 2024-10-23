def convert_font_to_txt(font_filepath):
    """
    Converts the binary data of a .font file to a .txt file.
    Each row in the text file will contain 16 bytes in hex format, separated by spaces.

    :param font_filepath: Path to the .font file
    """
    txt_filepath = font_filepath.replace('.font', '.txt')
    
    with open(font_filepath, 'rb') as f:
        font_data = f.read()
    
    with open(txt_filepath, 'w') as f:
        for i in range(0, len(font_data), 16):
            # Get 16 bytes from the data
            row_data = font_data[i:i + 16]
            # Convert each byte to 2-digit hex format with leading zeroes
            hex_row = ' '.join(f'{byte:02X}' for byte in row_data)
            # Write the row to the text file
            f.write(hex_row + '\n')

# Example usage
convert_font_to_txt('examples/font_editor/tgt/Arial Black_Regular_12x12.font')
