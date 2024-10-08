import os
import tkinter as tk
from tkinter import filedialog, messagebox, Toplevel
from PIL import Image
import configparser
from FontConfigEditor import FontConfigEditor
from AgonFont import read_font_file, create_font_image

class FileManager:
    def __init__(self, app_reference):
        self.app_reference = app_reference  # Store reference to the main app

    def parse_font_config_from_image_path(self, file_path):
        """Parse font configuration from an image file path and return as a dictionary."""
        
        # Extract parts from the file path
        path_parts = file_path.split(os.sep)
        
        # Font name is assumed to be the directory two levels up
        font_name = path_parts[-3] if len(path_parts) >= 3 else "unknown_font"
        
        # Font variant is the directory just above the file
        font_variant = path_parts[-2] if len(path_parts) >= 2 else "Regular"
        
        # Extract font dimensions from the filename (e.g., 8_bit_fortress_9x15.png)
        filename = os.path.splitext(os.path.basename(file_path))[0]
        width, height = 0, 0
        if '_' in filename and 'x' in filename:
            dimensions_part = filename.split('_')[-1]
            try:
                width, height = map(int, dimensions_part.split('x'))
            except ValueError:
                print("Warning: Unable to parse width and height from filename.")
        
        ascii_range_start = int(self.app_reference.config_manager.get_setting('ascii_range_start', '32'))
        ascii_range_end = int(self.app_reference.config_manager.get_setting('ascii_range_end', '127'))

        config = {
            'font_name': font_name,
            'font_variant': font_variant,
            'font_width': width,
            'font_height': height,
            'offset_left': 0,
            'offset_top': 0,
            'offset_width': 0,
            'offset_height': 0,
            'ascii_range_start': ascii_range_start,
            'ascii_range_end': ascii_range_end
        }
        
        return config
    
    def parse_font_config_from_font_filepath(self, file_path):
        """Parse font configuration from a font filename and return as a dictionary."""
        # Remove the path from the filename
        file_name = os.path.basename(file_path)
        
        # Remove the file extension to isolate the main part of the filename
        base_name = os.path.splitext(file_name)[0]
        
        # Split the filename into parts by underscores
        parts = base_name.split('_')
        
        # Extract width and height from the last part
        width, height = 0, 0
        try:
            dimensions_part = parts[-1]  # The final part should contain dimensions like "8x9"
            width, height = map(int, dimensions_part.split('x'))
        except ValueError:
            print("Warning: Unable to parse width and height from filename.")

        # Extract variant and font name
        font_variant = parts[-2] if len(parts) >= 2 else "Regular"
        font_name = '_'.join(parts[:-2]) if len(parts) > 2 else "unknown_font"
        
        # Retrieve ASCII range from the config manager with fallback
        ascii_range_start = int(self.app_reference.config_manager.get_setting('ascii_range_start', '32'))
        ascii_range_end = int(self.app_reference.config_manager.get_setting('ascii_range_end', '127'))

        config = {
            'font_name': font_name,
            'font_variant': font_variant,
            'font_width': width,
            'font_height': height,
            'offset_left': 0,
            'offset_top': 0,
            'offset_width': 0,
            'offset_height': 0,
            'ascii_range_start': ascii_range_start,
            'ascii_range_end': ascii_range_end
        }
        
        return config

    def validate_font_config(self, image, font_config):
        """Validate and adjust font config based on image dimensions."""
        
        # Calculate expected image dimensions based on font config
        expected_width = font_config['font_width'] * 16
        ascii_range_start = font_config['ascii_range_start']
        ascii_range_end = font_config['ascii_range_end']
        ascii_range_count = ascii_range_end - ascii_range_start + 1
        expected_height = font_config['font_height'] * ((ascii_range_count + 15) // 16)
        
        # If dimensions match, return unmodified
        if image.size == (expected_width, expected_height):
            return False, font_config  # No modifications needed

        # First try: default ASCII range from config.ini
        default_ascii_range = self.app_reference.config_manager.get_default_ascii_range()
        possible_ranges = [default_ascii_range, (32, 127), (0, 127), (0, 255)]
        
        for start, end in possible_ranges:
            range_count = end - start + 1
            adjusted_height = font_config['font_height'] * ((range_count + 15) // 16)
            
            if image.size == (expected_width, adjusted_height):
                # Update font config with the corrected ASCII range
                modified_config = font_config.copy()
                modified_config['ascii_range_start'] = start
                modified_config['ascii_range_end'] = end
                return True, modified_config  # Modified with corrected ASCII range
        
        # If no match, return modified = True and an empty config
        return True, {}

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

    def get_open_filename(self):
        """Handle the Open action."""
        most_recent_directory = self.app_reference.config_manager.get_most_recent_directory()
        file_path = filedialog.askopenfilename(
            title="Open File",
            filetypes=(("PNG Images", "*.png"), ("Font Files", "*.font"), ("All Files", "*.*")),
            initialdir=most_recent_directory
        )
        self.open_file(file_path)
    
    def open_file(self, file_path):
        if file_path:
            file_extension = os.path.splitext(file_path)[1].lower()
            if file_extension == '.png':
                self.open_png_image(file_path)
            elif file_extension == '.font':
                self.open_font_file(file_path)
            else:
                messagebox.showerror("Unsupported File", f"The file type {file_extension} is not supported.")

    def open_png_image(self, file_path):
        """Load the image and associated font metadata."""
        ini_filepath = file_path + '.ini'
        
        # Initialize font_config by loading from .ini or deriving from the filename
        if os.path.exists(ini_filepath):
            self.load_font_metadata_from_ini(ini_filepath)
            font_config = {
                'font_name': self.app_reference.font_name,
                'font_variant': self.app_reference.font_variant,
                'font_width': self.app_reference.font_width,
                'font_height': self.app_reference.font_height,
                'offset_left': self.app_reference.offset_left,
                'offset_top': self.app_reference.offset_top,
                'offset_width': self.app_reference.offset_width,
                'offset_height': self.app_reference.offset_height,
                'ascii_range_start': self.app_reference.ascii_range[0],
                'ascii_range_end': self.app_reference.ascii_range[1]
            }
        else:
            font_config = self.parse_font_config_from_image_path(file_path)
            self.apply_font_config(font_config)
        
        # Load the image and validate dimensions against metadata
        image = Image.open(file_path)
        modified, validated_config = self.validate_font_config(image, font_config)

        # Check for discrepancies and open config editor if necessary
        if modified:
            if validated_config:
                font_config.update(validated_config)  # Use suggested values if found
            else:
                font_config = {}  # Empty config if no valid settings were inferred

            self.open_config_editor_popup(font_config, ini_filepath)
        
        # Reload metadata after possible adjustments from FontConfigEditor
        self.apply_font_config(font_config)
        
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
        
        # Update the most recent directory
        new_most_recent_directory = os.path.dirname(file_path)
        self.app_reference.config_manager.set_most_recent_directory(new_most_recent_directory)

        # Save the most recent file path to config.ini
        self.app_reference.config_manager.set_most_recent_file(file_path)

    def open_config_editor_popup(self, font_config, ini_filepath=None):
        """Open the FontConfigEditor as a modal popup to adjust metadata."""
        # Create a Toplevel window to act as a modal dialog
        popup = Toplevel(self.app_reference)
        popup.title("Font Configuration Editor")
        popup.grab_set()  # Set the popup as modal

        # Instantiate the FontConfigEditor within the popup with pre-populated config
        config_editor = FontConfigEditor(popup)
        config_editor.set_config(font_config)  # Populate with font_config values
        config_editor.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Wait for the popup window to close before proceeding
        popup.wait_window(popup)

        # Reload updated metadata from file only if ini_filepath is provided
        if ini_filepath:
            self.load_font_metadata_from_ini(ini_filepath)
        else:
            # Re-apply the modified config from the editor if no .ini file exists
            modified_config = config_editor.get_config()
            self.apply_font_config(modified_config)

    def apply_font_config(self, font_config):
        """Apply font configuration values to the app."""
        self.app_reference.font_name = font_config.get('font_name', "unknown_font")
        self.app_reference.font_variant = font_config.get('font_variant', "Regular")
        self.app_reference.font_width = font_config.get('font_width', 0)
        self.app_reference.font_height = font_config.get('font_height', 0)
        self.app_reference.offset_left = font_config.get('offset_left', 0)
        self.app_reference.offset_top = font_config.get('offset_top', 0)
        self.app_reference.offset_width = font_config.get('offset_width', 0)
        self.app_reference.offset_height = font_config.get('offset_height', 0)
        self.app_reference.ascii_range = (
            font_config.get('ascii_range_start', 32),
            font_config.get('ascii_range_end', 127)
        )

    def open_font_file(self, file_path):
        """Load font configuration and character images from a .font file, allowing user review of the configuration."""
        
        # Parse font file for font name, variant, width, and height
        font_config = self.parse_font_config_from_font_filepath(file_path)
        char_width = font_config['font_width']
        char_height = font_config['font_height']
        
        # Read character images and create a composite font image from the .font file
        char_images = read_font_file(file_path, char_width, char_height)
        font_image = create_font_image(char_images, char_width, char_height)

        # Validate the font configuration against the generated font image dimensions
        modified, validated_config = self.validate_font_config(font_image, font_config)

        # Update font configuration if suggested adjustments are available
        if modified and validated_config:
            font_config.update(validated_config)  # Use suggested values if found

        # Always open the configuration editor for user review
        self.open_config_editor_popup(font_config, ini_filepath=None)  # No ini file, using in-memory config

        # Re-apply any user-modified configuration values
        self.apply_font_config(font_config)

        # Set font metadata in the ImageDisplayWidget
        self.app_reference.image_display.set_font_metadata(
            self.app_reference.font_width,
            self.app_reference.font_height,
            self.app_reference.ascii_range
        )

        # Initialize editor widget grid dimensions based on font metadata
        self.app_reference.editor_widget.initialize_grid(
            self.app_reference.font_width,
            self.app_reference.font_height
        )

        # Load font image into the ImageDisplayWidget without saving/opening a PNG file
        self.app_reference.image_display.load_image(font_image)

        # Trigger the click on ASCII 'A' after setup (optional, for demonstration)
        self.app_reference.image_display.trigger_click_on_ascii_code(ord('A'))

        # Update the most recent directory for subsequent actions
        new_most_recent_directory = os.path.dirname(file_path)
        self.app_reference.config_manager.set_most_recent_directory(new_most_recent_directory)

        # Save the most recent file path to config.ini
        self.app_reference.config_manager.set_most_recent_file(file_path)

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
