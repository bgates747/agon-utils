
import os
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from CustomWidgets import DeltaControl
from AgonFont import create_master_image, generate_metadata_file

class TTF(tk.Frame):
    """A widget for generating font images and metadata from a .ttf file with adjustable options."""
    
    def __init__(self, parent, ttf_path, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        
        self.ttf_path = ttf_path
        self.point_size = 10
        self.ascii_range = (32, 127)
        self.output_type = 'grayscale'

        # Set up UI controls
        self.create_controls()
        
        # Display the frame in the parent widget
        self.pack(fill=tk.BOTH, expand=True)

    def create_controls(self):
        """Set up controls for point size, ASCII range, and output type selection."""
        # Point Size Control
        tk.Label(self, text="Point Size:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.point_size_control = DeltaControl(self, label="Point Size", initial_value=self.point_size, step=1,
                                               min_value=1, max_value=100, callback=self.update_point_size)
        self.point_size_control.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        # ASCII Range Entry
        tk.Label(self, text="ASCII Range:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.ascii_range_entry = tk.Entry(self)
        self.ascii_range_entry.insert(0, "32-127")
        self.ascii_range_entry.grid(row=1, column=1, sticky="w", padx=5, pady=5)

        # Output Type Selection
        tk.Label(self, text="Output Type:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.output_type_var = tk.StringVar(value="grayscale")
        output_options = ["grayscale", "thresholded", "quantized"]
        for idx, option in enumerate(output_options):
            tk.Radiobutton(self, text=option.title(), variable=self.output_type_var, value=option).grid(row=2, column=idx+1, sticky="w", padx=5, pady=5)

        # Generate Button
        self.generate_button = tk.Button(self, text="Generate", command=self.generate_font_image)
        self.generate_button.grid(row=3, column=0, columnspan=3, pady=10)

    def update_point_size(self, size):
        """Update the point size when changed via DeltaControl."""
        self.point_size = size

    def generate_font_image(self):
        """Generate the font image and metadata based on user-selected options."""
        # Parse ASCII range
        try:
            ascii_start, ascii_end = map(int, self.ascii_range_entry.get().split("-"))
            self.ascii_range = (ascii_start, ascii_end)
        except ValueError:
            print("Invalid ASCII range. Please use 'start-end' format.")
            return
        
        # Render and measure characters
        char_images, max_width, max_height = self.render_characters()

        # Create the font image based on output type
        if self.output_type_var.get() == 'thresholded':
            processed_images = [self.apply_threshold(img, threshold=128) for img in char_images.values()]
        elif self.output_type_var.get() == 'quantized':
            processed_images = [self.quantize_image(img) for img in char_images.values()]
        else:
            processed_images = list(char_images.values())

        # Generate the master image
        font_image = create_master_image(processed_images, max_width, max_height, self.ascii_range)
        
        # Save the font image and metadata
        self.save_font_image_and_metadata(font_image, max_width, max_height)

    def render_characters(self):
        """Render each character within the specified ASCII range and return images with max dimensions."""
        char_images = {}
        max_width, max_height = 0, 0
        font = ImageFont.truetype(self.ttf_path, self.point_size)

        for char_code in range(self.ascii_range[0], self.ascii_range[1] + 1):
            char = chr(char_code)
            char_img = Image.new("L", (256, 256), color=0)  # Black background
            draw = ImageDraw.Draw(char_img)
            draw.text((0, 0), char, font=font, fill=255)  # White character
            bbox = char_img.getbbox()

            if bbox:
                width, height = bbox[2], bbox[3]
                max_width, max_height = max(max_width, width), max(max_height, height)
                cropped_img = char_img.crop(bbox)
                char_images[char_code] = cropped_img

        return char_images, max_width, max_height

    def apply_threshold(self, image, threshold=128):
        """Apply a threshold to a grayscale image to convert it to binary (black and white)."""
        return image.point(lambda p: 255 if p > threshold else 0, mode="1")

    def quantize_image(self, image):
        """Quantize a grayscale image to a 4-level palette."""
        return image.quantize(colors=4)

    def save_font_image_and_metadata(self, font_image, max_width, max_height):
        """Save the generated font image and metadata."""
        output_dir = filedialog.askdirectory(title="Select Directory to Save Font Image")
        if not output_dir:
            return  # User canceled the directory selection

        # Save font image
        font_name = os.path.splitext(os.path.basename(self.ttf_path))[0]
        output_image_path = os.path.join(output_dir, f"{font_name}_{max_width}x{max_height}.png")
        font_image.save(output_image_path)
        print(f"Font image saved: {output_image_path}")

        # Save metadata
        metadata_dir = filedialog.askdirectory(title="Select Directory to Save Metadata")
        generate_metadata_file(max_width, max_height, self.point_size, metadata_dir)
        print("Metadata generated successfully.")
