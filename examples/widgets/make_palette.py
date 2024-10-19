
import csv
import agonutils as au
import math
from PIL import Image, ImageDraw

def generate_normalized_quanta(val0, val1, num_quanta):
    """
    Generates a normalized list of values between val0 and val1 with the specified number of quanta.
    If val0 > val1, the function will step through the range in descending order.

    Args:
        val0 (float): The starting value of the range.
        val1 (float): The ending value of the range.
        quanta (int): The number of quanta or steps between val0 and val1.

    Returns:
        List[float]: A list of normalized values between val0 and val1.
    """
    if num_quanta < 2:
        raise ValueError("Number of quanta must be at least 2 to generate a range.")
    
    step = (val1 - val0) / (num_quanta - 1)  # Calculate step size

    return [(val0 + i * step) for i in range(num_quanta)]

def quantize_value(value, quanta):
    """
    Quantizes a value to the nearest quanta value.

    Args:
        value (float): The value to quantize.
        quanta (List[float]): A list of quantized values.

    Returns:
        float: The quantized value from the quanta list.
    """
    return min(quanta, key=lambda x: abs(x - value))

# Define index values for sorting keys
R, G, B, H, S, V, C, M, Y, K = range(10)

def sort_colors_by(data, sort_order):
    """Sort color data. If data contains RGB-only tuples, extend them to include HSV and CMYK."""
    extended_data = []

    for item in data:
        if len(item) == 3:  # Check if item is an RGB tuple
            r, g, b = item
            # Convert RGB to HSV and CMYK using the C library functions
            h, s, v = au.rgb_to_hsv(r, g, b)
            c, m, y, k = au.rgb_to_cmyk(r, g, b)
            # Append extended tuple (R, G, B, H, S, V, C, M, Y, K)
            extended_data.append((r, g, b, h, s, v, c, m, y, k))
        else:
            # Item is already in the extended form
            extended_data.append(item)

    # Sort based on the sort_order provided
    return sorted(extended_data, key=lambda x: tuple(x[index] for index in sort_order))

def generate_gimp_palette(rgb_data, palette_filepath, palette_name, num_columns, named_colors_csv=None):
    """
    Generate a GIMP palette file from given RGB data.
    
    Args:
        rgb_data: List of color data, where each color is represented as (R, G, B, ...).
                  The function only uses the first three values (R, G, B).
        palette_filepath: Filepath where the palette will be saved.
        palette_name: Name of the palette to use in the GIMP file.
        num_columns: Number of columns to specify in the GIMP palette.
        named_colors_csv: Optional. If provided, the palette will be annotated with the nearest named colors.
    """

    # Create the GIMP palette header line by line
    palette = []
    palette.append("GIMP Palette\n")
    palette.append(f"Name: {palette_name}\n")
    palette.append(f"Columns: {num_columns}\n")
    palette.append("#\n")

    # If named colors CSV is provided, load it into a Palette object in C
    if named_colors_csv:
        named_palette = au.csv_to_palette(named_colors_csv)
    else:
        named_palette = None

    # Iterate over the color data and append RGB values to the palette
    for i, color in enumerate(rgb_data):
        r, g, b = color[:3]  # Extract only the first three values (R, G, B)

        if named_palette:
            # Create the target color from RGB values
            target_rgb = (r, g, b)

            # Find the nearest named color using the C function
            nearest_color = au.find_nearest_color_rgb(target_rgb, named_palette)

            # Extract the name from the nearest color (assuming the last item is the color name)
            color_name = nearest_color[-1] if nearest_color else f"Color {i}"
        else:
            color_name = f"Color {i}"

        # Append the RGB values and name to the palette
        palette.append(f"{r:3} {g:3} {b:3} {color_name}\n")

    # Write the palette to the file
    with open(palette_filepath, 'w') as f:
        f.writelines(palette)

    print(f"GIMP palette saved to {palette_filepath}")

