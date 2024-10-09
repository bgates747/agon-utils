import os
import tkinter as tk
from tkinter import filedialog, messagebox, Toplevel
from PIL import Image
import configparser
from FontConfigEditor import FontConfigEditor
from AgonFont import read_font_file, create_font_image, make_font

class FileManager:
    def __init__(self, app_reference):
        self.app_reference = app_reference  # Store reference to the main app
    
    def parse_font_filename(self, file_path):
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
        """Load font metadata from a .ini file and return as a dictionary."""
        config = configparser.ConfigParser()
        config.read(ini_filepath)

        # Construct the font configuration dictionary directly from the .ini file
        font_config = {
            'font_name': config.get('font', 'font_name'),
            'font_variant': config.get('font', 'font_variant'),
            'font_width': config.getint('font', 'font_width'),
            'font_height': config.getint('font', 'font_height'),
            'offset_left': config.getint('font', 'offset_left'),
            'offset_top': config.getint('font', 'offset_top'),
            'offset_width': config.getint('font', 'offset_width'),
            'offset_height': config.getint('font', 'offset_height'),
            'ascii_range_start': config.getint('font', 'ascii_range_start'),
            'ascii_range_end': config.getint('font', 'ascii_range_end')
        }

        return font_config

    def save_font_metadata(self, font_config, ini_file_path):
        """Save the provided font configuration dictionary to an .ini file."""
        
        config = configparser.ConfigParser()
        config['font'] = {
            'font_name': font_config['font_name'],
            'font_variant': font_config['font_variant'],
            'font_width': str(font_config['font_width']),
            'font_height': str(font_config['font_height']),
            'offset_left': str(font_config['offset_left']),
            'offset_top': str(font_config['offset_top']),
            'offset_width': str(font_config['offset_width']),
            'offset_height': str(font_config['offset_height']),
            'ascii_range_start': str(font_config['ascii_range_start']),
            'ascii_range_end': str(font_config['ascii_range_end'])
        }

        with open(ini_file_path, 'w') as configfile:
            config.write(configfile)
            print(f"Metadata saved successfully to {ini_file_path}")

    def get_open_filename(self):
        """Handle the Open action."""
        most_recent_open_directory = self.app_reference.config_manager.get_most_recent_open_directory()
        file_path = filedialog.askopenfilename(
            title="Open File",
            filetypes=(("All Files", "*.*"), ("PNG Images", "*.png"), ("Font Files", "*.font")),
            initialdir=most_recent_open_directory
        )
        self.open_file(file_path)
    
    def open_file(self, file_path):
        if file_path:
            # Initialize font_config by loading from .ini or deriving from the filename
            ini_filepath = file_path + '.ini'
            if os.path.exists(ini_filepath):
                font_config = self.load_font_metadata_from_ini(ini_filepath)
            else:
                font_config = self.parse_font_filename(file_path)
            
            file_extension = os.path.splitext(file_path)[1].lower()
            if file_extension == '.png':
                modified, font_config, font_img = self.open_png_image(file_path, font_config)
            elif file_extension == '.font':
                modified, font_config, font_img = self.open_font_file(file_path, font_config)
            else:
                messagebox.showerror("Unsupported File", f"The file type {file_extension} is not supported.")
                return

            if font_config:
                # Set application font metadata based on the finalized configuration
                self.app_reference.set_font_metadata(font_config)

                # Save font metadata directly to the .ini file
                ini_filepath = file_path + '.ini'
                self.save_font_metadata(font_config, ini_filepath)
                print("Saved font metadata: ", font_config)
                
                # Update the most recent directory and file path in the config
                new_most_recent_open_directory = os.path.dirname(file_path)
                self.app_reference.config_manager.set_most_recent_open_directory(new_most_recent_open_directory)
                self.app_reference.config_manager.set_most_recent_file(file_path)

                # Load image into the ImageDisplayWidget
                self.app_reference.image_display.load_image(font_img)

                # Initialize the editor grid with the loaded font configuration
                self.app_reference.editor_widget.initialize_grid()

                # Trigger the click on ASCII 'A' after setup
                self.app_reference.image_display.trigger_click_on_ascii_code(ord('A'))

    def open_config_editor_popup(self, font_config):
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

        # Retrieve the updated configuration from the editor after the popup is closed
        return config_editor.result

    def open_png_image(self, file_path, font_config):
        """Load the image and associated font metadata."""
        
        # Load the image
        font_image = Image.open(file_path)

        # Use the helper function to finalize the configuration
        modified, final_config = self.validate_font_config(font_image, font_config)
        
        # Return font image and metadata
        return modified, final_config, font_image

    def open_font_file(self, file_path, font_config):
        """Load font configuration and character images from a .font file, allowing user review of the configuration."""

        char_width = font_config['font_width']
        char_height = font_config['font_height']
        ascii_range = (font_config['ascii_range_start'], font_config['ascii_range_end'])
        print(f'Loading font file: {file_path} with width={char_width}, height={char_height}, range={ascii_range}')

        # Read character images from the .font file with the specified configuration
        char_images = read_font_file(
            font_filepath=file_path,
            char_width=char_width,
            char_height=char_height,
            ascii_range=ascii_range
        )

        # Create the composite font image from the individual character images
        font_image = create_font_image(
            char_images=char_images,
            char_width=char_width,
            char_height=char_height,
            chars_per_row=16  # Explicitly set characters per row for the grid layout
        )

        # Use the helper function to finalize the configuration
        modified, final_config = self.validate_font_config(font_image, font_config)
        return modified, final_config, font_image

    def save_file(self):
        """Handle the Save action for saving both the image and metadata."""

        # Retrieve font metadata to construct the default save filename
        font_config = self.app_reference.get_font_metadata()
        default_name = f"{font_config['font_name']}_{font_config['font_variant']}_{font_config['font_width']}x{font_config['font_height']}"

        # Ask user for filename, setting default name and directory
        file_path = filedialog.asksaveasfilename(
            title="Save As",
            defaultextension=".font",
            filetypes=(("PNG Images", "*.png"), ("Font Files", "*.font"), ("All Files", "*.*")),
            initialdir=self.app_reference.config_manager.get_most_recent_save_directory(),
            initialfile=default_name  # Set default filename based on metadata
        )

        if not file_path:
            return  # User canceled the save

        # Check if an extension exists and default to .font if not
        _, ext = os.path.splitext(file_path)
        if not ext:
            ext = '.font'
            file_path = f"{file_path}{ext}"

        if ext == '.png':
            self.save_as_png(file_path, font_config)
        elif ext == '.font':
            self.save_as_font(file_path, font_config)
        else:
            messagebox.showerror("Unsupported File Type", f"Unsupported file extension: {ext}")

        # Update most recent save directory with the chosen directory
        self.app_reference.config_manager.set_most_recent_save_directory(os.path.dirname(file_path))

    def save_as_png(self, file_path, font_config):
        """Save the current image as a PNG with accompanying metadata."""
        # Define paths for .png and .ini files based on selected filename
        png_file_path = file_path if file_path.endswith('.png') else f"{file_path}.png"
        ini_file_path = f"{os.path.splitext(file_path)[0]}.ini"

        # Save image and metadata
        self.app_reference.image_display.original_image.save(png_file_path)
        self.save_font_metadata(font_config, ini_file_path)

        messagebox.showinfo("Save Successful", f"PNG image and metadata saved successfully to {png_file_path} and {ini_file_path}")

    def save_as_font(self, file_path, font_config):
        """Save the current font data as a .font file."""
        font_width = font_config['font_width']
        font_height = font_config['font_height']
        offset_left = font_config['offset_left']
        offset_top = font_config['offset_top']
        offset_width = font_config['offset_width']
        offset_height = font_config['offset_height']
        ascii_range = (font_config['ascii_range_start'], font_config['ascii_range_end'])
        src_image = self.app_reference.image_display.original_image

        make_font(src_image, file_path, font_width, font_height, offset_left, offset_top, offset_width, offset_height, ascii_range)

        messagebox.showinfo("Save Successful", f"Font file saved successfully to {file_path}")