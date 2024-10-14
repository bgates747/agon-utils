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

        # Initialize layout without scrolling
        self.create_widgets()

    def create_widgets(self):
        """
        Create DeltaControls for numeric settings and Entry widgets for string settings.
        """
        row = 0
        for key, value in self.font_config.items():
            # Create a label for each setting
            label = ttk.Label(self, text=key.replace('_', ' ').capitalize())
            label.grid(row=row, column=0, pady=0, padx=(10, 5), sticky="w")

            if isinstance(value, (int, float)):
                # Configure the DeltaControl for numeric settings
                control_config = self.delta_control_config.copy()
                control_config['value']['initial'] = value
                control_config['value']['data_type'] = "int" if isinstance(value, int) else "float"

                # Create DeltaControl with the updated config
                control = DeltaControl(
                    self,
                    config=control_config,
                    callback=lambda v, k=key: self.update_config(k, v)
                )
                control.grid(row=row, column=1, pady=0, padx=(5, 10), sticky="w")

            elif isinstance(value, str):
                # Configure an entry for string settings
                entry_var = tk.StringVar(value=value)
                entry = ttk.Entry(self, textvariable=entry_var, width=25)
                entry.grid(row=row, column=1, pady=0, padx=(5, 10), sticky="w")
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
        self.font_config[key] = value
        print(f"Updated {key} to {value}")