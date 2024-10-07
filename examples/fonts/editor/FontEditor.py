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

        # Initialize default font metadata using the config manager
        self.font_name = self.config_manager.get_default('font_name', 'default_font')
        self.font_variant = self.config_manager.get_default('font_variant', 'Regular')
        self.font_width = self.config_manager.get_default_font_width()
        self.font_height = self.config_manager.get_default_font_height()
        self.offset_left = self.config_manager.get_default_offset_left()
        self.offset_top = self.config_manager.get_default_offset_top()
        self.offset_width = self.config_manager.get_default_offset_width()
        self.offset_height = self.config_manager.get_default_offset_height()
        self.ascii_range = self.config_manager.get_default_ascii_range()

        # Create and add the menu bar
        self.menubar = MenuBar(master, self)

        # Initialize the FileManager
        self.file_manager = FileManager(self)

        # Create a blank control panel without loading any image initially
        self.create_control_panel()

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
        default_font_width = self.font_width
        default_font_height = self.font_height
        default_ascii_range = self.ascii_range

        # Initialize EditorWidget with default metadata
        self.editor_widget.initialize_grid(default_font_width, default_font_height)

        # Set metadata for ImageDisplayWidget after initialization
        self.image_display.set_font_metadata(default_font_width, default_font_height, default_ascii_range)


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