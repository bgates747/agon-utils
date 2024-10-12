import os
from tkinter import filedialog, messagebox
import configparser
from AgonFont import read_font, make_font

class FileManager:
    """Handles file operations like loading, saving, and parsing font files for the Agon Font Editor."""

    def __init__(self, app_reference):
        self.app_reference = app_reference  # Store reference to the main app

    # =========================================================================
    # Configuration Parsing and Metadata Handling
    # =========================================================================

    def parse_font_filename(self, file_path):
        """Parse font configuration from a font filename and return as a dictionary."""
        file_name = os.path.basename(file_path)
        base_name, ext = os.path.splitext(file_name)
        
        # Check extensions we do parsing for
        if ext not in {'.png', '.font'}:
            # Return minimal configuration for unsupported file types
            return {
                'font_name': base_name,
                'font_variant': "",
            }
        
        # Parse details from .png or .font file name
        parts = base_name.split('_')
        try:
            dimensions_part = parts[-1]
            width, height = map(int, dimensions_part.split('x'))
        except ValueError:
            print("Warning: Unable to parse width and height from filename.")
            width, height = 0, 0

        font_variant = parts[-2] if len(parts) >= 2 else "Regular"
        font_name = '_'.join(parts[:-2]) if len(parts) > 2 else "unknown_font"

        return {
            'font_name': font_name,
            'font_variant': font_variant,
            'font_width': width,
            'font_height': height,
        }

    def load_font_metadata_from_ini(self, ini_filepath):
        """Load font metadata from a .ini file, converting values based on types in the corresponding .cfg file."""
        ini_config = configparser.ConfigParser()
        ini_config.read(ini_filepath)
        font_section = ini_config['font']
        
        # Derive the font type from the filename pattern
        base_name = os.path.basename(ini_filepath)
        font_type = base_name.split('.')[-2]  # Get the part before '.ini' as the font type
        script_dir = os.path.dirname(os.path.abspath(__file__))
        cfg_filepath = os.path.join(script_dir, 'data', f'font_{font_type}.cfg')
        
        # Load the .cfg file to get data types and check if it loaded correctly
        cfg_config = configparser.ConfigParser()
        if not cfg_config.read(cfg_filepath):
            print(f"Error: Failed to read .cfg file at {cfg_filepath}")

        font_metadata = {}
        for key, value in font_section.items():
            if cfg_config.has_section(key):
                datatype = cfg_config.get(key, 'type', fallback='string').lower()
                if datatype == 'int':
                    font_metadata[key] = int(value)
                elif datatype == 'float':
                    font_metadata[key] = float(value)
                elif datatype == 'bool':
                    font_metadata[key] = value.lower() in ['true', '1', 'yes']
                else:
                    font_metadata[key] = value
            else:
                print(f"Warning: '{key}' not found as a section in .cfg file. Defaulting to string.")
                font_metadata[key] = value
        return font_metadata

    def save_font_metadata(self, font_config, ini_file_path):
        """Save the provided font configuration dictionary to an .ini file."""
        config = configparser.ConfigParser()
        config['font'] = {key: str(value) for key, value in font_config.items()}
        with open(ini_file_path, 'w') as configfile:
            config.write(configfile)
            print(f"Metadata saved successfully to {ini_file_path}")

    def validate_font_config(self, image, font_config):
        """Validate and adjust font config based on image dimensions."""
        expected_width = font_config['font_width'] * 16
        ascii_range_count = font_config['ascii_range_end'] - font_config['ascii_range_start'] + 1
        expected_height = font_config['font_height'] * ((ascii_range_count + 15) // 16)

        if image.size == (expected_width, expected_height):
            return False, font_config

        default_ascii_range = self.app_reference.config_manager.get_default_ascii_range()
        for start, end in [default_ascii_range, (32, 127), (0, 127), (0, 255)]:
            range_count = end - start + 1
            adjusted_height = font_config['font_height'] * ((range_count + 15) // 16)
            if image.size == (expected_width, adjusted_height):
                modified_config = font_config.copy()
                modified_config.update({'ascii_range_start': start, 'ascii_range_end': end})
                return True, modified_config

        return True, {}

    # =========================================================================
    # File Loading and Opening Operations
    # =========================================================================

    def get_open_filename(self):
        """Handle the Open action."""
        file_path = filedialog.askopenfilename(
            title="Open File",
            filetypes=(
                ("All Files", "*.*"),
                ("TrueType Font Files", "*.ttf"),
                ("OpenType Font Files", "*.otf"),
                ("PSF Font Files", "*.psf"),
                ("Agon Font Files", "*.font"),
                ("PNG Images", "*.png")
            ),
            initialdir=self.app_reference.config_manager.get_most_recent_open_directory()
        )
        self.open_file(file_path)

    def open_file(self, file_path):
        if file_path:
            ini_filepath = file_path + '.ini'
            font_config = self.load_font_metadata_from_ini(ini_filepath) if os.path.exists(ini_filepath) else self.parse_font_filename(file_path)
            font_config, font_image = read_font(file_path, font_config)

            self.app_reference.font_config_editor.setup_ui_from_config(font_config)
            self.app_reference.image_display.load_image(font_image)
            self.app_reference.editor_widget.initialize_grid()
            # self.app_reference.image_display.trigger_click_on_ascii_code(ord('A'))

            self.app_reference.config_manager.set_most_recent_open_directory(os.path.dirname(file_path))
            self.app_reference.config_manager.set_most_recent_file(file_path)
            filename = os.path.basename(file_path)
            self.app_reference.master.title(f"Agon Font Editor - {filename}")

    # =========================================================================
    # File Saving Operations
    # =========================================================================

    def save_file(self):
        font_config = self.app_reference.font_config_editor.get_config()
        default_name = f"{font_config['font_name']}_{font_config['font_variant']}_{font_config['font_width']}x{font_config['font_height']}"
        
        file_path = filedialog.asksaveasfilename(
            title="Save As",
            defaultextension=".font",
            filetypes=(("Font Files", "*.font"), ("PNG Images", "*.png"), ("All Files", "*.*")),
            initialdir=self.app_reference.config_manager.get_most_recent_save_directory(),
            initialfile=default_name
        )

        if not file_path:
            return

        _, ext = os.path.splitext(file_path)
        if not ext:
            ext = '.font'
            file_path += ext

        if ext == '.png':
            result = self.save_as_png(file_path, font_config)
        elif ext == '.font':
            result = self.save_as_font(file_path, font_config)
        else:
            messagebox.showerror("Unsupported File Type", f"Unsupported file extension: {ext}")
            return

        if result is True:
            self.app_reference.config_manager.set_most_recent_save_directory(os.path.dirname(file_path))
            filename = os.path.basename(file_path)
            self.app_reference.master.title(f"Agon Font Editor - {filename}")
        else:
            messagebox.showerror("Save Failed", result)

    def save_as_png(self, file_path, font_config):
        try:
            ini_file_path = f"{file_path}.ini"
            self.app_reference.image_display.working_image.save(file_path)
            self.save_font_metadata(font_config, ini_file_path)
            return True
        except Exception as e:
            return f"Failed to save PNG: {e}"

    def save_as_font(self, file_path, font_config):
        try:
            ini_file_path = f"{file_path}.ini"
            make_font(font_config, self.app_reference.image_display.working_image, file_path)
            self.save_font_metadata(font_config, ini_file_path)
            return True
        except Exception as e:
            return f"Failed to save font file: {e}"
