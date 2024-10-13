import os
import tkinter as tk
from tkinter import ttk
from config_manager import (
    read_xml_file,
    xml_element_to_dict,
    gather_includes,
    combine_xml_files,
    flatten_config
)
from custom_widgets import DeltaControl

class FontConfigEditor(ttk.Frame):
    """
    A dynamic editor for font configurations, creating controls based on configuration types.
    """
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # Set config directories and file paths
        self.config_directory = 'examples/fonts/editor2/data'
        self.font_config_filename = 'cfg.font.type.all.xml'
        self.font_config_filepath = os.path.join(self.config_directory, self.font_config_filename)

        # Load configuration settings and prepare the editor
        self.font_config = self.load_configurations(self.font_config_filepath)
        self.delta_control_config = self.load_delta_control_config()

        # Set up scrolling canvas and container for dynamic widgets
        self.canvas = tk.Canvas(self, borderwidth=0, background="#ffffff")
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Initialize layout
        self.create_widgets()

        # Pack the canvas and scrollbar
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def create_widgets(self):
        """
        Create DeltaControls for numeric settings and Entry widgets for string settings.
        """
        row = 0
        for key, value in self.font_config.items():
            if isinstance(value, (int, float)):
                # Make a copy of delta_control_config for the current control
                control_config = self.delta_control_config.copy()
                
                # Update control_config with specific values for the current DeltaControl
                control_config['label']['text'] = key.replace('_', ' ').capitalize()
                control_config['value']['initial'] = value
                control_config['value']['data_type'] = "int" if isinstance(value, int) else "float"

                # Create DeltaControl with the updated config
                control = DeltaControl(
                    self.scrollable_frame,
                    config=control_config,
                    callback=lambda v, k=key: self.update_config(k, v)
                )
                control.grid(row=row, column=0, pady=0, padx=10, sticky="w")

            elif isinstance(value, str):
                label = ttk.Label(self.scrollable_frame, text=key.replace('_', ' ').capitalize())
                label.grid(row=row, column=0, pady=0, padx=10, sticky="w")

                entry_var = tk.StringVar(value=value)
                entry = ttk.Entry(self.scrollable_frame, textvariable=entry_var, width=25)
                entry.grid(row=row, column=1, pady=0, padx=10, sticky="w")
                entry.bind("<FocusOut>", lambda e, k=key, var=entry_var: self.update_config(k, var.get()))

            row += 1

    def load_configurations(self, font_config_filepath):
        """
        Load, combine, and flatten XML configuration for font settings.
        """

        # Gather includes and combine XML files, specifying the root tag
        include_files = gather_includes(font_config_filepath)
        font_config_xml = combine_xml_files(include_files, root_tag="FontConfig")

        # Convert the combined XML element directly to a dictionary and flatten it
        font_config = xml_element_to_dict(font_config_xml)
        return flatten_config(font_config, target_key="Setting", key_attr="name", value_attr="default", type_attr="type")

    def load_delta_control_config(self):
        """
        Load configuration from XML for DeltaControl widget settings.
        """
        delta_control_config_path = os.path.join(self.config_directory, 'cfg.ui.delta_control.xml')

        # Read and parse the DeltaControl configuration
        delta_control_config_xml = read_xml_file(delta_control_config_path)
        return xml_element_to_dict(delta_control_config_xml)

    def update_config(self, key, value):
        """
        Update the configuration dictionary with the new value from the controls.
        """
        self.config[key] = value
        print(f"Updated {key} to {value}")

# Main testing block
if __name__ == "__main__":
    # Main application setup
    root = tk.Tk()
    root.title("Font Configuration Editor")

    # Initialize the FontConfigEditor widget
    editor = FontConfigEditor(root)
    editor.pack(fill="both", expand=True)

    # Run the main application loop
    root.mainloop()
