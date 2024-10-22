import tkinter as tk
from tkinter import ttk
import xml.etree.ElementTree as ET

class FontConfigWidget(tk.Frame):
    def __init__(self, parent, setting_name, setting_xml, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.setting_name = setting_name
        self.setting_xml = setting_xml

        # Extract complete setting dictionary from XML
        self.setting_dict = self._extract_setting_dict(setting_name)

        # Debug: Print the full setting dictionary
        print(f"Setting Dictionary for '{self.setting_name}': {self.setting_dict}")

        # Extract default value from the setting dictionary
        self.default_value = self.setting_dict.get('default_value', None)

        # Extract dynamic event handlers from XML
        self.event_handlers = self._extract_event_handlers(self.setting_dict)

    def _extract_event_handlers(self, setting_dict):
        """Dynamically extract all event handlers from the XML setting."""
        event_handlers = {}
        xml_event_handlers = setting_dict.get('event_handlers', {})

        # Loop through each event type in the event handlers
        for event_type, handlers in xml_event_handlers.items():
            # Ensure handlers are extracted as a list of strings
            if isinstance(handlers, dict):
                # Extract all 'item' elements within the event type
                handlers_list = [handlers['item']] if 'item' in handlers else []
            elif isinstance(handlers, list):
                # Extract handler names from each item
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
        # Find the specific setting element by name
        tag_xml = self.setting_xml.find(f"./setting[@name='{setting_name}']")
        if tag_xml is None:
            return {}

        # Build the nested dictionary for the found setting
        setting_dict = self._parse_element(tag_xml)
        return setting_dict

    def _parse_element(self, element):
        """Recursively parse an XML element and return a dictionary representation."""
        parsed_dict = {}
        for child in element:
            if child.tag == 'options':
                # Extract list of items under 'options'
                parsed_dict[child.tag] = [item.text for item in child.findall('item')]
            elif child.tag == 'event_handlers':
                # Parse event handlers specifically
                parsed_dict[child.tag] = self._parse_event_handlers(child)
            elif len(child):
                # Recursively parse nested elements
                parsed_dict[child.tag] = self._parse_element(child)
            else:
                # Handle simple text elements
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
        print(f"{self.setting_name}: default_on_change_handler fired")
    
    def default_redraw_font_handler(self):
        print(f"{self.setting_name}: default_redraw_font_handler fired")


class FontConfigComboBox(FontConfigWidget):
    def __init__(self, parent, setting_name, setting_xml, **kwargs):
        super().__init__(parent, setting_name, setting_xml, **kwargs)

        # Get value options from the setting dictionary
        self.options = self.setting_dict.get('options', [])

        # Debug: Print options and default value
        print(f"Options for '{setting_name}': {self.options}")
        print(f"Default Value for '{setting_name}': {self.default_value}")

        # Set the label for the combobox
        label_text = self.setting_dict.get('label_text', 'Setting')
        self.label = tk.Label(self, text=label_text)
        self.label.pack(padx=5, pady=5, anchor='w')

        # Combobox for selecting options
        self.combobox = ttk.Combobox(self, values=self.options)
        self.combobox.set(self.default_value)
        self.combobox.pack(padx=5, pady=5, anchor='w')

        # Bind the combobox-specific event handler
        self.combobox.bind("<<ComboboxSelected>>", self._handle_combobox_change)

    def _handle_combobox_change(self, event):
        """Handle the Combobox selection change and call event handlers dynamically."""
        new_value = self.combobox.get()
        print(f"{self.setting_name}: New Value Selected - {new_value}")

        # Call generic handlers for 'on_change' event type
        self.trigger_event_handlers('on_change')

    # Setting-specific event handler
    def raster_type_on_change_handler(self):
        new_value = self.combobox.get()
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
