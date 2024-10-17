import tkinter as tk
from tkinter import ttk, Button
import xml.etree.ElementTree as ET
from font_config_widget import FontConfigDeltaControl, FontConfigTextBox, FontConfigComboBox, FontConfigColorPicker
from config_manager import get_typed_data, dict_to_text

class FontConfigEditor(tk.Frame):
    """
    A dynamic editor for font configurations, creating controls based on data-driven configuration.
    """
    def __init__(self, parent, config_editor_file, app_reference, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.app_reference = app_reference
        self.config_editor_file = config_editor_file
        self.controls = {}
        self.visibility_rules = []
        self.event_handlers = {}
        self.create_widgets()
        self.create_buttons()

    def create_buttons(self):
        """Add buttons to print current and modified values to the console."""
        self.print_current_button = Button(self, text="Print Current Values", command=self.print_current_values)
        self.print_current_button.grid(row=100, column=0, pady=10, sticky="w")

        self.print_modified_button = Button(self, text="Print Modified Values", command=self.print_modified_values)
        self.print_modified_button.grid(row=100, column=1, pady=10, sticky="w")

    def create_widgets(self):
        # Parse the XML configuration file
        tree = ET.parse(self.config_editor_file)
        root = tree.getroot()

        # Loop through each setting and create the appropriate control
        row = 0
        for setting in root.findall("setting"):
            setting_name = setting.get("name")  # Retrieve the setting name attribute
            widget_type = setting.find("widget_type").text
            label_text = setting.find("label_text").text
            data_type = setting.find("data_type").text
            default_value = get_typed_data(data_type, setting.find("default_value").text)

    def get_original_values(self):
        """Return a dictionary of original values for all controls, with setting_name as the key."""
        original_values = {}
        for setting_name, control in self.controls.items():
            original_values[setting_name] = control.get_original_value()
        return original_values
            
    def get_current_values(self):
        """Return a dictionary of current values for all controls, with setting_name as the key."""
        current_values = {}
        for setting_name, control in self.controls.items():
            current_values[setting_name] = control.get_value()
        return current_values

    def get_modified_values(self):
        """Return a dictionary of modified values for all controls, with setting_name as the key."""
        return self.get_current_values()

    def get_config(self):
        """Return a dictionary of modified values for all controls, with setting_name as the key."""
        return self.get_modified_values()

    def print_current_values(self):
        """Print the current values dictionary to the console."""
        print("Current Values:\n", dict_to_text(self.get_current_values()))

    def print_modified_values(self):
        """Print the modified values dictionary to the console."""
        print("Modified Values:\n", dict_to_text(self.get_modified_values()))

    def setup_ui_from_config(self, font_config):
        """Set the control values based on the provided font configuration dictionary."""
        for setting_name, control in self.controls.items():
            if setting_name in font_config:
                control.set_value(font_config[setting_name])
