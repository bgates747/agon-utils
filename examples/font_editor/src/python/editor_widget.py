import tkinter as tk
from PIL import Image
from agon_font import parse_rgba_color, rgba_to_hex

class EditorWidget(tk.Frame):
    """A widget for editing individual characters with a scalable grid."""
    
    def __init__(self, parent, app_reference, **kwargs):
        super().__init__(parent, **kwargs)
        self.app_reference = app_reference  # Reference to the main app
        self.pixel_size = 16  # Each pixel in the character is scaled to 16 pixels in the grid
        self.pixel_fill_size = 15  # Actual fill size for each pixel (to leave a 1px cyan border)

        # Create the canvas for the pixel grid
        self.canvas = tk.Canvas(self, bg="cyan")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Bind click events to toggle pixel values
        self.canvas.bind("<Button-1>", self.on_click)

        # Initialize variables for character image and colors
        self.char_image = None
        self.fg_color = None  # Foreground color (RGBA tuple), set in initialize_grid
        self.bg_color = None  # Background color (RGBA tuple), set in initialize_grid
        self.fg_color_hex = None  # Tkinter-compatible foreground color in hex
        self.bg_color_hex = None  # Tkinter-compatible background color in hex

    def initialize_grid(self):
        """Initialize the character grid, set colors, and configure canvas size."""
        
        # Retrieve colors from font configuration
        font_config = self.app_reference.font_config_editor.get_modified_config()
        self.fg_color = parse_rgba_color(font_config['fg_color'])
        self.bg_color = parse_rgba_color(font_config['bg_color'])
        self.fg_color_hex = rgba_to_hex(self.fg_color)
        self.bg_color_hex = rgba_to_hex(self.bg_color)

        # Retrieve font dimensions for grid size
        char_width = font_config['font_width']
        char_height = font_config['font_height']

        # Calculate the canvas size based on pixel size and character dimensions
        canvas_width = char_width * self.pixel_size + 1
        canvas_height = char_height * self.pixel_size + 1

        # Resize the canvas and set frame dimensions
        self.canvas.config(width=canvas_width, height=canvas_height)
        self.config(width=canvas_width, height=canvas_height)

        # Initialize char_image as a blank image with background color
        self.char_image = Image.new("RGBA", (char_width, char_height), self.bg_color)
        self.populate_from_image(self.char_image)

    def update_pixel(self, x, y, color_hex):
        """Update a specific pixel in the grid (x, y) with the given color."""
        x1 = x * self.pixel_size + 2
        y1 = y * self.pixel_size + 2
        x2 = x1 + self.pixel_fill_size
        y2 = y1 + self.pixel_fill_size

        # Draw the pixel with the specified color, leaving a 1px cyan border
        self.canvas.create_rectangle(x1, y1, x2, y2, fill=color_hex, outline='')

    def populate_from_image(self, image):
        """Populate the editor grid with pixel data from the provided image."""
        pixels = image.load()
        width, height = image.size

        for x in range(width):
            for y in range(height):
                pixel_value = pixels[x, y]  # Get the RGBA tuple for the pixel
                color_hex = rgba_to_hex(pixel_value)  # Convert RGBA to hex
                self.update_pixel(x, y, color_hex)  # Update the editor canvas

    def on_click(self, event):
        """Handle mouse click on the editor grid and toggle the pixel."""
        if self.char_image is None:
            return

        # Get the grid dimensions from char_image
        char_width, char_height = self.char_image.size

        x = (event.x - 2) // self.pixel_size
        y = (event.y - 2) // self.pixel_size

        if 0 <= x < char_width and 0 <= y < char_height:
            current_color = self.char_image.getpixel((x, y))
            
            # Toggle the pixel color based on the current color
            new_color = self.bg_color if current_color[:3] == self.fg_color[:3] else self.fg_color
            
            # Update the editor's display and char_image with the new color
            self.char_image.putpixel((x, y), new_color)
            self.update_pixel(x, y, rgba_to_hex(new_color))  # Still necessary for Tkinter canvas

            # Pass the new color to ImageDisplay directly
            self.app_reference.image_display.update_pixel(x, y, new_color)
