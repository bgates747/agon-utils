from make_palette import read_gimp_palette, sort_colors_by, generate_normalized_quanta, process_palette
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
            x2 = x1 + cell_size
            y2 = y1 + cell_size
            draw.rectangle([x1, y1, x2, y2], fill=color)

    return image


if __name__ == "__main__":
    # num_hues = 5
    # hues = generate_normalized_quanta(0, 1-(1/num_hues), num_hues)
    # values = generate_normalized_quanta(0, 255, 4)

    # palette_file = 'examples/widgets/colors/Agon16.gpl'
    # palette = read_gimp_palette(palette_file)
    # palette = sort_colors_by(palette, [H, R, G, B])

    # max_saturation_colors, colors_by_hue = process_palette(palette, hues)

    # # print(f"Max saturation colors: {max_saturation_colors}")
    # # print(f"Colors by hue: {colors_by_hue}")

    # # Generate the image from the colors_by_hue dictionary
    # cell_size = 16
    # image = create_image_from_colors(colors_by_hue, cell_size)

    # # Show the image
    # image.show()

    quanta3 = generate_normalized_quanta(0, 255, 2**3)
    quanta2 = generate_normalized_quanta(0, 255, 2**2)
    print(quanta3)
    print(quanta2)