def generate_gimp_palette_from_csv(input_file, output_file, palette_name, num_columns=16):
    """
    Generate a GIMP palette from the named colors CSV file, sorting by RGB values.
    If duplicate RGB values are found, it combines the names.

    Args:
        input_file (str): Path to the input CSV file with named colors.
        output_file (str): Path to the output GIMP palette file.
        palette_name (str): Name of the palette.
        num_columns (int): Number of columns in the GIMP palette file (default: 16).
    """
    # Create the GIMP palette header line by line
    palette = []
    palette.append("GIMP Palette\n")
    palette.append(f"Name: {palette_name}\n")
    palette.append(f"Columns: {num_columns}\n")
    palette.append("#\n")

    # Dictionary to store combined color names by RGB
    color_dict = {}

    # Read the CSV and process each row
    with open(input_file, 'r') as infile:
        reader = csv.DictReader(infile)

        for row in reader:
            # Extract RGB values and color name
            r = int(row['r'].strip())
            g = int(row['g'].strip())
            b = int(row['b'].strip())
            name = row['name'].strip()

            # Create an RGB tuple as the key
            rgb_key = (r, g, b)

            # If the RGB value already exists, append the name; otherwise, create a new entry
            if rgb_key in color_dict:
                color_dict[rgb_key].append(name)
            else:
                color_dict[rgb_key] = [name]

    # Sort the colors by RGB values
    sorted_colors = sorted(color_dict.items(), key=lambda x: x[0])

    # Process the sorted colors and write to the palette
    for (r, g, b), names in sorted_colors:
        combined_names = ', '.join(names)  # Combine names if duplicates exist
        # Append to the palette in GIMP format: "R G B Name"
        palette.append(f"{r:3d} {g:3d} {b:3d}  {combined_names}\n")

    # Write the palette to the file
    with open(output_file, 'w') as outfile:
        outfile.writelines(palette)

    print(f"GIMP palette saved to {output_file}")

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

                # Convert RGB to HSV using the C API function
                h, s, v = au.rgb_to_hsv(r, g, b)

                # Convert RGB to CMYK using the C API function
                c, m, y, k = au.rgb_to_cmyk(r, g, b)

                # Append a single tuple with all values
                palette_data.append((r, g, b, h, s, v, c, m, y, k))

            except ValueError:
                # Skip lines that don't have valid integer RGB values
                continue

    return palette_data

def get_num_columns_from_gimp_palette(filepath):
    """
    Reads a GIMP palette file and returns the number of columns specified in the file.

    Args:
        filepath: Path to the GIMP palette file.

    Returns:
        The number of columns specified in the GIMP palette file.
    """
    with open(filepath, 'r') as f:
        for line in f:
            if "Columns" in line:
                return int(line.split(":")[1].strip())

    return None

def read_text_hex(file_path):
    """
    Reads a palette file and returns a list of RGB tuples.
    
    Args:
        file_path (str): Path to the palette.txt file.
        
    Returns:
        List[Tuple[int, int, int]]: List of RGB tuples.
    """
    rgb_list = []
    
    with open(file_path, 'r') as file:
        for line in file:
            hex_color = line.strip()
            
            # Ensure the line is a valid hex color (starts with # and has 7 characters total)
            if hex_color.startswith('#') and len(hex_color) == 7:
                # Convert hex to RGB tuple
                r = int(hex_color[1:3], 16)
                g = int(hex_color[3:5], 16)
                b = int(hex_color[5:7], 16)
                rgb_list.append((r, g, b))
    
    return rgb_list

