
import tkinter as tk
from tkinter import Toplevel
from config_editor import ConfigEditor
class ConfigEditorDialog(Toplevel):
    """
    A modal dialog that displays the ConfigEditor with Set and Cancel buttons.
    """
    def __init__(self, parent, config_editor_file, app_reference, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.title("Configuration Editor")
        self.geometry("400x600")  # Adjust the size as needed

        # Make the dialog modal
        self.transient(parent)
        self.grab_set()

        # Create the ConfigEditor widget
        self.editor = ConfigEditor(self, config_editor_file, app_reference)
        self.editor.pack(fill="both", expand=True, padx=10, pady=10)

        # Create the buttons frame
        self.create_buttons()

        # Initialize the values in the ConfigEditor
        self.init_values()

    def init_values(self):
        """Initialize the values in the ConfigEditor.
        This method should be overridden in subclasses to set the initial values."""
        pass

    def create_buttons(self):
        """Creates the Set, Cancel, and GO buttons at the bottom of the dialog."""
        button_frame = tk.Frame(self)
        button_frame.pack(side="bottom", fill="x", padx=10, pady=10)

        go_button = tk.Button(button_frame, text="GO", command=self.on_go)
        go_button.pack(side="right", padx=5)

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

    def on_go(self):
        """Handle the GO button click."""
        print("GO button pressed")
        self.destroy()
