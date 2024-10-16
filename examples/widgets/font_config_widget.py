import tkinter as tk
from tkinter import ttk
import xml.etree.ElementTree as ET

class FontConfigWidget(tk.Frame):
    """Base widget class for common font configuration controls."""

    def __init__(self, parent, config_setting, font_config_xml, **kwargs):
        super().__init__(parent, **kwargs)

        # Parse the XML configuration and filter for the specific setting
        self.config_xml = ET.fromstring(font_config_xml)
        self.setting_xml = self.config_xml.find(f".//setting[@name='{config_setting}']")

        # Extract label text from the XML
        label_text = self.setting_xml.find('label_text').text if self.setting_xml is not None else "Unknown Setting"

        self.pad_x = 0  # Padding for grid layout

        # Main label for the control
        self.label = tk.Label(self, width=15, text=label_text, font=("Helvetica", 10), anchor="w")
        self.label.grid(row=0, column=0, padx=self.pad_x)


class FontConfigComboBox(FontConfigWidget):
    """A widget for displaying and selecting from a dropdown list of configuration values."""

    def __init__(self, parent, config_setting, font_config_xml, **kwargs):
        super().__init__(parent, config_setting, font_config_xml, **kwargs)

        # Extract options and default value from the XML
        options = [option.text for option in self.setting_xml.findall("options/value")] if self.setting_xml is not None else []
        default_value = self.setting_xml.find('default_value').text if self.setting_xml is not None else ""

        # Dropdown (combobox) for selecting a value
        self.selected_var = tk.StringVar(value=default_value)
        self.combobox = ttk.Combobox(self, textvariable=self.selected_var, values=options, width=20, state="readonly")
        self.combobox.grid(row=0, column=1, padx=self.pad_x)
        self.combobox.set(default_value)  # Set default selection

    def get_value(self):
        """Return the currently selected value in the combobox."""
        return self.selected_var.get()

    def set_value(self, value):
        """Set the selected value in the combobox."""
        if value in self.combobox['values']:
            self.selected_var.set(value)
            self.combobox.set(value)