def process_palette(palette, hues):
    master_hue_colors = {}
    colors_by_hue = {h: [] for h in hues}

    # Step 1: Pre-quantize hues and filter out fully unsaturated colors
    quantized_palette = [
        (*color, quantize_value(color[H], hues)) 
        for color in palette if color[S] > 0
    ]

    # Step 2: Assemble colors into their respective hue buckets
    for color in quantized_palette:
        quantized_h = color[-1]  # The quantized hue
        colors_by_hue[quantized_h].append(color)

    # Step 3: Set the master hue color for each hue bucket
    for h in hues:
        # The master color is the fully saturated and valued color for the hue
        r, g, b = au.hsv_to_rgb(h, 1, 1)
        master_hue_colors[h] = (r, g, b, h, 1, 1, 0, 0, 0, 0)  # Full color tuple

    # Step 4: Add grayscale colors to all hue buckets
    for color in palette:
        if color[S] == 0:  # Grayscale colors
            for h in colors_by_hue:
                if color not in colors_by_hue[h]:
                    colors_by_hue[h].append(color)  # Add full color tuple

    return master_hue_colors, colors_by_hue

def get_nearest_color_hsv(target_color, palette):
    """Finds the nearest color in HSV space."""
    nearest_color = None
    min_distance = float('inf')

    for color in palette:
        distance = math.sqrt((color[H] - target_color[0])**2 +
                             (color[S] - target_color[1])**2 +
                             (color[V] - target_color[2])**2)
        if distance < min_distance:
            nearest_color = color
            min_distance = distance

    return nearest_color

def create_image_from_colors(colors_by_hue, cell_size=16):
    # Find the maximum number of colors in any hue category
    max_colors_in_hue = max(len(colors) for colors in colors_by_hue.values())
    num_hues = len(colors_by_hue)
    
    # Create a new image with additional row for saturation = 0
    img_width = max_colors_in_hue * cell_size
    img_height = num_hues * cell_size  # Rows are automatically adjusted based on num_hues
    image = Image.new('RGB', (img_width, img_height), 'black')
    draw = ImageDraw.Draw(image)

    # Draw the rectangles
    for row, (hue, colors) in enumerate(colors_by_hue.items()):
        for col, color in enumerate(colors):
            r, g, b = color[R], color[G], color[B]  # Extract R, G, B values
            x1 = col * cell_size
            y1 = row * cell_size
            x2 = x1 + cell_size - 1
            y2 = y1 + cell_size - 1
            draw.rectangle([x1, y1, x2, y2], fill=(r, g, b))

    return image


def rgb_to_cmyk(r, g, b):
    """Convert RGB to CMYK."""
    if (r == 0) and (g == 0) and (b == 0):
        return 0, 0, 0, 1
    # Normalize RGB values to [0, 1]
    r = r / 255.0
    g = g / 255.0
    b = b / 255.0
    k = 1 - max(r, g, b)
    c = (1 - r - k) / (1 - k) if 1 - k != 0 else 0
    m = (1 - g - k) / (1 - k) if 1 - k != 0 else 0
    y = (1 - b - k) / (1 - k) if 1 - k != 0 else 0
    return c, m, y, k

def generate_gimp_palette_rainbow():
    """
    Generate a rainbow GIMP palette with grayscale colors and hues.
    
    Args:
        filename: Filepath where the palette will be saved.
        palette_name: Name of the palette to use in the GIMP file.
        num_columns: Number of columns to specify in the GIMP palette.
    """

    # Create an empty list for RGB color data
    rgb_data = []

    # Step 1: Generate grayscale colors (first 16 colors)
    grays = generate_normalized_quanta(0,255,16)
    for gray in grays:
        rgb_data.append((round(gray), round(gray), round(gray)))

    # Step 2: Generate colors for each hue
    num_hues = 15
    hues = generate_normalized_quanta(0,1,num_hues)

    num_values = 8
    values = generate_normalized_quanta(1/8,1,num_values)

    num_saturations = 8
    saturations = generate_normalized_quanta(7/8,1/8,num_saturations)

    for h in hues:
        # First half: value from high to low, full saturation
        for v in values:
            r,g,b = au.hsv_to_rgb(h, 1, v)
            rgb_data.append((round(r), round(g), round(b)))

        # Second half: saturation from low to high, full value
        for s in saturations:
            r,g,b = au.hsv_to_rgb(h, s, 1)
            rgb_data.append((round(r), round(g), round(b)))

    return rgb_data

