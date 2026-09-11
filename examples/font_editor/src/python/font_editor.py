import os
import tkinter as tk
from tkinter import ttk
from config_manager import get_app_config_value, xml_values_to_dict
from file_manager import open_file
from config_editor import ConfigEditor
from menu_bar import MenuBar
from image_display import ImageDisplay
from custom_widgets import ConsoleDisplay, ScrollableFrame
from ui_scaling import initialize_ui_scaling, ui_px
from editor_widget import EditorWidget
from asm_config_editor import DoAssemblyDialog
from batch_convert_dialog import BatchConvertDialog

class FontEditor(ttk.Frame):
    """
    Main application class for FontEditor. Manages and organizes the main widgets.
    """
    def __init__(self, master):
        initialize_ui_scaling(master)
        super().__init__(master)

        master.title("Agon Font Editor")  
        self.pack(fill=tk.BOTH, expand=True)

        # Initialize application state variables for the currently loaded font files
        self.current_font_file = None  # Path to the currently open font file
        self.current_font_xml_file = None    # Path to the currently open .ini file
        self.editor_window = None
        self.editor_widget = None
        self.optimization_window = None

        # Create and add the menu bar
        self.menubar = MenuBar(master, self)

        # Main content area divided into left (config) and right (image display and editor) sections
        main_content_frame = tk.Frame(self)
        main_content_frame.pack(fill=tk.BOTH, expand=True)

        # Left Frame for ConfigEditor
        config_frame = tk.Frame(main_content_frame)
        config_frame.pack(side=tk.LEFT, fill=tk.Y, padx=ui_px(self, 10), pady=ui_px(self, 10), anchor="n")

        # Create an instance of ConfigEditor with XML data properties and an app reference
        config_editor_file = os.path.join(os.path.dirname(__file__), "font_config_editor.xml")
        self.config_scroll = ScrollableFrame(config_frame)
        self.font_config_editor = ConfigEditor(
            self.config_scroll.content, config_editor_file, app_reference=self,
            on_redraw=lambda: self.image_display.render_font(),
        )
        self.font_config_editor.pack(fill="both", expand=True)

        # Add the "Do Assembly" button at the bottom of the config frame
        do_assembly_button = tk.Button(
            config_frame,
            text="Do Assembly",
            command=self.open_assembly_dialog
        )
        do_assembly_button.pack(side=tk.BOTTOM, pady=ui_px(self, 10))

        # Add the "Batch Convert" button at the bottom of the config frame
        batch_convert_button = tk.Button(
            config_frame,
            text="Batch Convert",
            command=self.open_batch_convert_dialog
        )
        batch_convert_button.pack(side=tk.BOTTOM, pady=ui_px(self, 10))
        self.config_scroll.pack(fill="both", expand=True)

        # Right Frame for ImageDisplay and EditorWidget
        image_frame = tk.Frame(main_content_frame)
        image_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=ui_px(self, 10), pady=ui_px(self, 10))

        # Create an instance of ImageDisplay with an app reference
        if True:
            self.image_display = ImageDisplay(image_frame, app_reference=self)
            self.image_display.pack(fill="both", expand=True)  # Fully expand to fill right frame
        else:
            self.image_display = None

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

    def optimize_all_characters(self):
        from atlas_resampling import AtlasResampling
        if self.optimization_window is not None and self.optimization_window.winfo_exists():
            self.optimization_window.lift()
            return
        self.optimization_window = AtlasResampling(self)

    def open_character_editor(self):
        """Reuse one non-modal editor while allowing further atlas selections."""
        if self.editor_window is None or not self.editor_window.winfo_exists():
            self.editor_window = tk.Toplevel(self.master)
            self.editor_window.transient(self.master)
            self.editor_window.protocol("WM_DELETE_WINDOW", self.close_character_editor)
            self.editor_window.bind("<Escape>", lambda event: self.close_character_editor())
            self.editor_widget = EditorWidget(self.editor_window, app_reference=self)
            self.editor_widget.pack(fill="both", expand=True, padx=ui_px(self, 8), pady=ui_px(self, 8))
        self.refresh_character_editor()
        self.editor_window.deiconify()
        self.editor_window.lift()
        self.editor_widget.canvas.focus_set()

    def refresh_character_editor(self):
        if self.editor_widget is None:
            return
        ascii_code = self.image_display.current_ascii_code
        if ascii_code is None:
            self.close_character_editor()
            return
        label = f" — {chr(ascii_code)}" if 32 <= ascii_code < 127 else ""
        self.editor_window.title(f"Character {ascii_code} (0x{ascii_code:02X}){label}")
        self.editor_widget.populate_from_image(self.image_display.get_char_img_ascii(ascii_code))

    def close_character_editor(self):
        window = self.editor_window
        self.editor_window = None
        self.editor_widget = None
        if window is not None and window.winfo_exists():
            window.destroy()

    def open_assembly_dialog(self):
        """Open the assembly configuration dialog with the current font configuration."""
        font_config = self.font_config_editor.get_config()  # Get the current font config
        config_editor_file = "src/python/asm_config_editor.xml"
        app_reference = self

        dialog = DoAssemblyDialog(self, config_editor_file, app_reference, font_config)

    def open_batch_convert_dialog(self):
        """Open the batch conversion dialog with the current font configuration."""
        app_reference = self
        xml_values_filepath = 'src/python/batch_convert_values.xml'
        xml_defaults_filepath = 'src/python/batch_convert_dialog.xml'
        values_dict = xml_values_to_dict(xml_defaults_filepath, xml_values_filepath)
        dialog = BatchConvertDialog(self, xml_defaults_filepath, app_reference, values_dict, xml_values_filepath)

if __name__ == "__main__":
    root = tk.Tk()

    # Launch the Font Editor Application
    app = FontEditor(root)
    
    # Start the Tkinter event loop
    root.mainloop()
