import tkinter as tk
from ImageDisplayWidget import ImageDisplayWidget
from EditorWidget import EditorWidget
from MenuBar import MenuBar
from ConfigManager import ConfigManager
from FileManager import FileManager

class FontEditorApp(tk.Frame):
    """ The main application for the font editor """
    def __init__(self, master, config_manager):
        super().__init__(master)
        
        # Set the title of the main window
        self.pack(fill=tk.BOTH, expand=True)
        self.config_manager = config_manager  # Pass config manager

        # Initialize application state variables from config defaults
        self.current_font_image_file = None  # Path to the currently open font image
        self.current_font_ini_file = None    # Path to the currently open .ini file
        self.current_ascii_code = ord('A')   # Default to ASCII code for 'A'

        # Initialize font metadata to None
        self.font_name = 'no_font_loaded'
        self.font_variant = 'Regular'
        self.font_width = int(self.config_manager.get_setting('default_font_width', 9))
        self.font_height = int(self.config_manager.get_setting('default_font_height', 15))
        self.offset_left = int(self.config_manager.get_setting('default_offset_left', 0))
        self.offset_top = int(self.config_manager.get_setting('default_offset_top', 0))
        self.offset_width = int(self.config_manager.get_setting('default_offset_width', 0))
        self.offset_height = int(self.config_manager.get_setting('default_offset_height', 0))
        self.ascii_range_start = int(self.config_manager.get_setting('default_ascii_range_start', 32))
        self.ascii_range_end = int(self.config_manager.get_setting('default_ascii_range_end', 127))

        # Create and add the menu bar
        self.menubar = MenuBar(master, self)

        # Initialize the FileManager
        self.file_manager = FileManager(self)

        # Create a blank control panel without loading any image initially
        self.create_control_panel()

        # # Open the most recently opened file or load default if it doesn't exist
        # most_recent_file = self.config_manager.get_most_recent_file()
        # self.file_manager.open_file(most_recent_file)


    def create_control_panel(self):
        """ Create a control panel to hold widgets (Image display and Editor) """
        control_frame = tk.Frame(self)
        control_frame.pack(fill=tk.BOTH, expand=True)  # This frame now expands to hold both widgets horizontally

        # Editor Widget for character editing (placed on the left)
        self.editor_widget = EditorWidget(control_frame, self)
        self.editor_widget.pack(side=tk.LEFT, padx=10, pady=10)

        # Image Display Widget for character selection (placed on the right)
        self.image_display = ImageDisplayWidget(control_frame, self)
        self.image_display.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Load default metadata from the config manager
        default_font_width = int(self.config_manager.get_setting('default_font_width', 9))
        default_font_height = int(self.config_manager.get_setting('default_font_height', 15))
        default_ascii_range_start = int(self.config_manager.get_setting('default_ascii_range_start', 32))
        default_ascii_range_end = int(self.config_manager.get_setting('default_ascii_range_end', 127))
        default_ascii_range = (default_ascii_range_start, default_ascii_range_end)

        # Initialize EditorWidget with default metadata
        self.editor_widget.initialize_grid(default_font_width, default_font_height)

        # Set metadata for ImageDisplayWidget after initialization
        self.image_display.set_font_metadata(default_font_width, default_font_height, default_ascii_range)

# ==============================================================================
# Font configuration methods
# ==============================================================================
    def get_font_metadata(self):
        """Retrieve font metadata from the application state."""
        return {
            'font_name': self.font_name,
            'font_variant': self.font_variant,
            'font_width': self.font_width,
            'font_height': self.font_height,
            'offset_left': self.offset_left,
            'offset_top': self.offset_top,
            'offset_width': self.offset_width,
            'offset_height': self.offset_height,
            'ascii_range_start': self.ascii_range_start,
            'ascii_range_end': self.ascii_range_end
        }
    
    def set_font_metadata(self, font_config):
        """Set font font configuration in the application state."""
        self.font_name = font_config['font_name']
        self.font_variant = font_config['font_variant']
        self.font_width = font_config['font_width']
        self.font_height = font_config['font_height']
        self.offset_left = font_config['offset_left']
        self.offset_top = font_config['offset_top']
        self.offset_width = font_config['offset_width']
        self.offset_height = font_config['offset_height']
        self.ascii_range_start = font_config['ascii_range_start']
        self.ascii_range_end = font_config['ascii_range_end']

# Example Usage
if __name__ == "__main__":
    root = tk.Tk()

    # Initialize the ConfigManager to load configuration
    config_manager = ConfigManager()

    # Launch the Font Editor Application
    app = FontEditorApp(root, config_manager)
    
    # Start the Tkinter event loop
    root.mainloop()
# test change