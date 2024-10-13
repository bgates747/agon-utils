import tkinter as tk
from tkinter import ttk
from font_config_editor import FontConfigEditor
from menu_bar import MenuBar

class FontEditor(ttk.Frame):
    """
    Main application class for FontEditor. Manages and organizes the main widgets.
    """
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.configure(borderwidth=1, relief="solid")

        # Initialize widget elements
        self.create_components()

        # Layout components
        self.layout_components()

    def create_components(self):
        """
        Instantiate and configure widget elements.
        """
        # Initialize the MenuBar and FontConfigEditor
        self.menu_bar = MenuBar(self.master)  # Create and attach MenuBar
        self.master.config(menu=self.menu_bar)  # Attach menu to the root window

        self.font_config_editor = FontConfigEditor(self)  # Create FontConfigEditor instance

    def layout_components(self):
        """
        Place widget elements in the layout.
        """
        # Place FontConfigEditor at the top-left of the main app frame
        self.font_config_editor.pack(anchor="nw", padx=10, pady=10)  # Adjust padding as needed

# To run this class in a standalone window:
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Agon Font Editor")
    root.geometry("800x600")

    app = FontEditor(root)
    app.pack(fill="both", expand=True)

    root.mainloop()
