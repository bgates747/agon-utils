import os
import tkinter as tk
from tkinter import ttk
from font_config_editor import FontConfigEditor
from menu_bar import MenuBar
from image_display import ImageDisplay
from custom_widgets import ConsoleDisplay

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

        # Create a PanedWindow for dividing the top (main content) and bottom (console)
        main_vertical_pane = tk.PanedWindow(self, orient=tk.VERTICAL, sashrelief=tk.RAISED)
        main_vertical_pane.pack(fill=tk.BOTH, expand=True)

        # Top Pane for main application content (config editor and image display)
        main_content_frame = tk.Frame(main_vertical_pane)
        main_vertical_pane.add(main_content_frame, minsize=400)

        # Create a PanedWindow within the top pane for dividing the left and right halves
        main_pane = tk.PanedWindow(main_content_frame, orient=tk.HORIZONTAL, sashrelief=tk.RAISED)
        main_pane.pack(fill=tk.BOTH, expand=True)

        # Left frame for FontConfigEditor
        config_frame = tk.Frame(main_pane)
        main_pane.add(config_frame, minsize=200)

        # Create an instance of FontConfigEditor with XML data properties and an app reference
        font_config_file = os.path.join(os.path.dirname(__file__), "font_config_editor.xml")
        self.font_config_editor = FontConfigEditor(config_frame, font_config_file, app_reference=self)
        self.font_config_editor.pack(fill="both", expand=True)

        # Right frame for additional controls and ImageDisplay
        right_frame = tk.Frame(main_pane)
        main_pane.add(right_frame, minsize=200)

        # Frame for ImageDisplay within the right frame
        image_frame = tk.Frame(right_frame)
        image_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create an instance of ImageDisplay with an app reference
        self.image_display = ImageDisplay(image_frame, app_reference=self)
        self.image_display.pack(fill="both", expand=True)

        # Add main_pane to main_content_frame
        main_content_frame.pack(fill=tk.BOTH, expand=True)

        # Bottom Pane for ConsoleDisplay
        self.console_display = ConsoleDisplay(main_vertical_pane)
        main_vertical_pane.add(self.console_display, minsize=100)
        self.console_display.pack(fill="both", expand=True)

if __name__ == "__main__":
    root = tk.Tk()

    # Launch the Font Editor Application
    app = FontEditor(root)
    
    # Start the Tkinter event loop
    root.mainloop()
