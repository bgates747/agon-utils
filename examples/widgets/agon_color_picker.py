
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

        # Extract other parameters from kwargs
        self.geometry(kwargs.get('app_geometry', '320x380'))
        palette_name = kwargs.get('palette_name')
        self.palette_filepath = f'{base_dir}/{palette_name}.gpl'
        self.palette = mp.read_gimp_palette(self.palette_filepath)

        # self.hues = [0.000, 0.083, 0.167, 0.333, 0.500, 0.667, 0.764, 0.833]
        # self.hues = [0.000, 0.125, 0.250, 0.375, 0.500, 0.625, 0.750, 0.875]

        # # Initialize num_hues and store hue dictionaries
        # self.num_hues = 12
        # self.hues = mp.generate_normalized_quanta(0, 1-(1/self.num_hues), self.num_hues)
        # print(f"Hues: {self.hues}")

        self.hues = []
        for color in self.palette:
            h = round(color[H],2)
            if h not in self.hues:
                self.hues.append(h)
        self.hues.sort()
        print(f"Hues: {self.hues}")

        # Process the palette and get the hue-based dictionaries
        self.master_hue_colors, self.colors_by_hue = mp.process_palette(self.palette, self.hues)

        # Repopulate self.hues with the keys from max_saturation_colors
        self.hues = list(self.master_hue_colors.keys())
        self.num_hues = len(self.hues)  # Update num_hues to reflect the new length of self.hues

        print(f"Hues: {self.hues}")



        # Set image dimensions
        self.hue_image_width = kwargs.get('hue_image_width', 320)
        self.hue_image_height = kwargs.get('hue_image_height', 32)
        self.color_picker_width = kwargs.get('color_picker_width', 160)
        self.color_picker_height = kwargs.get('color_picker_height', 160)

        # Create dummy RGBA images
        self.create_dummy_images()

        # Create hue picker canvas
        self.canvas_hue_picker = Canvas(self, width=self.hue_image_width, height=self.hue_image_height)
        self.canvas_hue_picker.pack()
        self.generate_hue_picker_image(self.hue_image_path)
        self.hue_image_tk, self.hue_image_pillow = self.load_image(self.hue_image_path)
        self.canvas_hue_picker.create_image(0, 0, anchor=tk.NW, image=self.hue_image_tk)
        self.canvas_hue_picker.bind("<Button-1>", self.on_hue_click)

        # Create frame for color picker and palette grid
        self.side_by_side_frame = tk.Frame(self)
        self.side_by_side_frame.pack()

        # Create color picker canvas
        self.canvas_color_picker = Canvas(self.side_by_side_frame, width=self.color_picker_width, height=self.color_picker_height)
        self.canvas_color_picker.pack(side=tk.LEFT)
        self.color_picker_image_tk, self.color_picker_image_pillow = self.load_image(self.color_picker_image_path)
        self.canvas_color_picker.create_image(0, 0, anchor=tk.NW, image=self.color_picker_image_tk)
        self.canvas_color_picker.bind("<Button-1>", self.on_color_click)

        # Create palette grid canvas
        self.canvas_palette_grid = Canvas(self.side_by_side_frame, width=self.color_picker_width, height=self.color_picker_height)
        self.canvas_palette_grid.pack(side=tk.RIGHT)
        self.generate_palette_grid_image(self.palette_filepath)
        self.palette_grid_image_tk, self.palette_grid_image_pillow = self.load_image(self.palette_grid_image_path)
        self.canvas_palette_grid.create_image(0, 0, anchor=tk.NW, image=self.palette_grid_image_tk)
        self.canvas_palette_grid.bind("<Button-1>", self.on_palette_grid_click)

        # Create canvas for selected color
        self.canvas_selected_color = Canvas(self, width=self.hue_image_width, height=self.hue_image_height)
        self.canvas_selected_color.pack()

        # OK/Cancel buttons
        button_frame = tk.Frame(self)
        button_frame.pack(pady=5)

        self.ok_button = tk.Button(button_frame, text="OK", command=self.on_ok)
        self.ok_button.pack(side=tk.LEFT, padx=5)

        self.cancel_button = tk.Button(button_frame, text="Cancel", command=self.on_cancel)
        self.cancel_button.pack(side=tk.LEFT, padx=5)

        # Info label
        self.info_label = tk.Label(self, text="Click on a hue to generate color picker", font=("Arial", 10), pady=5, height=3, anchor="w", justify="left")
        self.info_label.pack(side=tk.BOTTOM, fill=tk.X)

        # Initialize color selection variables
        self.selected_rgb = None
        self.selected_hex = None

        # Initialize hue picker and color selection
        self.on_hue_selected(0)
        self.set_color_from_pixel(0, 0)

        # Wait for the dialog to be dismissed
        self.wait_window(self)

    def generate_hue_picker_image(self, filepath):
        """Generates a hue picker image with max saturation colors and saves it to the given filepath."""
        image = Image.new("RGBA", (self.hue_image_width, self.hue_image_height))
        draw = ImageDraw.Draw(image)

        # Divide the width of the image by the number of hues and draw rectangles
        hue_segment_width = self.hue_image_width / self.num_hues

        for i, hue in enumerate(self.master_hue_colors):
            r, g, b = [self.master_hue_colors[hue][i] for i in (R, G, B)] 
            x0 = i * hue_segment_width
            x1 = (i + 1) * hue_segment_width
            draw.rectangle([x0, 0, x1, self.hue_image_height], fill=(r, g, b, 255))

        image.save(filepath)

        # Convert the hue picker image to match the palette using the C API
        tgt_file = filepath  # Overwrite the same file
        method = "HSV"  # Use HSV-based conversion
        transparent_rgb = (0, 0, 0, 255)  # No transparency used

        # Call the C API to process the image with the palette
        au.convert_to_palette(filepath, tgt_file, self.palette_filepath, method, transparent_rgb)

    def on_hue_selected(self, hue):
        """Calls the C API to generate the color picker image based on the selected hue."""
        # hue = mp.quantize_value(hue, self.hues)
        print(f"Hue selected: {hue}")

        # Create a temporary Gimp palette containing only colors in the selected hue dictionary
        rgb_data = []
        hue_lookup = mp.quantize_value(hue, self.hues)
        for color in self.colors_by_hue[hue_lookup]:
            rgb_data.append([color[i] for i in (R, G, B)])

        # Write the temporary palette to a file
        temp_palette_path = os.path.join(os.path.dirname(__file__), "colors", "temp_palette.gpl")
        mp.generate_gimp_palette(rgb_data, temp_palette_path, palette_name='temp_palette', num_columns=16, named_colors_csv=None)

        # Call the API function to generate the color picker image based on the hue
        image_data = au.process_image_with_palette(temp_palette_path, hue_lookup, self.color_picker_width, self.color_picker_height)

        # Convert the raw image data (RGBA) to a Pillow Image
        self.image = Image.frombytes('RGBA', (self.color_picker_width, self.color_picker_height), image_data)
        self.image.save(self.color_picker_image_path)

        # Update the canvas with the new image
        self.tk_image = ImageTk.PhotoImage(self.image)
        self.canvas_color_picker.create_image(0, 0, anchor=tk.NW, image=self.tk_image)

        # Store image data for later color lookup
        self.image_data = self.image

        # Get the color of the upper-left pixel
        self.set_color_from_pixel(0, 0)
        r, g, b, a = self.image.getpixel((0, 0))

        # Update the selection rectangle in the palette grid
        self.update_selection(r, g, b)

    def on_hue_click(self, event):
        """Handles user click on the hue picker, finds the color under the pointer, and generates the color picker image."""
        # Get the mouse coordinates relative to the canvas
        x, y = event.x, event.y

        # Get the color of the pixel at the clicked position from the Pillow image
        r, g, b, a = self.hue_image_pillow.getpixel((x, y))  # Get the RGBA value from the Pillow image

        # Convert the RGB color to HSV
        hsv = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
        hue = hsv[0]  # Extract the hue value
        # hue = mp.quantize_value(hue, self.hues)

        # Generate the color picker image using the C API function with the extracted hue
        self.on_hue_selected(hue)

        # Update the selection rectangle in the palette grid
        self.update_selection(r, g, b)
        self.update_selected_color(r, g, b, a)

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
        # hue = mp.quantize_value(hue, self.hues)

        # Update the color picker widget with the new hue
        self.on_hue_selected(hue)

        # Update the selection rectangle in the palette grid
        self.update_selection(r, g, b)
        self.update_selected_color(r, g, b, a)

    def on_color_click(self, event):
        """Handles user click on the color picker, finds the color, and displays details."""
        x, y = event.x, event.y

        # Get the color of the pixel at the clicked position from the color picker
        r, g, b, a = self.image_data.getpixel((x, y))

        # Fill a new canvas with the selected color
        selected_color_image = Image.new("RGBA", (self.hue_image_width, self.hue_image_height), (r, g, b, a))
        self.selected_color_tk = ImageTk.PhotoImage(selected_color_image)
        self.canvas_selected_color.create_image(0, 0, anchor=tk.NW, image=self.selected_color_tk)

        # Update the selection rectangle in the palette grid
        self.update_selection(r, g, b)
        self.update_selected_color(r, g, b, a)

    def set_color_from_pixel(self, x, y):
        """Set the color based on the pixel at (x, y) in the color picker image."""
        r, g, b, a = self.color_picker_image_pillow.getpixel((x, y))
        selected_color_image = Image.new("RGBA", (self.hue_image_width, self.hue_image_height), (r, g, b, a))
        selected_color_image.save(self.selected_color_image_path)
        self.selected_color_image_tk = ImageTk.PhotoImage(selected_color_image)
        self.canvas_selected_color.create_image(0, 0, anchor=tk.NW, image=self.selected_color_image_tk)

        # Update the selection rectangle in the palette grid
        self.update_selection(r, g, b)
        self.update_selected_color(r, g, b, a)

    def update_selected_color(self, r, g, b, a):
        """Updates the selected color and displays it."""
        selected_color_image = Image.new("RGBA", (self.hue_image_width, self.hue_image_height), (r, g, b, a))
        self.selected_color_image_tk = ImageTk.PhotoImage(selected_color_image)
        self.canvas_selected_color.create_image(0, 0, anchor=tk.NW, image=self.selected_color_image_tk)
        self.selected_rgb = (r, g, b, a)

        # Display the selected color information in the status label
        hex_value = f"#{r:02x}{g:02x}{b:02x}{a:02x}"
        h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
        h *= 360  # Convert hue to degrees
        s *= 100  # Convert saturation to percentage
        v *= 100  # Convert value to percentage
        self.info_label.config(text=f"RGB: ({r}, {g}, {b}, {a})\nHSV: ({h:.0f}, {s:.0f}, {v:.0f})\nHex: {hex_value}")

    def on_cancel(self):
        """Handles the cancel action and closes the dialog."""
        self.selected_rgb = None
        self.selected_hex = None
        self.destroy()

    def on_ok(self):
        """Handles the OK action and closes the dialog."""
        self.destroy()

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

    def load_image(self, filepath):
        """Loads the image from a file and returns both a Tkinter PhotoImage and a Pillow Image."""
        image_pillow = Image.open(filepath)
        image_tk = ImageTk.PhotoImage(image_pillow)
        return image_tk, image_pillow  # Return both the Tkinter and Pillow image
        
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

    @staticmethod
    def askcolor(color=None, parent=None, palette_name=None, **kwargs):
        """Static method to display the color picker dialog and return the selected color."""
        root = parent
        dialog = AgonColorPicker(root, color=color, palette_name=palette_name, **kwargs)
        return dialog.selected_rgb, dialog.selected_hex  # RGB tuple and hex color