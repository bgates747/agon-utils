import tkinter as tk
from PIL import Image, ImageDraw, ImageFont
from CustomWidgets import DeltaControl
from AgonFont import create_font_image

class TTFWidget(tk.Frame):
    """A widget for generating font images and metadata from a .ttf file with adjustable options."""
    
    # Default values for the widget
    DEFAULT_POINT_SIZE = 16
    DEFAULT_ASCII_RANGE = (32, 127)
    DEFAULT_OUTPUT_TYPE = 'thresholded'

    def __init__(self, parent, app_reference, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.app_reference = app_reference
        self.point_size = self.DEFAULT_POINT_SIZE  # Initialize with default point size
        self.ascii_range = self.DEFAULT_ASCII_RANGE
        self.output_type = self.DEFAULT_OUTPUT_TYPE
        self.ttf_path = None  # Filepath for the currently loaded TTF file

        # Set up UI controls
        self.create_controls()
        
        # Display the frame in the parent widget
        self.pack(fill=tk.BOTH, expand=True)

    def read_ttf_file(self, file_path, point_size=DEFAULT_POINT_SIZE):
        """Sets the TTF file path and initializes default settings."""
        self.ttf_path = file_path
        self.point_size_control.set_value(point_size)
        self.point_size = point_size

        # Generate default font image and metadata
        font_config, font_image = self.generate_font_image()

        # Pass results to main app
        return font_config, font_image

    def create_controls(self):
        """Set up controls for point size, ASCII range, and output type selection."""
        # Point Size Control
        tk.Label(self, text="Point Size:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.point_size_control = DeltaControl(self, label="Point Size", initial_value=self.DEFAULT_POINT_SIZE, step=1,
                                               min_value=1, max_value=100, callback=self.update_point_size)
        self.point_size_control.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        # ASCII Range Entry
        tk.Label(self, text="ASCII Range:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.ascii_range_entry = tk.Entry(self)
        # Set the default ASCII range
        self.ascii_range_entry.insert(0, f"{self.DEFAULT_ASCII_RANGE[0]}-{self.DEFAULT_ASCII_RANGE[1]}")
        self.ascii_range_entry.grid(row=1, column=1, sticky="w", padx=5, pady=5)

        # Output Type Selection
        tk.Label(self, text="Output Type:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.output_type_var = tk.StringVar(value=self.DEFAULT_OUTPUT_TYPE)
        output_options = ["grayscale", "thresholded", "quantized"]
        for idx, option in enumerate(output_options):
            tk.Radiobutton(self, text=option.title(), variable=self.output_type_var, value=option).grid(row=2, column=idx+1, sticky="w", padx=5, pady=5)

        # Generate Button
        self.generate_button = tk.Button(self, text="Generate", command=self.generate_and_return)
        self.generate_button.grid(row=3, column=0, columnspan=3, pady=10)

    def generate_and_return(self):
        """Generates the font image and metadata, and passes it to the main app."""
        font_config, font_image = self.generate_font_image()
        self.app_reference.font_config_editor.set_config(font_config)
        self.app_reference.image_display.load_image(font_image)
        self.app_reference.editor_widget.initialize_grid()

    def update_point_size(self, size):
        """Update the point size when changed via DeltaControl."""
        self.point_size = size

    def generate_font_image(self):
        """Generate the font image and metadata based on user-selected options."""
        if not self.ttf_path:
            print("No TTF file loaded.")
            return None, None

        # Parse ASCII range
        try:
            ascii_start, ascii_end = map(int, self.ascii_range_entry.get().split("-"))
            self.ascii_range = (ascii_start, ascii_end)
        except ValueError:
            print("Invalid ASCII range. Please use 'start-end' format.")
            return None, None
        
        # Render and measure characters
        char_images, max_width, max_height = self.render_characters()

        # Create the font image based on output type
        if self.output_type_var.get() == 'thresholded':
            char_images = [self.apply_threshold(img, threshold=128) for img in char_images.values()]
        elif self.output_type_var.get() == 'quantized':
            char_images = [self.quantize_image(img) for img in char_images.values()]
        else:
            char_images = list(char_images.values())

        curr_config = self.app_reference.font_config_editor.get_config()
        font_name = curr_config.get('font_name', 'ttf_font')
        font_variant = curr_config.get('font_variant', 'ttf_variant')

        # Create the font configuration
        font_config = {
            'font_name': font_name,
            'font_variant': font_variant,
            'font_width': max_width,
            'font_height': max_height,
            'offset_left': 0,
            'offset_top': 0,
            'offset_width': 0,
            'offset_height': 0,
            'ascii_range_start': ascii_start,
            'ascii_range_end': ascii_end
        }

        # Generate the master image
        font_image = create_font_image(char_images, font_config, chars_per_row=16)
        
        return font_config, font_image

    def render_characters(self):
        """
        Render each character within the specified ASCII range and return images cropped to max dimensions.
        """
        char_images = {}
        max_width, max_height = 0, 0
        font = ImageFont.truetype(self.ttf_path, self.point_size)

        # First Pass: Render each character and calculate max width and height without altering the original images
        for char_code in range(self.ascii_range[0], self.ascii_range[1] + 1):
            char = chr(char_code)
            char_img = Image.new("L", (64, 64), color=0)  # Black background
            draw = ImageDraw.Draw(char_img)
            draw.text((0, 0), char, font=font, fill=255)  # White character
            bbox = char_img.getbbox()

            if bbox:
                width, height = bbox[2], bbox[3]
                max_width = max(max_width, width)
                max_height = max(max_height, height)

            # Store the original unaltered image for the second pass
            char_images[char_code] = char_img

        # Second Pass: Crop each image to max width and height determined from the first pass
        cropped_images = {}
        for char_code, char_img in char_images.items():
            cropped_img = char_img.crop((0, 0, max_width, max_height))
            cropped_images[char_code] = cropped_img

        return cropped_images, max_width, max_height

    def apply_threshold(self, image, threshold=128):
        """Apply a threshold to a grayscale image to convert it to binary (black and white)."""
        return image.point(lambda p: 255 if p > threshold else 0, mode="1")

    def quantize_image(self, image):
        """Quantize a grayscale image to a 4-level palette."""
        return image.quantize(colors=4)
