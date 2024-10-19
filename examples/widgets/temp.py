from make_palette import read_gimp_palette, sort_colors_by, generate_normalized_quanta, process_palette, create_image_from_colors
import agonutils as au
from PIL import Image, ImageDraw

# Define index values for sorting keys
R, G, B, H, S, V, C, M, Y, K = range(10)

if __name__ == "__main__":
    # num_hues = 16
    # hues = generate_normalized_quanta(0, 1-(1/num_hues), num_hues)
    # hues = [0.000, 0.083, 0.167, 0.333, 0.500, 0.667, 0.764, 0.833]

    palette_file = 'examples/widgets/colors/Agon64.gpl'
    palette = read_gimp_palette(palette_file)
    palette = sort_colors_by(palette, [H, R, G, B])

    hues = []
    for color in palette:
        h = color[H]
        if h not in hues:
            hues.append(h)
    hues.sort()
    print(f"Hues: {hues}")

    max_saturation_colors, colors_by_hue = process_palette(palette, hues)

    # print(f"Max saturation colors: {max_saturation_colors}")
    # print(f"Colors by hue: {colors_by_hue}")

    # Generate the image from the colors_by_hue dictionary
    cell_size = 24
    image = create_image_from_colors(colors_by_hue, cell_size)

    # Show the image
    image.show()