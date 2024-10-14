import os
import tkinter as tk
from tkinter import ttk
from config_manager import (
    read_xml_file,
    xml_element_to_dict,
    gather_includes,
    combine_xml_files,
    flatten_config,
    dict_to_text
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

        # Store DeltaControls and text entries
        self.delta_controls = {}
        self.text_entries = {}

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

                # Create DeltaControl without callback for deferred updates
                control = DeltaControl(self, config=control_config)
                control.grid(row=row, column=1, pady=0, padx=(5, 10), sticky="w")
                self.delta_controls[key] = control

            elif isinstance(value, str):
                # Configure an entry for string settings
                entry_var = tk.StringVar(value=value)
                entry = ttk.Entry(self, textvariable=entry_var, width=25)
                entry.grid(row=row, column=1, pady=0, padx=(5, 10), sticky="w")
                self.text_entries[key] = entry_var

            row += 1

        # Add the "Apply Changes" button at the end
        apply_button = ttk.Button(self, text="Apply Changes", command=self.apply_changes)
        apply_button.grid(row=row, column=0, columnspan=2, pady=(10, 0))

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

    def get_current_config(self):
        """
        Retrieve the original (default) configuration values from both text entry and DeltaControl widgets.
        Returns:
            dict: A dictionary containing the original configuration values.
        """
        return self.font_config

    def get_modified_config(self):
        """
        Retrieve the modified (computed) configuration values from both text entry and DeltaControl widgets.
        Returns:
            dict: A dictionary containing the modified configuration values.
        """
        modified_config = {}

        # Get computed values from DeltaControls
        for key, control in self.delta_controls.items():
            modified_config[key] = control.get_computed_value()  # Use the computed (modified) value

        # Get current values from text entry fields
        for key, entry_var in self.text_entries.items():
            modified_config[key] = entry_var.get()  # Current value in the entry

        return modified_config
    
    def apply_changes(self):
        """
        Apply modified values to font_config, set these values as the new original values in DeltaControls,
        reset deltas, and refresh the original value display.
        """
        # Retrieve modified configuration and apply to font_config
        self.font_config = self.get_modified_config().copy()

        # Update DeltaControls to make the new values the original values and reset deltas
        for key, control in self.delta_controls.items():
            new_value = self.font_config[key]  # Get the updated value from font_config
            control.set_initial_value(new_value)  # Set this as the new original value
            control.reset_delta()  # Reset delta to 0

        # Refresh text entry fields with updated font_config values
        for key, entry_var in self.text_entries.items():
            entry_var.set(self.font_config[key])  # Update entry field to show the updated value

        # Print updated font_config for confirmation
        font_config_text = dict_to_text(self.font_config)
        print(font_config_text)
