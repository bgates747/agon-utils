import os
import tkinter as tk
from tkinter import ttk
from config_manager import get_app_config_value, xml_values_to_dict
from file_manager import open_file
from config_editor import ConfigEditor
from menu_bar import MenuBar
from image_display import ImageDisplay
from custom_widgets import ConsoleDisplay
from editor_widget import EditorWidget
from config_editor_dialog import DoAssemblyDialog
from batch_convert_dialog import BatchConvertDialog

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

        # Create and add the menu bar
        self.menubar = MenuBar(master, self)

        # Main content area divided into left (config) and right (image display and editor) sections
        main_content_frame = tk.Frame(self)
        main_content_frame.pack(fill=tk.BOTH, expand=True)

        # Left Frame for ConfigEditor
        config_frame = tk.Frame(main_content_frame)
        config_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10, anchor="n")  # Only expand vertically

        # Create an instance of ConfigEditor with XML data properties and an app reference
        config_editor_file = os.path.join(os.path.dirname(__file__), "font_config_editor.xml")
        self.font_config_editor = ConfigEditor(config_frame, config_editor_file, app_reference=self)
        self.font_config_editor.pack(fill="y", expand=True)  # Fills available vertical space only

        # Add the "Do Assembly" button at the bottom of the config frame
        do_assembly_button = tk.Button(
            config_frame,
            text="Do Assembly",
            command=self.open_assembly_dialog
        )
        do_assembly_button.pack(side=tk.BOTTOM, pady=10)

        # Add the "Batch Convert" button at the bottom of the config frame
        batch_convert_button = tk.Button(
            config_frame,
            text="Batch Convert",
            command=self.open_batch_convert_dialog
        )
        batch_convert_button.pack(side=tk.BOTTOM, pady=10)

        # Right Frame for ImageDisplay and EditorWidget
        image_frame = tk.Frame(main_content_frame)
        image_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)  # Expands fully

        # Create an instance of ImageDisplay with an app reference
        if True:
            self.image_display = ImageDisplay(image_frame, app_reference=self)
            self.image_display.pack(fill="both", expand=True)  # Fully expand to fill right frame
        else:
            self.image_display = None

        # Create an instance of EditorWidget below ImageDisplay
        if False:
            self.editor_widget = EditorWidget(image_frame, app_reference=self)
            self.editor_widget.pack(fill="x", expand=True, pady=(5, 0))  # Horizontal fill, aligns below ImageDisplay
        else:
            self.editor_widget = None

        # Bottom ConsoleDisplay
        if False:
            self.console_display = ConsoleDisplay(self)
            self.console_display.pack(fill="x", padx=10, pady=5, anchor="s")  # Fills available horizontal space
        else:
            self.console_display = None

        # Load the last opened font file
        file_path = get_app_config_value("most_recent_file")
        if file_path:
            open_file(self, file_path)

    def open_assembly_dialog(self):
        """Open the assembly configuration dialog with the current font configuration."""
        font_config = self.font_config_editor.get_config()  # Get the current font config
        config_editor_file = "examples/font_editor/src/python/asm_config_editor.xml"
        app_reference = self

        dialog = DoAssemblyDialog(self, config_editor_file, app_reference, font_config)

    def open_batch_convert_dialog(self):
        """Open the batch conversion dialog with the current font configuration."""
        app_reference = self
        xml_values_filepath = 'examples/font_editor/src/python/batch_convert_values.xml'
        xml_defaults_filepath = 'examples/font_editor/src/python/batch_convert_dialog.xml'
        values_dict = xml_values_to_dict(xml_defaults_filepath, xml_values_filepath)
        dialog = BatchConvertDialog(self, xml_defaults_filepath, app_reference, values_dict, xml_values_filepath)

if __name__ == "__main__":
    root = tk.Tk()

    # Launch the Font Editor Application
    app = FontEditor(root)
    
    # Start the Tkinter event loop
    root.mainloop()
