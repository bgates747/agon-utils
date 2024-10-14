
from tkinter import ttk
import xml.etree.ElementTree as ET
from custom_widgets import DeltaControl, get_typed_data


class FontConfigEditor(ttk.Frame):
    """
    A dynamic editor for font configurations, creating controls based on data-driven configuration.
    """
    def __init__(self, parent, config_file, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.config_file = config_file
        self.create_widgets()

    def create_widgets(self):
        # Parse the XML configuration file
        tree = ET.parse(self.config_file)
        root = tree.getroot()

        # Loop through each setting and create a DeltaControl for it
        row = 0
        for setting in root.findall("setting"):
            widget_type = setting.find("widget_type").text
            label_text = setting.find("label_text").text
            data_type = setting.find("data_type").text
            default_value = get_typed_data(data_type, setting.find("default_value").text)

            if widget_type == "DeltaControl":
                # Create DeltaControl with XML-defined data properties
                min_value = get_typed_data(data_type, setting.find("min_value").text)
                max_value = get_typed_data(data_type, setting.find("max_value").text)
                step_value = get_typed_data(data_type, setting.find("step_value").text)
                
                delta_control = DeltaControl(self, label_text, data_type, default_value, min_value, max_value, step_value)
                delta_control.grid(row=row, column=0, pady=0, padx=10, sticky="w")

            row += 1

    def get_current_values(self):
        """Return a dictionary of current values for all controls, with setting_name as the key."""
        current_values = {}
        for setting_name, control in self.controls.items():
            current_values[setting_name] = control.current_value
        return current_values

    def get_modified_values(self):
        """Return a dictionary of modified values for all controls, with setting_name as the key."""
        modified_values = {}
        for setting_name, control in self.controls.items():
            modified_values[setting_name] = float(control.modified_var.get()) if control.data_type == 'float' else int(control.modified_var.get())
        return modified_values

