import tkinter as tk
from ImageDisplayWidget import ImageDisplayWidget
from EditorWidget import EditorWidget
from MenuBar import MenuBar
from ConfigManager import ConfigManager
from FileManager import FileManager
from FontConfigEditor import FontConfigEditor

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

        # Initialize font metadata to defaults or None
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

    def create_control_panel(self):
        """ Create a control panel to hold widgets (Image display and Editor with Config Manager) """
        control_frame = tk.Frame(self)
        control_frame.pack(fill=tk.BOTH, expand=True)

        # Create a sub-frame for the EditorWidget and FontConfigEditor
        editor_frame = tk.Frame(control_frame)
        editor_frame.pack(side=tk.LEFT, padx=10, pady=10, anchor="n")  # Keep aligned at top

        # Editor Widget for character editing (placed on the left, in editor_frame)
        self.editor_widget = EditorWidget(editor_frame, self)
        self.editor_widget.pack(pady=(0, 5))  # Add padding between widgets

        # FontConfigEditor for managing font metadata below the editor widget
        self.font_config_manager = FontConfigEditor(editor_frame, config_dict=self.get_font_metadata())
        self.font_config_manager.pack(fill=tk.X, pady=5)

        # Image Display Widget for character selection (placed on the right)
        self.image_display = ImageDisplayWidget(control_frame, self)
        self.image_display.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Initialize EditorWidget with default metadata
        self.editor_widget.initialize_grid()

        # # Update image display to recognize editor and config manager as a single unit
        # self.image_display.set_editor_and_config_manager(self.editor_widget, self.font_config_manager)

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
        """Set font configuration in the application state."""
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

        self.font_config_manager.set_config(font_config)

# Example Usage
if __name__ == "__main__":
    root = tk.Tk()

    # Initialize the ConfigManager to load configuration
    config_manager = ConfigManager()

    # Launch the Font Editor Application
    app = FontEditorApp(root, config_manager)
    
    # Start the Tkinter event loop
    root.mainloop()
