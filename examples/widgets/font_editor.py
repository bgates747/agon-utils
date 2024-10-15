
import os
import tkinter as tk
import xml.etree.ElementTree as ET
from font_config import FontConfigEditor

# Main app to display the FontConfigEditor form
class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Font Config Editor")
        self.geometry("400x600")

        # Create an instance of FontConfigEditor with XML data properties
        font_config_file = os.path.join(os.path.dirname(__file__), "font_config.xml")
        editor = FontConfigEditor(self, font_config_file)
        editor.pack(fill="both", expand=True)

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
