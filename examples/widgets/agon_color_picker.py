import tkinter as tk
from tkinter import Canvas
from PIL import Image, ImageTk, ImageDraw
import colorsys
import math
import agonutils as au
import make_palette as mp
import os

# Define index values for sorting keys
R, G, B, H, S, V, C, M, Y, K = range(10)

class AgonColorPicker(tk.Toplevel):
    """Custom color picker dialog that emulates tkinter's askcolor behavior."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent)
        self.title("Color Picker with Hue and Color Picker")
        
        # Make this window modal
        self.transient(parent)
        self.grab_set()
        
        # Set image paths dynamically based on the current script's directory
        base_dir = os.path.join(os.path.dirname(__file__), "colors")
        self.hue_image_path = os.path.join(base_dir, 'hue_picker.png')
        self.color_picker_image_path = os.path.join(base_dir, 'color_picker.png')
        self.palette_grid_image_path = os.path.join(base_dir, 'palette_grid.png')
        self.selected_color_image_path = os.path.join(base_dir, 'selected_color.png')

        # Extract all parameters from kwargs
        palette_name = kwargs.get('palette_name')
        self.palette_filepath = f'{base_dir}/{palette_name}.gpl'
        self.geometry(kwargs.get('app_geometry', '800x600'))

        # Set image dimensions with defaults if not provided
        self.hue_image_width = kwargs.get('hue_image_width', 640)
        self.hue_image_height = kwargs.get('hue_image_height', 64)
        self.color_picker_width = kwargs.get('color_picker_width', 240)
        self.color_picker_height = kwargs.get('color_picker_height', 240)

        # Create dummy RGBA images
        self.create_dummy_images()

        # Canvas for the hue picker image
        self.canvas_hue_picker = Canvas(self, width=self.hue_image_width, height=self.hue_image_height)
        self.canvas_hue_picker.pack()
        self.hue_image_tk, self.hue_image_pillow = self.load_image(self.hue_image_path)
        self.canvas_hue_picker.create_image(0, 0, anchor=tk.NW, image=self.hue_image_tk)
        self.canvas_hue_picker.bind("<Button-1>", self.on_hue_click)

        # Generate the hue picker image
        self.generate_hue_picker_image(self.hue_image_path)
        self.hue_image_tk, self.hue_image_pillow = self.load_image(self.hue_image_path)
        self.canvas_hue_picker.create_image(0, 0, anchor=tk.NW, image=self.hue_image_tk)

        # Frame to hold color picker and palette grid
        self.side_by_side_frame = tk.Frame(self)
        self.side_by_side_frame.pack()

        # Canvas for the color picker
        self.canvas_color_picker = Canvas(self.side_by_side_frame, width=self.color_picker_width, height=self.color_picker_height)
        self.canvas_color_picker.pack(side=tk.LEFT)
        self.color_picker_image_tk, self.color_picker_image_pillow = self.load_image(self.color_picker_image_path)
        self.canvas_color_picker.create_image(0, 0, anchor=tk.NW, image=self.color_picker_image_tk)
        self.canvas_color_picker.bind("<Button-1>", self.on_color_click)

        # Canvas for the palette grid
        self.canvas_palette_grid = Canvas(self.side_by_side_frame, width=self.color_picker_width, height=self.color_picker_height)
        self.canvas_palette_grid.pack(side=tk.RIGHT)
        self.generate_palette_grid_image(self.palette_filepath)
        self.palette_grid_image_tk, self.palette_grid_image_pillow = self.load_image(self.palette_grid_image_path)
        self.canvas_palette_grid.create_image(0, 0, anchor=tk.NW, image=self.palette_grid_image_tk)
        self.canvas_palette_grid.bind("<Button-1>", self.on_palette_grid_click)

        # Canvas for displaying selected color
        self.canvas_selected_color = Canvas(self, width=self.hue_image_width, height=self.hue_image_height)
        self.canvas_selected_color.pack()
        self.selected_color_image_tk, self.selected_color_image_pillow = self.load_image(self.selected_color_image_path)
        self.canvas_selected_color.create_image(0, 0, anchor=tk.NW, image=self.selected_color_image_tk)

        # Info label
        self.info_label = tk.Label(self, text="Click on a hue to generate color picker", font=("Arial", 14), pady=10)
        self.info_label.pack(side=tk.BOTTOM)

        # Initialize color selection variables
        self.selected_rgb = None
        self.selected_hex = None

        # Initialize the hue picker
        self.on_hue_selected(0)  # Set hue to 0 by default
        self.set_color_from_pixel(0, 0)

        # OK button to confirm the color selection
        self.ok_button = tk.Button(self, text="OK", command=self.on_ok)
        self.ok_button.pack(side=tk.BOTTOM, pady=10)

        # Wait for the dialog to be dismissed
        self.wait_window(self)


    def on_palette_grid_click(self, event):
        """Handles user click on the palette grid, updates the hue, and refreshes the color picker."""
        x, y = event.x, event.y

        # Get the color of the pixel at the clicked position from the palette grid
        r, g, b, a = self.palette_grid_image_pillow.getpixel((x, y))

        # Fill the selected color canvas with the selected color
        selected_color_image = Image.new("RGBA", (self.hue_image_width, self.hue_image_height), (r, g, b, a))
        self.selected_color_image_tk = ImageTk.PhotoImage(selected_color_image)
        self.canvas_selected_color.create_image(0, 0, anchor=tk.NW, image=self.selected_color_image_tk)

        # Convert RGB to HSV to extract the hue value
        h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
        hue = h  # Update hue

        # Update the color picker widget with the new hue
        self.on_hue_selected(hue)

        # Update the selection rectangle in the palette grid
        self.update_selection(r, g, b)

        # Display the selected color information in the status label
        hex_value = f"#{r:02x}{g:02x}{b:02x}{a:02x}"
        self.info_label.config(text=f"RGB: ({r}, {g}, {b}, {a})\nHSV: ({h:.2f}, {s:.2f}, {v:.2f})\n"
                                    f"Hex: {hex_value}")

    def set_color_from_pixel(self, x, y):
        """Set the color based on the pixel at (x, y) in the color picker image."""
        r, g, b, a = self.color_picker_image_pillow.getpixel((x, y))
        selected_color_image = Image.new("RGBA", (self.hue_image_width, self.hue_image_height), (r, g, b, a))
        selected_color_image.save(self.selected_color_image_path)
        self.selected_color_image_tk = ImageTk.PhotoImage(selected_color_image)
        self.canvas_selected_color.create_image(0, 0, anchor=tk.NW, image=self.selected_color_image_tk)

    def generate_palette_grid_image(self, palette_filepath):
        """Generates an image of the palette colors laid out in a grid."""
        palette_data = mp.read_gimp_palette(palette_filepath)
        num_colors = len(palette_data)

        # Calculate grid size by specifying the number of columns and determining the required number of rows
        grid_width = mp.get_num_columns_from_gimp_palette(palette_filepath)  # Number of columns
        grid_height = math.ceil(num_colors / grid_width)  # Number of rows based on number of colors

        # Calculate the size of each cell
        cell_width = self.color_picker_width // grid_width
        cell_height = self.color_picker_height // grid_height

        # Create an image for the palette grid
        palette_grid_image = Image.new("RGBA", (self.color_picker_width, self.color_picker_height), (0, 0, 0, 255))
        draw = ImageDraw.Draw(palette_grid_image)

        # Fill the grid with palette colors (RGBA values)
        for i, (r, g, b, h, s, v, c, m, y, k) in enumerate(palette_data):
            col = i % grid_width
            row = i // grid_width
            x0, y0 = col * cell_width, row * cell_height
            x1, y1 = x0 + cell_width, y0 + cell_height
            draw.rectangle([x0, y0, x1, y1], fill=(r, g, b, 255))

        # Save the palette grid image
        palette_grid_image.save(self.palette_grid_image_path)

    def on_hue_selected(self, hue):
        """Calls the C API to generate the color picker image based on the selected hue."""
        print(f"Hue selected: {hue}")

        # Call the API function to generate the color picker image based on the hue
        image_data = au.process_image_with_palette(self.palette_filepath, hue, self.color_picker_width, self.color_picker_height)

        # Convert the raw image data (RGBA) to a Pillow Image
        self.image = Image.frombytes('RGBA', (self.color_picker_width, self.color_picker_height), image_data)

        # Update the canvas with the new image
        self.tk_image = ImageTk.PhotoImage(self.image)
        self.canvas_color_picker.create_image(0, 0, anchor=tk.NW, image=self.tk_image)

        # Store image data for later color lookup
        self.image_data = self.image


    def create_dummy_images(self):
        """Create black dummy RGBA images for each widget."""
        black_image_hue = Image.new("RGBA", (self.hue_image_width, self.hue_image_height), (0, 0, 0, 255))
        black_image_hue.save(self.hue_image_path)

        black_image_color_picker = Image.new("RGBA", (self.color_picker_width, self.color_picker_height), (0, 0, 0, 255))
        black_image_color_picker.save(self.color_picker_image_path)

        black_image_palette = Image.new("RGBA", (self.color_picker_width, self.color_picker_height), (0, 0, 0, 255))
        black_image_palette.save(self.palette_grid_image_path)

        black_image_selected_color = Image.new("RGBA", (self.hue_image_width, self.hue_image_height), (0, 0, 0, 255))
        black_image_selected_color.save(self.selected_color_image_path)

    def generate_hue_picker_image(self, filepath):
        """Generates a hue picker image and saves it to the given filepath."""
        # Create a new RGBA image for the hue picker
        image = Image.new("RGBA", (self.hue_image_width, self.hue_image_height))

        # Fill the image with hues (full saturation and value)
        for x in range(self.hue_image_width):
            hue = x / self.hue_image_width
            saturation = 1.0
            value = 1.0

            # Convert HSV to RGB
            rgb = colorsys.hsv_to_rgb(hue, saturation, value)
            r, g, b = int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255)

            # Draw the column with the RGBA values
            for y in range(self.hue_image_height):
                image.putpixel((x, y), (r, g, b, 255))

        # Save the hue image temporarily before processing it with the palette
        image.save(filepath)

        # Convert the hue picker image to match the palette using the C API
        tgt_file = filepath  # Overwrite the same file
        method = "HSV"  # Use HSV-based conversion
        transparent_rgb = (0, 0, 0, 255)  # No transparency used

        # Call the C API to process the image with the palette
        au.convert_to_palette(filepath, tgt_file, self.palette_filepath, method, transparent_rgb)

    def convert_hue_picker_to_palette(self, src_file, palette_file):
        """Converts the hue picker image to match the palette."""
        tgt_file = src_file  # Overwrite the same file
        method = "HSV"  # Find nearest color in the palette based on HSV values
        transparent_rgb = (0, 0, 0, 255)  # Alpha > 0 means no transparency used (RGB channels don't matter)

        # Call the C API function to convert the image to the palette
        au.convert_to_palette(src_file, tgt_file, palette_file, method, transparent_rgb)

    def load_image(self, filepath):
        """Loads the image from a file and returns both a Tkinter PhotoImage and a Pillow Image."""
        image_pillow = Image.open(filepath)
        image_tk = ImageTk.PhotoImage(image_pillow)
        return image_tk, image_pillow  # Return both the Tkinter and Pillow image

    def on_hue_click(self, event):
        """Handles user click on the hue picker, finds the color under the pointer, and generates the color picker image."""
        # Get the mouse coordinates relative to the canvas
        x, y = event.x, event.y

        # Get the color of the pixel at the clicked position from the Pillow image
        r, g, b, _ = self.hue_image_pillow.getpixel((x, y))  # Get the RGBA value from the Pillow image

        # Convert the RGB color to HSV
        hsv = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
        hue = hsv[0]  # Extract the hue value

        # Display the selected hue value
        self.info_label.config(text=f"Selected hue: {hue:.2f}")

        # Generate the color picker image using the C API function with the extracted hue
        self.on_hue_selected(hue)

    def on_hue_selected(self, hue):
        """Calls the C API to generate the color picker image based on the selected hue."""
        print(f"Hue selected: {hue}")

        # Call the API function to generate the color picker image based on the hue
        image_data = au.process_image_with_palette(self.palette_filepath, hue, self.color_picker_width, self.color_picker_height)

        # Convert the raw image data (RGBA) to a Pillow Image
        self.image = Image.frombytes('RGBA', (self.color_picker_width, self.color_picker_height), image_data)

        # Update the canvas with the new image
        self.tk_image = ImageTk.PhotoImage(self.image)
        self.canvas_color_picker.create_image(0, 0, anchor=tk.NW, image=self.tk_image)

        # Store image data for later color lookup
        self.image_data = self.image

    def on_color_click(self, event):
        """Handles user click on the color picker, finds the color, and displays details."""
        x, y = event.x, event.y

        # Get the color of the pixel at the clicked position from the color picker
        r, g, b, a = self.image_data.getpixel((x, y))

        # Fill a new canvas with the selected color
        selected_color_image = Image.new("RGBA", (self.hue_image_width, self.hue_image_height), (r, g, b, a))
        self.selected_color_tk = ImageTk.PhotoImage(selected_color_image)
        self.canvas_selected_color.create_image(0, 0, anchor=tk.NW, image=self.selected_color_tk)

        # Convert to HSV
        h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)

        # Convert to CMYK (simple method)
        c, m, y, k = self.rgb_to_cmyk(r, g, b)

        # Display color information
        hex_value = f"#{r:02x}{g:02x}{b:02x}{a:02x}"
        self.info_label.config(text=f"RGB: ({r}, {g}, {b}, {a})\nHSV: ({h:.2f}, {s:.2f}, {v:.2f})\n"
                                    f"CMYK: ({c:.2f}, {m:.2f}, {y:.2f}, {k:.2f})\nHex: {hex_value}")

        # Update the selection rectangle in the palette grid
        self.update_selection(r, g, b)


    def rgb_to_cmyk(self, r, g, b):
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
        
    def draw_selection_rectangle(self, col, row, cell_width, cell_height):
        """Draw a selection rectangle around the chosen color in the palette grid."""
        # Remove the previous selection rectangle if it exists
        if hasattr(self, 'selection_rectangle'):
            self.canvas_palette_grid.delete(self.selection_rectangle)

        # Calculate the coordinates of the rectangle based on the column and row
        x0 = col * cell_width
        y0 = row * cell_height
        x1 = x0 + cell_width
        y1 = y0 + cell_height

        self.selection_rectangle = self.canvas_palette_grid.create_rectangle(
            x0, y0, x1, y1, outline="magenta", width=5, dash=(4, 8)  # Dashed line
        )

    def update_selection(self, r, g, b):
        """Update the selection rectangle when a color is chosen."""
        # Read the palette data
        palette_data = mp.read_gimp_palette(self.palette_filepath)
        num_colors = len(palette_data)

        # Get the number of columns and calculate rows
        grid_width = mp.get_num_columns_from_gimp_palette(self.palette_filepath)
        grid_height = math.ceil(num_colors / grid_width)

        # Calculate the cell size
        cell_width = self.color_picker_width // grid_width
        cell_height = self.color_picker_height // grid_height

        # Find the index of the selected color (RGB match)
        for i, (pr, pg, pb, _, _, _, _, _, _, _) in enumerate(palette_data):
            if pr == r and pg == g and pb == b:
                # Calculate the row and column in the grid
                col = i % grid_width
                row = i // grid_width

                # Draw the selection rectangle at the calculated grid position
                self.draw_selection_rectangle(col, row, cell_width, cell_height)
                break

    def on_ok(self):
        """Close the dialog and save the selected color."""
        self.destroy()

    def on_palette_grid_click(self, event):
        """Handles user click on the palette grid."""
        x, y = event.x, event.y
        r, g, b, a = self.palette_grid_image_pillow.getpixel((x, y))
        self.update_selected_color(r, g, b, a)

    def set_color_from_pixel(self, x, y):
        """Set color based on pixel from color picker."""
        r, g, b, a = self.color_picker_image_pillow.getpixel((x, y))
        self.update_selected_color(r, g, b, a)

    def update_selected_color(self, r, g, b, a):
        """Updates the selected color and displays it."""
        selected_color_image = Image.new("RGBA", (self.hue_image_width, self.hue_image_height), (r, g, b, a))
        self.selected_color_image_tk = ImageTk.PhotoImage(selected_color_image)
        self.canvas_selected_color.create_image(0, 0, anchor=tk.NW, image=self.selected_color_image_tk)
        self.selected_rgb = (r, g, b, a)
        self.selected_hex = f"#{r:02x}{g:02x}{b:02x}{a:02x}"
        self.info_label.config(text=f"RGB: ({r}, {g}, {b}, {a})\nHex: {self.selected_hex}")

    @staticmethod
    def askcolor(color=None, parent=None, palette_name=None, **kwargs):
        """Static method to display the color picker dialog and return the selected color."""
        root = parent
        dialog = AgonColorPicker(root, color=color, palette_name=palette_name, **kwargs)
        return dialog.selected_rgb, dialog.selected_hex  # RGB tuple and hex color