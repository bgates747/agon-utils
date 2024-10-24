import tkinter as tk
from tkinter import Toplevel
from font_config_editor import FontConfigEditor

class FontConfigEditorDialog(Toplevel):
    """
    A modal dialog that displays the FontConfigEditor with Set and Cancel buttons.
    """
    def __init__(self, parent, config_editor_file, app_reference, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.title("Font Configuration Editor")
        self.geometry("400x600")  # Adjust the size as needed

        # Make the dialog modal
        self.transient(parent)
        self.grab_set()

        # Create the FontConfigEditor widget
        self.editor = FontConfigEditor(self, config_editor_file, app_reference)
        self.editor.pack(fill="both", expand=True, padx=10, pady=10)

        # Create the buttons frame
        self.create_buttons()

    def create_buttons(self):
        """Creates the Set and Cancel buttons at the bottom of the dialog."""
        button_frame = tk.Frame(self)
        button_frame.pack(side="bottom", fill="x", padx=10, pady=10)

        set_button = tk.Button(button_frame, text="Set", command=self.on_set)
        set_button.pack(side="right", padx=5)

        cancel_button = tk.Button(button_frame, text="Cancel", command=self.on_cancel)
        cancel_button.pack(side="right")

    def on_set(self):
        """Handle the Set button click."""
        print("Set button pressed")
        self.destroy()

    def on_cancel(self):
        """Handle the Cancel button click."""
        print("Cancel button pressed")
        self.destroy()

class MainApp(tk.Tk):
    """
    Main application with a button to spawn the FontConfigEditorDialog.
    """
    def __init__(self):
        super().__init__()
        self.title("Main Application")
        self.geometry("300x100")  # Adjust the size as needed

        # Create a button to open the FontConfigEditorDialog
        open_button = tk.Button(self, text="Open Font Config Editor", command=self.open_editor_dialog)
        open_button.pack(pady=20)

    def open_editor_dialog(self):
        """Open the FontConfigEditorDialog when the button is pressed."""
        config_editor_file = "examples/font_editor/src/python/asm_config_editor.xml"
        app_reference = None  # Replace with the actual app reference if needed

        dialog = FontConfigEditorDialog(self, config_editor_file, app_reference)

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
