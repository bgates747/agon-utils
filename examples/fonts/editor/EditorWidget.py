
import tkinter as tk
from tkinter import messagebox

class EditorWidget(tk.Frame):
    """ A widget for editing individual characters with a scalable grid """
    def __init__(self, parent, app_reference, *args, **kwargs):
        super().__init__(parent, **kwargs)  # Pass only parent and **kwargs to the super class (tk.Frame)

        self.app_reference = app_reference  # Store reference to the main app
        self.char_width = None  # Width of the character in pixels (will be set later)
        self.char_height = None  # Height of the character in pixels (will be set later)
        self.pixel_size = 16  # Each pixel in the character is scaled to 16 pixels in the grid
        self.pixel_fill_size = 15  # Actual fill size for each pixel (to leave a 1px cyan border)

        # Create the canvas to draw the grid and pixels
        self.canvas = tk.Canvas(self, bg="cyan")
        self.canvas.pack()

        # Bind a click event for toggling pixel values
        self.canvas.bind("<Button-1>", self.on_click)

        # Internal representation of the character (black/white)
        self.char_image = None

    def initialize_grid(self, char_width, char_height):
        """ Initialize the character grid and canvas based on font metadata """
        self.char_width = char_width
        self.char_height = char_height

        # Resize the canvas based on the new character width and height
        self.canvas.config(width=self.char_width * self.pixel_size + 1, 
                           height=self.char_height * self.pixel_size + 1)

        # Re-initialize the internal character image as a blank image (black/white array)
        self.char_image = [[0 for _ in range(self.char_height)] for _ in range(self.char_width)]
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

        for x in range(self.char_width):
            for y in range(self.char_height):
                self.update_pixel(x, y, 'black')

    def populate_from_image(self, char_img):
        """ Populate the editor grid with pixel data from a character image. """
        char_pixels = char_img.load()

        # Make sure the image matches the editor's grid size
        img_width, img_height = char_img.size

        if img_width != self.char_width or img_height != self.char_height:
            messagebox.showerror(
                "Image Size Mismatch", 
                f"The character image size ({img_width}x{img_height}) does not match the expected "
                f"grid size ({self.char_width}x{self.char_height})."
            )
            return

        for x in range(self.char_width):
            for y in range(self.char_height):
                # Get the pixel value (0-255 grayscale)
                pixel_value = char_pixels[x, y]

                # Assume threshold for binary conversion: below 128 = black, above = white
                color = 'black' if pixel_value < 128 else 'white'
                self.char_image[x][y] = 0 if pixel_value < 128 else 1
                self.update_pixel(x, y, color)


    def on_click(self, event):
        """ Handle mouse click on the editor grid and toggle the pixel """
        if self.char_image is None:
            return  # Ensure the grid is initialized before handling clicks

        x = (event.x - 2) // self.pixel_size
        y = (event.y - 2) // self.pixel_size

        # Ensure the clicked position is within the grid bounds
        if 0 <= x < self.char_width and 0 <= y < self.char_height:
            # Toggle the pixel in the internal image representation
            current_value = self.char_image[x][y]
            new_value = 1 if current_value == 0 else 0  # Toggle between black (0) and white (1)
            self.char_image[x][y] = new_value

            # Update the pixel color visually in the editor
            color = 'white' if new_value == 1 else 'black'
            self.update_pixel(x, y, color)

            # Update the larger image via the ImageDisplayWidget (using actual pixel coordinates)
            self.app_reference.image_display.update_pixel(x, y, new_value)