def generate_gimp_palette_hsv():
    h_values = generate_normalized_quanta(0.0, 1.0, 2**4)
    s_values = generate_normalized_quanta(0.125, 0.875, 2**2)
    v_values = generate_normalized_quanta(0.125, 0.875, 2**2)

    rgb_data = []

    for h in h_values:
        for s in s_values:
            for v in v_values:
                r, g, b = au.hsv_to_rgb(h, s, v)
                rgb_data.append((r, g, b))
                # print(f"HSV: {h}, {s}, {v} -> RGB: {r}, {g}, {b}")

    return rgb_data

# def generate_gimp_palette_rgb332():
#     r_values = generate_normalized_quanta(0.0, 255.0, 2**3)
#     g_values = generate_normalized_quanta(0.0, 255.0, 2**3)
#     b_values = generate_normalized_quanta(0.0, 255.0, 2**2)

#     rgb_data = []

#     for r in r_values:
#         for g in g_values:
#             for b in b_values:
#                 rgb_data.append((round(r), round(g), round(b)))
#                 # print(f"RGB: {round(r)}, {round(g)}, {round(b)}")

#     return rgb_data

def generate_gimp_palette_rgb332():
    r_values = [0, 36, 72, 109, 145, 182, 218, 255]
    g_values = r_values
    # b_values = [0,     72,      145,           255]
    b_values = [0,         109,      182,      255]
    # b_values = [0,     72,           182,      255]

    rgb_data = []

    for r in r_values:
        for g in g_values:
            for b in b_values:
                rgb_data.append((round(r), round(g), round(b)))
                # print(f"RGB: {round(r)}, {round(g)}, {round(b)}")

    return rgb_data

def generate_gimp_palette_rgb565():
    r_values = generate_normalized_quanta(0.0, 255.0, 2**5)
    g_values = generate_normalized_quanta(0.0, 255.0, 2**6)
    b_values = generate_normalized_quanta(0.0, 255.0, 2**5)

    rgb_data = []

    for r in r_values:
        for g in g_values:
            for b in b_values:
                rgb_data.append((round(r), round(g), round(b)))
                # print(f"RGB: {round(r)}, {round(g)}, {round(b)}")

    return rgb_data

def generate_gimp_palette_rgb111():
    r_values = generate_normalized_quanta(0.0, 255.0, 2)
    g_values = generate_normalized_quanta(0.0, 255.0, 2)
    b_values = generate_normalized_quanta(0.0, 255.0, 2)

    rgb_data = []

    for r in r_values:
        for g in g_values:
            for b in b_values:
                rgb_data.append((round(r), round(g), round(b)))
                # print(f"RGB: {round(r)}, {round(g)}, {round(b)}")

    return rgb_data

def generate_gimp_palette_vrgb1111():
    v_values = generate_normalized_quanta(0.5, 1.0, 2)
    r_values = generate_normalized_quanta(0.0, 255.0, 2)
    g_values = generate_normalized_quanta(0.0, 255.0, 2)
    b_values = generate_normalized_quanta(0.0, 255.0, 2)


    rgb_data = []

    for v in v_values:
        for r in r_values:
            for g in g_values:
                for b in b_values:
                    rgb_data.append((round(r*v), round(g*v), round(b*v)))
                    # print(f"RGB: {round(r)}, {round(g)}, {round(b)}")

    return rgb_data

