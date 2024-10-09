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
        master.title("Agon Font Editor")  # Set the window title here
        self.pack(fill=tk.BOTH, expand=True)
        self.config_manager = config_manager  # Pass config manager

        # Initialize application state variables for the currently loaded font files
        self.current_font_image_file = None  # Path to the currently open font image
        self.current_font_ini_file = None    # Path to the currently open .ini file
        self.current_ascii_code = ord('A')   # Default to ASCII code for 'A'

        # Create and add the menu bar
        self.menubar = MenuBar(master, self)

        # Initialize the FileManager
        self.file_manager = FileManager(self)

        # Create a control panel that contains widgets for font editing
        self.create_control_panel()

    def create_control_panel(self):
        """ Create a control panel to hold widgets (Image display and Editor with Config Manager) """
        control_frame = tk.Frame(self)
        control_frame.pack(fill=tk.BOTH, expand=True)

        # Create a sub-frame for the EditorWidget and FontConfigEditor
        editor_frame = tk.Frame(control_frame)
        editor_frame.pack(side=tk.LEFT, padx=10, pady=10, anchor="n")  # Keep aligned at top

        # Initialize default metadata from the config manager to pass to FontConfigEditor
        default_metadata = {
            'font_name': self.config_manager.get_setting('default_font_name', 'no_font_loaded'),
            'font_variant': self.config_manager.get_setting('default_font_variant', 'Regular'),
            'font_width': int(self.config_manager.get_setting('default_font_width', 9)),
            'font_height': int(self.config_manager.get_setting('default_font_height', 15)),
            'offset_left': int(self.config_manager.get_setting('default_offset_left', 0)),
            'offset_top': int(self.config_manager.get_setting('default_offset_top', 0)),
            'offset_width': int(self.config_manager.get_setting('default_offset_width', 0)),
            'offset_height': int(self.config_manager.get_setting('default_offset_height', 0)),
            'ascii_range_start': int(self.config_manager.get_setting('default_ascii_range_start', 32)),
            'ascii_range_end': int(self.config_manager.get_setting('default_ascii_range_end', 127))
        }

        # Editor Widget for character editing (placed above the FontConfigEditor)
        self.editor_widget = EditorWidget(editor_frame, self)
        self.editor_widget.pack(pady=(0, 5))  # Add padding between widgets

        # FontConfigEditor for managing font metadata below the editor widget
        self.font_config_manager = FontConfigEditor(editor_frame, config_dict=default_metadata)
        self.font_config_manager.pack(fill=tk.X, pady=5)

        # Image Display Widget for character selection (placed on the right)
        self.image_display = ImageDisplayWidget(control_frame, self)
        self.image_display.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Initialize EditorWidget with default metadata
        self.editor_widget.initialize_grid()

# Example Usage
if __name__ == "__main__":
    root = tk.Tk()

    # Initialize the ConfigManager to load configuration
    config_manager = ConfigManager()

    # Launch the Font Editor Application
    app = FontEditorApp(root, config_manager)
    
    # Start the Tkinter event loop
    root.mainloop()
