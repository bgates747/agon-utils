import os
import tkinter as tk
from tkinter import ttk
from config_manager import get_app_config_value
from file_manager import open_file
from font_config_editor_test import FontConfigEditor
from menu_bar import MenuBar
from image_display import ImageDisplay
from custom_widgets import ConsoleDisplay
from editor_widget import EditorWidget

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
        self.current_font_xml_file = None    # Path to the currently open .ini file
        self.current_ascii_code = ord('A')   # Default to ASCII code for 'A'

        # Create and add the menu bar
        self.menubar = MenuBar(master, self)

        # Main content area divided into left (config) and right (image display and editor) sections
        main_content_frame = tk.Frame(self)
        main_content_frame.pack(fill=tk.BOTH, expand=True)

        # Left Frame for FontConfigEditor
        config_frame = tk.Frame(main_content_frame)
        config_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10, anchor="n")  # Only expand vertically

        # Create an instance of FontConfigEditor with XML data properties and an app reference
        config_editor_file = os.path.join(os.path.dirname(__file__), "font_config_editor.xml")
        self.font_config_editor = FontConfigEditor(config_frame, config_editor_file, app_reference=self)
        self.font_config_editor.pack(fill="y", expand=True)  # Fills available vertical space only

        # Right Frame for ImageDisplay and EditorWidget
        image_frame = tk.Frame(main_content_frame)
        image_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)  # Expands fully

        # Create an instance of ImageDisplay with an app reference
        self.image_display = ImageDisplay(image_frame, app_reference=self)
        self.image_display.pack(fill="both", expand=True)  # Fully expand to fill right frame

        # Create an instance of EditorWidget below ImageDisplay
        self.editor_widget = EditorWidget(image_frame, app_reference=self)
        self.editor_widget.pack(fill="x", expand=True, pady=(5, 0))  # Horizontal fill, aligns below ImageDisplay

        # Bottom ConsoleDisplay
        self.console_display = ConsoleDisplay(self)
        self.console_display.pack(fill="x", padx=10, pady=5, anchor="s")  # Fills available horizontal space

        # Load the last opened font file
        file_path = get_app_config_value("most_recent_file")
        if file_path:
            open_file(self, file_path)


if __name__ == "__main__":
    root = tk.Tk()

    # Launch the Font Editor Application
    app = FontEditor(root)
    
    # Start the Tkinter event loop
    root.mainloop()
