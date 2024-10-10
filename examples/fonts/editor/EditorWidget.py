import tkinter as tk
from tkinter import messagebox

class EditorWidget(tk.Frame):
    """ A widget for editing individual characters with a scalable grid """
    def __init__(self, parent, app_reference, *args, **kwargs):
        super().__init__(parent, **kwargs)

        self.app_reference = app_reference  # Store reference to the main app
        self.pixel_size = 16  # Each pixel in the character is scaled to 16 pixels in the grid
        self.pixel_fill_size = 15  # Actual fill size for each pixel (to leave a 1px cyan border)

        # Create the canvas to draw the grid and pixels
        self.canvas = tk.Canvas(self, bg="cyan")
        self.canvas.pack()

        # Bind a click event for toggling pixel values
        self.canvas.bind("<Button-1>", self.on_click)

        # Internal representation of the character (black/white)
        self.char_image = None

    def initialize_grid(self):
        """ Initialize the character grid and canvas based on the current font configuration """
        # Get font dimensions directly from the font configuration
        font_config = self.app_reference.font_config_editor.get_config()
        char_width = font_config['font_width']
        char_height = font_config['font_height']

        # Resize the canvas based on the new character width and height
        self.canvas.config(width=char_width * self.pixel_size + 1, height=char_height * self.pixel_size + 1)

        # Re-initialize the internal character image as a blank image (black/white array)
        self.char_image = [[0 for _ in range(char_height)] for _ in range(char_width)]
        self.populate_with_black()

    def update_pixel(self, x, y, color):
        """ Update a specific pixel in the grid (x, y) with the given color """
        x1 = x * self.pixel_size + 2
        y1 = y * self.pixel_size + 2
        x2 = x1 + self.pixel_fill_size
        y2 = y1 + self.pixel_fill_size

        # Draw the pixel with the specified color, leaving the background (1px border) cyan
        self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline='')

    def populate_with_black(self):
        """ Populate the entire editor with black pixels initially """
        if self.char_image is None:
            return  # Make sure the grid is initialized

        # Fetch current dimensions from font config for each row and column
        font_config = self.app_reference.font_config_editor.get_config()
        char_width = font_config['font_width']
        char_height = font_config['font_height']

        for x in range(char_width):
            for y in range(char_height):
                self.update_pixel(x, y, 'black')

    def populate_from_image(self, char_image):
        """ Populate the editor grid with pixel data from a character image. """
        pixels = char_image.load()
        width, height = char_image.size

        # Ensure that self.char_image matches the dimensions of char_image
        self.char_image = [[0 for _ in range(height)] for _ in range(width)]

        for x in range(width):
            for y in range(height):
                pixel_value = pixels[x, y]
                color = 'black' if pixel_value < 128 else 'white'
                self.char_image[x][y] = 0 if pixel_value < 128 else 1
                self.update_pixel(x, y, color)

    def on_click(self, event):
        """ Handle mouse click on the editor grid and toggle the pixel """
        if self.char_image is None:
            return

        # Retrieve dimensions from font config for consistency
        font_config = self.app_reference.font_config_editor.get_config()
        char_width = font_config['font_width']
        char_height = font_config['font_height']

        x = (event.x - 2) // self.pixel_size
        y = (event.y - 2) // self.pixel_size

        # Ensure the clicked position is within the grid bounds
        if 0 <= x < char_width and 0 <= y < char_height:
            current_value = self.char_image[x][y]
            new_value = 1 if current_value == 0 else 0
            self.char_image[x][y] = new_value

            # Update the pixel color visually in the editor
            color = 'white' if new_value == 1 else 'black'
            self.update_pixel(x, y, color)

            # Update the larger image via the ImageDisplayWidget (using actual pixel coordinates)
            self.app_reference.image_display.update_pixel(x, y, new_value)
