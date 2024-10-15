
import tkinter as tk
from tkinter import ttk, Button
import xml.etree.ElementTree as ET
from custom_widgets import DeltaControl, ConfigTextBox, ConfigComboBox
from config_manager import get_typed_data, dict_to_text

class FontConfigEditor(tk.Frame):
    """
    A dynamic editor for font configurations, creating controls based on data-driven configuration.
    """
    def __init__(self, parent, config_file, app_reference, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.app_reference = app_reference  # Store the app reference
        self.config_file = config_file
        self.controls = {}  # Dictionary to store controls by setting_name
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
        tree = ET.parse(self.config_file)
        root = tree.getroot()

        # Loop through each setting and create the appropriate control
        row = 0
        for setting in root.findall("setting"):
            setting_name = setting.get("name")  # Retrieve the setting name attribute
            widget_type = setting.find("widget_type").text
            label_text = setting.find("label_text").text
            data_type = setting.find("data_type").text
            default_value = get_typed_data(data_type, setting.find("default_value").text)
            
            # Initialize the control based on widget_type
            setting_control = None
            if widget_type == "DeltaControl":
                # DeltaControl requires min, max, and step values
                min_value = get_typed_data(data_type, setting.find("min_value").text)
                max_value = get_typed_data(data_type, setting.find("max_value").text)
                step_value = get_typed_data(data_type, setting.find("step_value").text)
                setting_control = DeltaControl(self, label_text, data_type, default_value, min_value, max_value, step_value)

            elif widget_type == "ConfigTextBox":
                # ConfigTextBox with only label and default value
                setting_control = ConfigTextBox(self, label_text, default_value)
                
            elif widget_type == "ConfigComboBox":
                # ConfigComboBox requires additional options
                options = [opt.text for opt in setting.find("options").findall("value")]
                setting_control = ConfigComboBox(self, label_text, options, default_value)
                
            # Place control in the grid if it was created
            if setting_control:
                setting_control.grid(row=row, column=0, pady=0, padx=10, sticky="w")
                self.controls[setting_name] = setting_control
                row += 1

    def get_current_values(self):
        """Return a dictionary of current values for all controls, with setting_name as the key."""
        current_values = {}
        for setting_name, control in self.controls.items():
            if isinstance(control, DeltaControl):
                current_values[setting_name] = control.current_value
            elif isinstance(control, ConfigTextBox) or isinstance(control, ConfigComboBox):
                current_values[setting_name] = control.get_value()
        return current_values

    def get_modified_values(self):
        """Return a dictionary of modified values for all controls, with setting_name as the key."""
        modified_values = {}
        for setting_name, control in self.controls.items():
            if isinstance(control, DeltaControl):
                modified_values[setting_name] = float(control.modified_var.get()) if control.data_type == 'float' else int(control.modified_var.get())
            elif isinstance(control, ConfigTextBox) or isinstance(control, ConfigComboBox):
                modified_values[setting_name] = control.get_value()
        return modified_values

    def print_current_values(self):
        """Print the current values dictionary to the console."""
        print("Current Values:\n", dict_to_text(self.get_current_values()))

    def print_modified_values(self):
        """Print the modified values dictionary to the console."""
        print("Modified Values:\n", dict_to_text(self.get_modified_values()))