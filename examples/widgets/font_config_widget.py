import tkinter as tk
from tkinter import ttk
import xml.etree.ElementTree as ET
from config_manager import get_typed_data

class FontConfigWidget(tk.Frame):
    """Base widget class for common font configuration controls."""

    def __init__(self, parent, config_setting, font_config_xml, **kwargs):
        super().__init__(parent, **kwargs)

        # Parse the XML configuration and filter for the specific setting
        config_xml = ET.fromstring(font_config_xml)
        self.setting_xml = config_xml.find(f".//setting[@name='{config_setting}']")

        # Extract common properties from the XML
        self.data_type = self.setting_xml.find('data_type').text
        self.default_value = get_typed_data(self.data_type, self.setting_xml.find('default_value').text)
        self.label_text = self.setting_xml.find('label_text').text
        self.visible = self._extract_nested_dict('visible')
        self.event_handlers = self._extract_nested_dict('event_handlers')

        # Create the control based on the specific widget type
        self.pad_x = 0
        self.label = tk.Label(self, width=15, text=self.label_text, font=("Helvetica", 10), anchor="w")
        self.label.grid(row=0, column=0, padx=self.pad_x)

    def _extract_nested_dict(self, tag_name):
        """Extract nested dictionary structure from XML for a given tag."""
        def recurse_element(element):
            nested_dict = {}
            for child in element:
                if child.tag == 'item':
                    # If the tag is 'item', add directly to list without an extra key
                    if isinstance(nested_dict, list):
                        nested_dict.append(child.text)
                    else:
                        nested_dict = [child.text] if not nested_dict else nested_dict + [child.text]
                elif len(child):
                    nested_dict[child.tag] = recurse_element(child)
                else:
                    if child.tag in nested_dict:
                        if isinstance(nested_dict[child.tag], list):
                            nested_dict[child.tag].append(child.text)
                        else:
                            nested_dict[child.tag] = [nested_dict[child.tag], child.text]
                    else:
                        nested_dict[child.tag] = child.text if len(element.findall(child.tag)) == 1 else [child.text]
            return nested_dict

        tag_xml = self.setting_xml.find(tag_name) if self.setting_xml is not None else None
        return recurse_element(tag_xml) if tag_xml is not None else {}

class FontConfigComboBox(FontConfigWidget):
    """A widget for displaying and selecting from a dropdown list of configuration values."""

    def __init__(self, parent, config_setting, font_config_xml, **kwargs):
        super().__init__(parent, config_setting, font_config_xml, **kwargs)

        # Test code
        self.options_dict = self._extract_nested_dict('options')

        # Extract options and default value from the XML
        options = [get_typed_data(self.data_type, option.text) for option in self.setting_xml.findall("options/item")] if self.setting_xml is not None else []

        # Dropdown (combobox) for selecting a value
        self.selected_var = tk.StringVar(value=self.default_value)
        self.combobox = ttk.Combobox(self, textvariable=self.selected_var, values=options, width=20, state="readonly")
        self.combobox.grid(row=0, column=1, padx=self.pad_x)
        self.combobox.set(self.default_value) 

    def get_value(self):
        """Return the currently selected value in the combobox."""
        return get_typed_data(self.data_type, self.selected_var.get())

    def set_value(self, value):
        """Set the selected value in the combobox."""
        value = get_typed_data(self.data_type, value)
        if value in self.combobox['values']:
            self.selected_var.set(value)
            self.combobox.set(value)
