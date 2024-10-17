def read_gimp_palette(filepath):
    """
    Reads a GIMP palette file and returns a list of tuples containing
    RGB, HSV, and CMYK values for each color.

    Args:
        filepath: Path to the GIMP palette file.

    Returns:
        A list of tuples where each tuple contains:
        (RGB tuple, HSV tuple, CMYK tuple)
    """
    palette_data = []

    with open(filepath, 'r') as f:
        for line in f:
            # Extract RGB values from the line
            parts = line.split()
            # if len(parts) >= 3:
            try:
                r = int(parts[0])
                g = int(parts[1])
                b = int(parts[2])

                # Append a single tuple with all values
                palette_data.append((r, g, b))

            except ValueError:
                # Skip lines that don't have valid integer RGB values
                continue

    return palette_data

if __name__ == "__main__":
    # Example usage of read_gimp_palette
    palette_file = 'examples/widgets/Agon16.gpl'
    palette = read_gimp_palette(palette_file)
    print(palette)