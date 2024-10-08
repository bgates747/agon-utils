import os
from tkinter import filedialog, messagebox
import configparser
from PIL import Image

class FileManager:
    def __init__(self, app_reference):
        self.app_reference = app_reference  # Store reference to the main app

    def load_image_and_metadata(self, file_path):
        """Load the image and associated font metadata."""
        ini_filepath = file_path + '.ini'

        # Load metadata from .ini file if it exists; otherwise, derive it from filename
        if os.path.exists(ini_filepath):
            self.load_font_metadata_from_ini(ini_filepath)
        else:
            self.derive_font_metadata_from_filename(file_path)

        # Load the image and validate dimensions against metadata
        image = Image.open(file_path)
        img_width, img_height = image.size

        expected_width = self.app_reference.font_width * 16
        ascii_range = self.app_reference.ascii_range
        expected_height = self.app_reference.font_height * ((ascii_range[1] - ascii_range[0]) // 16 + 1)

        if img_width != expected_width or img_height != expected_height:
            response = messagebox.askyesnocancel(
                "Image Size Mismatch",
                f"The image dimensions {img_width}x{img_height} do not match the expected {expected_width}x{expected_height}.\n"
                "Would you like to crop or enlarge the image to fit the grid?"
            )
            if response is None:  # Cancel operation
                return
            elif response:  # Enlarge the image
                image = self.app_reference.image_display.enlarge_image(image, expected_width, expected_height)
            else:  # Crop the image
                image = self.app_reference.image_display.crop_image(image, expected_width, expected_height)

        # Pass font metadata to ImageDisplayWidget
        self.app_reference.image_display.set_font_metadata(
            self.app_reference.font_width,
            self.app_reference.font_height,
            self.app_reference.ascii_range
        )

        # Initialize editor widget grid dimensions
        self.app_reference.editor_widget.initialize_grid(
            self.app_reference.font_width,
            self.app_reference.font_height
        )

        # Load image into the ImageDisplayWidget
        self.app_reference.image_display.load_image(image)

        # Trigger the click on ASCII 'A' after setup
        self.app_reference.image_display.trigger_click_on_ascii_code(ord('A'))

        # Save derived or loaded font metadata directly to the .ini file
        self.save_font_metadata(ini_filepath)
        print("Saved font metadata:", self.get_font_metadata())

    def load_font_metadata_from_ini(self, ini_filepath):
        """Load font metadata from a .ini file and update the application state."""
        config = configparser.ConfigParser()
        config.read(ini_filepath)

        # Update application state with loaded metadata or defaults from config manager
        self.app_reference.font_name = config.get('font', 'font_name', fallback=self.app_reference.config_manager.get_setting('font_name', 'default_font'))
        self.app_reference.font_variant = config.get('font', 'font_variant', fallback=self.app_reference.config_manager.get_setting('font_variant', 'Regular'))
        self.app_reference.font_width = config.getint('font', 'font_width', fallback=int(self.app_reference.config_manager.get_setting('default_font_width', '8')))
        self.app_reference.font_height = config.getint('font', 'font_height', fallback=int(self.app_reference.config_manager.get_setting('default_font_height', '11')))
        self.app_reference.offset_left = config.getint('font', 'offset_left', fallback=int(self.app_reference.config_manager.get_setting('default_offset_left', '0')))
        self.app_reference.offset_top = config.getint('font', 'offset_top', fallback=int(self.app_reference.config_manager.get_setting('default_offset_top', '0')))
        self.app_reference.offset_width = config.getint('font', 'offset_width', fallback=int(self.app_reference.config_manager.get_setting('default_offset_width', '0')))
        self.app_reference.offset_height = config.getint('font', 'offset_height', fallback=int(self.app_reference.config_manager.get_setting('default_offset_height', '0')))
        
        # For ASCII range, retrieve both start and end with defaults from config manager
        self.app_reference.ascii_range = (
            config.getint('font', 'ascii_range_start', fallback=int(self.app_reference.config_manager.get_setting('ascii_range_start', '32'))),
            config.getint('font', 'ascii_range_end', fallback=int(self.app_reference.config_manager.get_setting('ascii_range_end', '127')))
        )

    def derive_font_metadata_from_filename(self, file_path):
        """Derive font metadata from the file path if no .ini file exists."""
        path_parts = file_path.split(os.sep)
        self.app_reference.font_variant = path_parts[-2]  # Variant from folder name
        self.app_reference.font_name = path_parts[-3]      # Font name from higher folder

        # Extract font dimensions from the filename (e.g., 8_bit_fortress_9x8.png)
        filename = os.path.splitext(os.path.basename(file_path))[0]
        if '_' in filename and 'x' in filename:
            font_dimensions = filename.split('_')[-1]
            width, height = map(int, font_dimensions.split('x'))
            self.app_reference.font_width = width
            self.app_reference.font_height = height

    def get_font_metadata(self):
        """Retrieve font metadata from the application state."""
        return {
            'font_name': self.app_reference.font_name,
            'font_variant': self.app_reference.font_variant,
            'font_width': self.app_reference.font_width,
            'font_height': self.app_reference.font_height,
            'offset_left': self.app_reference.offset_left,
            'offset_top': self.app_reference.offset_top,
            'offset_width': self.app_reference.offset_width,
            'offset_height': self.app_reference.offset_height,
            'ascii_range': self.app_reference.ascii_range
        }

    def save_font_metadata(self, ini_file_path):
        """Save the current font metadata from the application state to an .ini file."""
        font_metadata = self.get_font_metadata()

        config = configparser.ConfigParser()
        config['font'] = {
            'font_name': font_metadata['font_name'],
            'font_variant': font_metadata['font_variant'],
            'font_width': str(font_metadata['font_width']),
            'font_height': str(font_metadata['font_height']),
            'offset_left': str(font_metadata['offset_left']),
            'offset_top': str(font_metadata['offset_top']),
            'offset_width': str(font_metadata['offset_width']),
            'offset_height': str(font_metadata['offset_height']),
            'ascii_range_start': str(font_metadata['ascii_range'][0]),
            'ascii_range_end': str(font_metadata['ascii_range'][1])
        }

        with open(ini_file_path, 'w') as configfile:
            config.write(configfile)
            print(f"Metadata saved successfully to {ini_file_path}")

    def open_file(self):
        """Handle the Open action."""
        most_recent_directory = self.app_reference.config_manager.get_most_recent_directory()
        file_path = filedialog.askopenfilename(
            title="Open File",
            filetypes=(("PNG Images", "*.png"), ("Font Files", "*.font"), ("All Files", "*.*")),
            initialdir=most_recent_directory
        )

        if file_path:
            file_extension = os.path.splitext(file_path)[1].lower()
            if file_extension == '.png':
                self.open_png_image(file_path)
            elif file_extension == '.font':
                self.open_font_file(file_path)
            else:
                messagebox.showerror("Unsupported File", f"The file type {file_extension} is not supported.")

    def open_png_image(self, file_path):
        """Load and display the PNG image along with its metadata."""
        self.load_image_and_metadata(file_path)
        
        # Update the most recent directory
        new_most_recent_directory = os.path.dirname(file_path)
        self.app_reference.config_manager.set_most_recent_directory(new_most_recent_directory)

        # Save the most recent file path to config.ini
        self.app_reference.config_manager.set_most_recent_file(file_path)


    def open_font_file(self, file_path):
        """Stub for handling opening a .font file."""
        messagebox.showinfo("Not Implemented", "Opening .font files is not implemented yet.")

    def save_file(self):
        """Handle the Save action for saving both the image and metadata."""
        file_path = filedialog.asksaveasfilename(
            title="Save As",
            defaultextension=".png",
            filetypes=(("PNG Images", "*.png"), ("Font Files", "*.font"), ("All Files", "*.*")),
            initialdir=self.app_reference.config_manager.get_most_recent_directory()
        )

        if not file_path:
            return  # User canceled the save

        # Define paths for both .png and .ini files
        png_file_path = file_path if file_path.endswith('.png') else f"{file_path}.png"
        ini_file_path = f"{file_path}.ini"

        # Save image and metadata
        self.save_png_image(png_file_path)
        self.save_font_metadata(ini_file_path)

    def save_png_image(self, file_path):
        """Save the current image as a PNG."""
        self.app_reference.image_display.original_image.save(file_path)
        new_most_recent_directory = os.path.dirname(file_path)
        self.app_reference.config_manager.set_most_recent_directory(new_most_recent_directory)
        messagebox.showinfo("Save Successful", f"Image saved successfully to {file_path}")
