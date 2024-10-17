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
        self.options_dict = self._extract_nested_dict('options')  # Keep options_dict for compatibility

        # Create the control based on the specific widget type
        self.pad_x = 0
        self.label = tk.Label(self, width=15, text=self.label_text, font=("Helvetica", 10), anchor="w")
        self.label.grid(row=0, column=0, padx=self.pad_x)

        # Set the value object for easier access to get/set methods
        self.value_object = None

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
    
    def get_value(self):
        """Return the current value of the control."""
        if self.value_object:
            return get_typed_data(self.data_type, self.value_object.get())
        return None

    def set_value(self, value):
        """Set the value of the control."""
        value = get_typed_data(self.data_type, value)
        if self.value_object and value in self.value_object['values']:
            self.value_object.set(value)
    
    def set_default_value(self):
        """Set the default value for the control."""
        self.set_value(self.default_value)

    def _initialize_event_handlers(self):
        """Initialize event handlers based on XML configuration."""
        for event_name, handlers in self.event_handlers.items():
            if isinstance(handlers, list):
                for handler_name in handlers:
                    self._bind_event_handler(event_name, handler_name)
            else:
                self._bind_event_handler(event_name, handlers)

    def _bind_event_handler(self, event_name, handler_name):
        """Bind an event handler dynamically."""
        handler = getattr(self, handler_name, None)
        if callable(handler):
            # Bind specific event types for different controls
            widget = getattr(self, 'widget', None)
            if event_name == 'on_change' and widget:
                # Bind to <<ComboboxSelected>> event for ComboBox
                widget.bind("<<ComboboxSelected>>", handler)

    # Default change handler
    def default_on_change_handler(self, event):
        """Default handler for on_change events."""
        print(f"Default on_change handler called for {self.label_text} with value: {self.get_value()}")

    # Example handlers
    def foo_handler(self, event):
        """Example event handler."""
        print("foo_handler called!")

    def bar_handler(self, event):
        """Another example event handler."""
        print("bar_handler called!")

class FontConfigComboBox(FontConfigWidget):
    """A widget for displaying and selecting from a dropdown list of configuration values."""

    def __init__(self, parent, config_setting, font_config_xml, **kwargs):
        super().__init__(parent, config_setting, font_config_xml, **kwargs)

        # Extract options and default value from the XML
        options = [get_typed_data(self.data_type, option.text) for option in self.setting_xml.findall("options/item")] if self.setting_xml is not None else []

        # Dropdown (combobox) for selecting a value
        self.selected_var = tk.StringVar(value=self.default_value)
        self.combobox = ttk.Combobox(self, textvariable=self.selected_var, values=options, width=20, state="readonly")
        self.combobox.grid(row=0, column=1, padx=self.pad_x)
        self.combobox.set(self.default_value)

        # Set the value object for easier access
        self.value_object = self.selected_var

        # Set 'widget' to the combobox for event handler binding
        self.widget = self.combobox

        # Initialize event handlers after widget setup
        self._initialize_event_handlers()

    # Custom on_change handler for the ComboBox
    def palette_on_change_handler(self, event):
        """Custom on_change handler for the palette setting."""
        print(f"Palette changed to: {self.get_value()}")
