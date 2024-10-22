import tkinter as tk
from tkinter import ttk
import xml.etree.ElementTree as ET

def get_typed_data(data_type, value):
    """Convert value to specified data type."""
    if data_type == 'int':
        return int(value)
    elif data_type == 'float':
        return float(value)
    elif data_type == 'bool':
        return value.lower() in ('true', '1', 'yes')
    else:  # Default to string
        return str(value)

class FontConfigWidget(tk.Frame):
    def __init__(self, parent, setting_name, setting_xml, **kwargs):
        super().__init__(parent, **kwargs)
        self.setting_name = setting_name
        self.setting_xml = setting_xml
        self.value_object = None  
        self.setting_dict = self._extract_setting_dict(setting_name)
        self.data_type = self.setting_dict.get('data_type', 'string')
        self._value = get_typed_data(self.data_type, self.setting_dict.get('default_value', ''))
        self.event_handlers = self._extract_event_handlers(self.setting_dict)

    @property
    def value(self):
        """Return the current value of the control."""
        return self._value

    @value.setter
    def value(self, new_value):
        """Set the current value of the control, converting to the specified data type."""
        self._value = get_typed_data(self.data_type, new_value)
        if self.value_object and hasattr(self.value_object, 'set'):
            self.value_object.set(self._value)

    def _extract_event_handlers(self, setting_dict):
        """Dynamically extract all event handlers from the XML setting."""
        event_handlers = {}
        xml_event_handlers = setting_dict.get('event_handlers', {})

        # Loop through each event type in the event handlers
        for event_type, handlers in xml_event_handlers.items():
            # Ensure handlers are extracted as a list of strings
            if isinstance(handlers, dict):
                handlers_list = [handlers['item']] if 'item' in handlers else []
            elif isinstance(handlers, list):
                handlers_list = [item['item'] if isinstance(item, dict) else item for item in handlers]
            else:
                handlers_list = []

            event_handlers[event_type] = handlers_list

        return event_handlers

    def trigger_event_handlers(self, event_type):
        """Trigger all event handlers for the given event type dynamically."""
        if event_type in self.event_handlers:
            for handler_name in self.event_handlers[event_type]:
                handler = getattr(self, handler_name, None)
                if handler:
                    handler()

    def _extract_setting_dict(self, setting_name):
        """Extract the setting dictionary from the XML for a given setting name."""
        tag_xml = self.setting_xml.find(f"./setting[@name='{setting_name}']")
        if tag_xml is None:
            return {}

        setting_dict = self._parse_element(tag_xml)
        return setting_dict

    def _parse_element(self, element):
        """Recursively parse an XML element and return a dictionary representation."""
        parsed_dict = {}
        for child in element:
            if child.tag == 'options':
                parsed_dict[child.tag] = [item.text for item in child.findall('item')]
            elif child.tag == 'event_handlers':
                parsed_dict[child.tag] = self._parse_event_handlers(child)
            elif len(child):
                parsed_dict[child.tag] = self._parse_element(child)
            else:
                parsed_dict[child.tag] = child.text
        return parsed_dict

    def _parse_event_handlers(self, element):
        """Parse event handlers from the XML element."""
        event_handlers = {}
        for child in element:
            event_type = child.tag
            event_handlers[event_type] = [item.text for item in child.findall('item')]
        return event_handlers
    
    def default_on_change_handler(self):
        new_value = self.value
        print(f"{self.setting_name}: default_on_change_handler fired - New Value: {new_value}")
    
    def default_redraw_font_handler(self):
        print(f"{self.setting_name}: default_redraw_font_handler fired")


class FontConfigComboBox(FontConfigWidget):
    def __init__(self, parent, setting_name, setting_xml, **kwargs):
        super().__init__(parent, setting_name, setting_xml, **kwargs)

        # Get value options from the setting dictionary
        self.options = self.setting_dict.get('options', [])

        # Set the label for the combobox
        label_text = self.setting_dict.get('label_text', 'Setting')
        self.label = tk.Label(self, text=label_text)
        self.label.pack(padx=5, pady=5, anchor='w')

        # Combobox for selecting options
        self.combobox = ttk.Combobox(self, values=self.options)
        self.combobox.set(self._value)
        self.combobox.pack(padx=5, pady=5, anchor='w')

        # Set value_object to the combobox
        self.value_object = self.combobox

        # Bind the combobox-specific event handler
        self.combobox.bind("<<ComboboxSelected>>", self._handle_combobox_change)

    def _handle_combobox_change(self, event):
        """Handle the Combobox selection change and call event handlers dynamically."""
        self.value = self.combobox.get()
        self.trigger_event_handlers('on_change')

    def raster_type_on_change_handler(self):
        new_value = self.value
        print(f"{self.setting_name}: raster_type_on_change_handler fired - New Value: {new_value}")

def load_xml(xml_filepath):
    """Load an XML file and return the root XML element."""
    try:
        tree = ET.parse(xml_filepath)
        return tree.getroot()
    except FileNotFoundError:
        print(f"Error: Could not find XML file {xml_filepath}")
        return None
    except ET.ParseError:
        print(f"Error: Could not parse XML file {xml_filepath}")
        return None


if __name__ == "__main__":
    # Load the XML file
    xml_filepath = 'examples/font_editor/src/python/font_config_editor.xml'
    root_element = load_xml(xml_filepath)

    if root_element is not None:
        # Create the Tkinter app
        root = tk.Tk()
        root.title("Font Config Editor")

        # Define setting name
        setting_name = "raster_type"

        # Create and pack the FontConfigComboBox
        font_config_combobox = FontConfigComboBox(root, setting_name, root_element)
        font_config_combobox.pack(padx=10, pady=10)

        # Start the Tkinter event loop
        root.mainloop()
