import tkinter as tk
from tkinter import ttk, Button
import xml.etree.ElementTree as ET
from font_config_widget import FontConfigDeltaControl, FontConfigTextBox, FontConfigComboBox, FontConfigColorPicker
from config_manager import get_typed_data, dict_to_text, load_xml

class FontConfigEditor(tk.Frame):
    """
    A dynamic editor for font configurations, creating controls based on data-driven configuration.
    """
    def __init__(self, parent, config_editor_file, app_reference, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.app_reference = app_reference
        self.config_editor_file = config_editor_file
        self.font_config_xml = load_xml(self.config_editor_file)
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
        self.print_modified_button.grid(row=101, column=0, pady=10, sticky="w")

        self.print_original_button = Button(self, text="Print Original Values", command=self.print_original_values)
        self.print_original_button.grid(row=102, column=0, pady=10, sticky="w")

    def create_widgets(self):
        # Loop through each setting and create the appropriate control
        row = 0
        for setting in self.font_config_xml.findall("setting"):
            config_setting = setting.get("name")
            widget_type = setting.find("widget_type").text
            if widget_type == "FontConfigDeltaControl":
                control = FontConfigDeltaControl(self, config_setting, self.font_config_xml)
            elif widget_type == "FontConfigTextBox":
                control = FontConfigTextBox(self, config_setting, self.font_config_xml)
            elif widget_type == "FontConfigComboBox":
                control = FontConfigComboBox(self, config_setting, self.font_config_xml)
            elif widget_type == "FontConfigColorPicker":
                control = FontConfigColorPicker(self, config_setting, self.font_config_xml)
            else:
                raise ValueError(f"Unsupported widget type: {widget_type}")
            
            control.grid(row=row, column=0, sticky="w")
            self.controls[config_setting] = control
            row += 1

    def get_original_values(self):
        """Return a dictionary of original values for all controls, with config_setting as the key."""
        original_values = {}
        for config_setting, control in self.controls.items():
            original_values[config_setting] = control.get_original_value()
        return original_values
            
    def get_current_values(self):
        """Return a dictionary of current values for all controls, with config_setting as the key."""
        current_values = {}
        for config_setting, control in self.controls.items():
            current_values[config_setting] = control.get_value()
        return current_values

    def get_modified_values(self):
        """Return a dictionary of modified values for all controls, with config_setting as the key."""
        return self.get_current_values()

    def get_config(self):
        """Return a dictionary of modified values for all controls, with config_setting as the key."""
        return self.get_modified_values()

    def print_current_values(self):
        """Print the current values dictionary to the console."""
        print("Current Values:\n", dict_to_text(self.get_current_values()))

    def print_modified_values(self):
        """Print the modified values dictionary to the console."""
        print("Modified Values:\n", dict_to_text(self.get_modified_values()))

    def print_original_values(self):
        """Print the original values dictionary to the console."""
        print("Original Values:\n", dict_to_text(self.get_original_values()))

    def setup_ui_from_config(self, font_config):
        """Set the control values based on the provided font configuration dictionary."""
        for config_setting, control in self.controls.items():
            if config_setting in font_config:
                control.set_value(font_config[config_setting])
