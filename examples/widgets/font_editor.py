
import os
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

        # Create an instance of FontConfigEditor with XML data properties and an app reference
        font_config_file = os.path.join(os.path.dirname(__file__), "font_config_editor.xml")
        self.font_config_editor = FontConfigEditor(self, font_config_file, app_reference=self)
        self.font_config_editor.pack(fill="both", expand=True)

if __name__ == "__main__":
    root = tk.Tk()

    # Launch the Font Editor Application
    app = FontEditor(root)
    
    # Start the Tkinter event loop
    root.mainloop()
