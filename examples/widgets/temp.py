from make_palette import read_gimp_palette, sort_colors_by, generate_normalized_quanta, quantize_value
import agonutils as au
from PIL import Image, ImageDraw

# Define index values for sorting keys
R, G, B, H, S, V, C, M, Y, K = range(10)

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
            x1 = col * cell_size
            y1 = row * cell_size
            x2 = x1 + cell_size - 1  # Adjust to fit the rectangles within their space
            y2 = y1 + cell_size - 1
            draw.rectangle([x1, y1, x2, y2], fill=color)

    return image

if __name__ == "__main__":
    palette_file = 'examples/widgets/colors/Agon64.gpl'
    palette = read_gimp_palette(palette_file)
    palette = sort_colors_by(palette, [H, V, S, R, G, B])
    values = generate_normalized_quanta(0, 255, 4)

    hues = []
    colors_by_hue = {}
    colors_by_hue[1] = []  # This will store grayscale colors
    
    # First pass: Add only hues with quantized full-saturation color found
    for color in palette:
        h = color[H]
        if h not in hues:
            # Convert HSV to RGB for full saturation and value
            r, g, b = au.hsv_to_rgb(h, 1, 1)
            r0 = int(quantize_value(r, values))
            g0 = int(quantize_value(g, values))
            b0 = int(quantize_value(b, values))

            # If the quantized color matches the original, add to hues and dictionary
            if (r, g, b) == (r0, g0, b0):
                hues.append(h)
                colors_by_hue[h] = [(r0, g0, b0)]  # First entry for each hue
    
    # Second pass: Quantize hues and add colors to appropriate buckets
    for color in palette:
        if color[S] > 0:
            h = quantize_value(color[H], hues)
            colors_by_hue[h].append((color[R], color[G], color[B]))  # Store RGB tuple for colors with saturation > 0
        else:
            colors_by_hue[1].append((color[R], color[G], color[B]))  # Store grayscale colors under hue key 1

    print(f"Unique hues: {len(colors_by_hue)}")

    # Generate the image from the colors_by_hue dictionary
    cell_size = 16
    image = create_image_from_colors(colors_by_hue, cell_size)

    # Show the image
    image.show()
