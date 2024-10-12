import tkinter as tk
from ImageDisplayWidget import ImageDisplayWidget
from EditorWidget import EditorWidget
from MenuBar import MenuBar
from ConfigManager import ConfigManager
from FileManager import FileManager
from FontConfigEditor import FontConfigEditor
from AgonFont import create_blank_font_image

class FontEditorApp(tk.Frame):
    """ The main application for the font editor """
    def __init__(self, master, config_manager):
        super().__init__(master)

        master.title("Agon Font Editor")  
        self.pack(fill=tk.BOTH, expand=True)
        self.config_manager = config_manager
        self.default_font_config = self.config_manager.get_config_defaults('data/fontmeta.cfg')

        # Initialize application state variables for the currently loaded font files
        self.current_font_file = None  # Path to the currently open font file
        self.current_font_ini_file = None    # Path to the currently open .ini file
        self.current_ascii_code = ord('A')   # Default to ASCII code for 'A'

        # Create and add the menu bar
        self.menubar = MenuBar(master, self)

        # Create a control panel that contains widgets for font editing
        self.create_control_panel()

        # Initialize the FileManager
        self.file_manager = FileManager(self)

    def create_control_panel(self):
        """ Create a control panel to hold widgets (Image display and Editor with Config Manager) """
        control_frame = tk.Frame(self)
        control_frame.pack(fill=tk.BOTH, expand=True)

        # Create a frame for FontConfigEditor on the left
        config_frame = tk.Frame(control_frame)
        config_frame.pack(side=tk.LEFT, padx=10, pady=10, anchor="n", fill=tk.Y) 

        # FontConfigEditor for managing font metadata, placed on the left side
        self.font_config_editor = FontConfigEditor(config_frame, self, self.default_font_config)
        self.font_config_editor.pack(fill=tk.Y, pady=5, expand=True)

        # Create a frame for ImageDisplayWidget and EditorWidget stacked vertically on the right
        display_editor_frame = tk.Frame(control_frame)
        display_editor_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Image Display Widget for character selection (placed on top)
        blank_font_img = create_blank_font_image(self.default_font_config)
        self.image_display = ImageDisplayWidget(display_editor_frame, self, blank_font_img)
        self.image_display.pack(fill=tk.BOTH, expand=True, pady=(0, 5))

        # Editor Widget for character editing (placed below the ImageDisplayWidget)
        self.editor_widget = EditorWidget(display_editor_frame, self)
        self.editor_widget.pack(fill=tk.X, pady=(5, 0))

        # Initialize EditorWidget with default metadata
        self.editor_widget.initialize_grid()

        # Trigger ImageDisplayWidget redraw with the blank font image
        self.image_display.trigger_click_on_ascii_code(self.current_ascii_code)

# Example Usage
if __name__ == "__main__":
    root = tk.Tk()

    # Initialize the ConfigManager to load configuration
    config_manager = ConfigManager()

    # Launch the Font Editor Application
    app = FontEditorApp(root, config_manager)
    
    # Start the Tkinter event loop
    root.mainloop()
