import tkinter as tk
from tkinter import ttk
from font_config_editor import FontConfigEditor
from menu_bar import MenuBar

class FontEditor(ttk.Frame):
    """
    Main application class for FontEditor. Manages and organizes the main widgets.
    """
    def __init__(self, master):
        super().__init__(master)

        master.title("Agon Font Editor")  
        self.pack(fill=tk.BOTH, expand=True)

        # Initialize application state variables for the currently loaded font files
        self.current_font_file = None  # Path to the currently open font file
        self.current_font_ini_file = None    # Path to the currently open .ini file
        self.current_ascii_code = ord('A')   # Default to ASCII code for 'A'

        # Create and add the menu bar
        self.menubar = MenuBar(master, self)

        # Create a control panel that contains widgets for font editing
        control_frame = tk.Frame(self)
        control_frame.pack(fill=tk.BOTH, expand=True)

        # Create a frame for FontConfigEditor on the left
        config_frame = tk.Frame(control_frame)
        config_frame.pack(side=tk.LEFT, padx=10, pady=10, anchor="n", fill=tk.Y) 

        # FontConfigEditor for managing font metadata, placed on the left side
        self.font_config_editor = FontConfigEditor(config_frame, )
        self.font_config_editor.pack(fill=tk.Y, pady=5, expand=True)

        # # Create a frame for ImageDisplayWidget and EditorWidget in a shared space on the right
        # display_editor_frame = tk.Frame(control_frame)
        # display_editor_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # # Create a container frame to hold EditorWidget and ImageDisplayWidget together
        # editor_display_container = tk.Frame(display_editor_frame)
        # editor_display_container.pack(fill=tk.BOTH, expand=True)

        # # Editor Widget in the top-left corner of the container
        # self.editor_widget = EditorWidget(editor_display_container, self)
        # self.editor_widget.pack(side=tk.LEFT, anchor="n", padx=5, pady=5)

        # # Image Display Widget, placed to the right of the EditorWidget
        # blank_font_img = create_blank_font_image(self.config_manager.get_config_defaults('data/font.cfg'))
        # self.image_display = ImageDisplayWidget(editor_display_container, self, blank_font_img)
        # self.image_display.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # # Initialize EditorWidget with default metadata
        # self.editor_widget.initialize_grid()

        # # Trigger ImageDisplayWidget redraw with the blank font image
        # self.image_display.trigger_click_on_ascii_code(self.current_ascii_code)

        # # ConsoleDisplay for output messages, placed across the bottom of control_frame
        # self.console_display = ConsoleDisplay(self)
        # self.console_display.pack(fill=tk.X, padx=10, pady=(10, 0), side=tk.BOTTOM)
        # self.console_display.append_message("Console initialized. Ready for output.")

        # Initialize widget elements
        self.create_components()

        # Layout components
        self.layout_components()

    def create_components(self):
        """
        Instantiate and configure widget elements.
        """
        pass

    def layout_components(self):
        """
        Place widget elements in the layout.
        """
        pass

# To run this class in a standalone window:
if __name__ == "__main__":
    root = tk.Tk()

    # Launch the Font Editor Application
    app = FontEditor(root)
    
    # Start the Tkinter event loop
    root.mainloop()