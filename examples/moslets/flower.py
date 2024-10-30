import math
from PIL import Image, ImageDraw

def polar_to_cartesian(radius, theta):
    """
    Convert polar coordinates to Cartesian coordinates.
    """
    x = radius * math.cos(theta)
    y = radius * math.sin(theta)
    return x, y

def calc_point(theta_prime, theta_petal, prime_radius, depth, center_x, center_y, radius_scale):
    """
    Calculate the Cartesian coordinates based on normalized radii.
    """
    # Calculate the petal radius and total radius (unit circle)
    petal_radius = math.cos(theta_petal) * depth
    radius = prime_radius + petal_radius * prime_radius

    # Scale the radius
    radius *= radius_scale

    # Convert polar to Cartesian coordinates
    x, y = polar_to_cartesian(radius, theta_prime)

    # Shift to image coordinates
    x += center_x
    y += center_y

    return round(x), round(y)

def write_to_file(coords, autoexec_filepath, header):
    """
    Write the coordinates to the specified text file with the given header.
    """
    with open(autoexec_filepath, 'w') as file:
        # Write the header
        for line in header:
            file.write(line + '\n')

        # Write the initial move command
        x_prev, y_prev = coords[0]
        file.write(f"draw move abs {x_prev} {y_prev}\n")

        # Write the line commands for the rest of the coordinates
        for x, y in coords[1:]:
            file.write(f"draw line abs {x} {y}\n")

def flower(petals, vectors, depth, periods, shrink, clock_prime, clock_petal, 
           theta_prime, theta_petal, center_x, center_y, radius_scale, screen_width, screen_height, autoexec_filepath=None):
    # Convert angles to radians
    theta_prime_rad = theta_prime * math.pi / 180
    theta_petal_rad = theta_petal * math.pi / 180

    # Calculate step increments and total steps
    step_theta_prime = 2 * math.pi / (petals * vectors)
    step_theta_petal = 2 * math.pi / vectors
    total_steps = int(2 * math.pi / step_theta_prime * periods)
    step_theta_prime *= clock_prime
    step_theta_petal *= clock_petal

    # Calculate shrink per step (linear)
    shrink_step = -shrink / total_steps

    # Initialize prime_radius (unit circle)
    prime_radius = 1 - depth / 2

    # Create an image to plot the flower with specified screen resolution
    img = Image.new("RGB", (screen_width, screen_height), (0, 0, 170))  # Set background to #0000AA
    draw = ImageDraw.Draw(img)

    # Calculate initial coordinates
    coords = []
    x_prev, y_prev = calc_point(theta_prime_rad, theta_petal_rad, prime_radius, depth, center_x, center_y, radius_scale)
    coords.append((x_prev, y_prev))

    # Draw the flower
    for step in range(total_steps):
        # Advance theta values
        theta_prime_rad += step_theta_prime
        theta_petal_rad += step_theta_petal

        # Update prime_radius
        prime_radius += shrink_step

        # Calculate new coordinates
        x, y = calc_point(theta_prime_rad, theta_petal_rad, prime_radius, depth, center_x, center_y, radius_scale)
        coords.append((x, y))

        # Draw a line from the previous point to the current one
        draw.line([(x_prev, y_prev), (x, y)], fill=(255, 255, 255), width=1)

        # Update previous coordinates
        x_prev, y_prev = x, y

    # Invert the y-axis by flipping the image vertically
    img = img.transpose(Image.FLIP_TOP_BOTTOM)

    # Save the image
    img.save("examples/moslets/flower.png")

    return coords

if __name__ == "__main__":
    petals = 2.97
    vectors = 1
    depth = 0.0
    periods = 75
    shrink = 1.0
    clock_prime = -1.0
    clock_petal = 1.0
    theta_prime = 240
    theta_petal = 0.0
    radius_scale = 480
    center_x = 640
    center_y = 512
    screen_width = 1280
    screen_height = 1024
    autoexec_filepath = "/home/smith/Agon/emulator/sdcard/autoexec.txt"

    # Define the file header
    header = [
        "SET KEYBOARD 1",
        "vdu 22 19",
        "# vdu 23 1 0",
        f"# petals: {petals}",
        f"# vectors: {vectors}",
        f"# depth: {depth}",
        f"# periods: {periods}",
        f"# shrink: {shrink}",
        f"# clock_prime: {clock_prime}",
        f"# clock_petal: {clock_petal}",
        f"# theta_prime: {theta_prime}",
        f"# theta_petal: {theta_petal}",
        f"# radius_scale: {radius_scale}",
        f"# center_x: {center_x}",
        f"# center_y: {center_y}",
        "# draw gcol fg 4",
        f"# draw recf rel {screen_width} {screen_height}",
        "# draw gcol fg 15"
    ]

    # Generate the flower and get the list of coordinates
    coords = flower(petals, vectors, depth, periods, shrink, clock_prime, clock_petal, 
                    theta_prime, theta_petal, center_x, center_y, radius_scale, screen_width, screen_height, autoexec_filepath)

    # Write the coordinates to the specified file
    write_to_file(coords, autoexec_filepath, header)