def generate_gimp_palette_vrgb2222():
    """
    Generate a VRGB GIMP palette with intensity multipliers.
    
    Args:
        filename: Filepath where the palette will be saved.
        palette_name: Name of the palette to use in the GIMP file.
        num_columns: Number of columns to specify in the GIMP palette.
    """
    # Define VRGB quanta and multipliers
    min_quantum = 8
    max_quantum = 64 + min_quantum
    num_quanta = 4
    rgb_quanta = generate_normalized_quanta(min_quantum, max_quantum, num_quanta)
    print(rgb_quanta)
    v_multipliers = [1, 2, 3, 4]
    
    # Create an empty list for RGB color data
    rgb_data = []

    # Iterate over V multipliers (00 to 11)
    for v_mult in v_multipliers:
        # Iterate over all combinations of R, G, B quantum values
        for r in rgb_quanta:
            for g in rgb_quanta:
                for b in rgb_quanta:
                    # Scale RGB values by the V multiplier
                    r_scaled = min(round(r * v_mult)-min_quantum, 255)
                    g_scaled = min(round(g * v_mult)-min_quantum, 255)
                    b_scaled = min(round(b * v_mult)-min_quantum, 255)

                    # Append the scaled RGB color to the list
                    rgb_data.append((r_scaled, g_scaled, b_scaled))

    return rgb_data

def generate_gimp_palette_rgb222():
    r_values = generate_normalized_quanta(0.0, 255.0, 2**2)
    g_values = generate_normalized_quanta(0.0, 255.0, 2**2)
    b_values = generate_normalized_quanta(0.0, 255.0, 2**2)

    rgb_data = []

    for r in r_values:
        for g in g_values:
            for b in b_values:
                rgb_data.append((round(r), round(g), round(b)))
                # print(f"RGB: {round(r)}, {round(g)}, {round(b)}")

    return rgb_data

def generate_gimp_palette_rgb333():
    r_values = generate_normalized_quanta(0.0, 255.0, 2**3)
    g_values = generate_normalized_quanta(0.0, 255.0, 2**3)
    b_values = generate_normalized_quanta(0.0, 255.0, 2**3)

    rgb_data = []

    for r in r_values:
        for g in g_values:
            for b in b_values:
                rgb_data.append((round(r), round(g), round(b)))
                # print(f"RGB: {round(r)}, {round(g)}, {round(b)}")

    return rgb_data

def generate_gimp_palette_rgb444():
    r_values = generate_normalized_quanta(0.0, 255.0, 2**4)
    g_values = generate_normalized_quanta(0.0, 255.0, 2**4)
    b_values = generate_normalized_quanta(0.0, 255.0, 2**4)

    rgb_data = []

    for r in r_values:
        for g in g_values:
            for b in b_values:
                rgb_data.append((round(r), round(g), round(b)))
                # print(f"RGB: {round(r)}, {round(g)}, {round(b)}")

    return rgb_data

def generate_gimp_palette_cmyk():
    """Generate a list of lists for color data (RGB, CMYK, HSV)."""
    quant_levels = 3
    k_scaling_factor = 1 / 4
    rgb_data = []
    for k in range(4):
        for c in range(4):
            for m in range(4):
                for y in range(4):
                    c_scale = c / quant_levels
                    m_scale = m / quant_levels
                    y_scale = y / quant_levels
                    k_value = k * k_scaling_factor / quant_levels
                    red, green, blue = au.cmyk_to_rgb(c_scale, m_scale, y_scale, k_value)
                    rgb_data.append((red, green, blue))
    return rgb_data

if __name__ == "__main__":
    rgb_data = generate_gimp_palette_rgb222()
    generate_gimp_palette(rgb_data, 'examples/widgets/colors/RGB222.gpl', 'RGB222', 8)
    rgb_data = generate_gimp_palette_vrgb1111()
    generate_gimp_palette(rgb_data, 'examples/widgets/colors/VRGB1111.gpl', 'VRGB1111', 4)
    rgb_data = generate_gimp_palette_rgb332()
    generate_gimp_palette(rgb_data, 'examples/widgets/colors/RGB332.gpl', 'RGB332', 16)
    rgb_data = generate_gimp_palette_rainbow()
    generate_gimp_palette(rgb_data, 'examples/widgets/colors/Rainbow.gpl', 'Rainbow', 16)
    rgb_data = generate_gimp_palette_vrgb2222()
    generate_gimp_palette(rgb_data, 'examples/widgets/colors/VRGB2222.gpl', 'VRGB2222', 16)