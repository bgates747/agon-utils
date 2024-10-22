import tkinter as tk
from tkinter import ttk
from config_manager import get_typed_data, load_xml
from agon_color_picker import AgonColorPicker

class FontConfigWidget(tk.Frame):
    def __init__(self, parent, config_setting, font_config_xml, **kwargs):
        super().__init__(parent, **kwargs)

        self.id = config_setting
        self.config_setting = config_setting
        self.parent = parent
        self.hidden = False

        self.font_config_xml = font_config_xml
        self.value_object = None  # Widget to get/set the value
        self.on_change_object = None  # Widget to trigger change events

        self.setting_dict = self._extract_setting_dict(config_setting)
        self.data_type = self.setting_dict.get('data_type', 'string')
        self._value = get_typed_data(self.data_type, self.setting_dict.get('default_value', ''))
        self.event_handlers = self._extract_event_handlers(self.setting_dict)
        self.description = self.setting_dict.get('description', '')
        self.label_text = self.setting_dict.get('label_text', '')

        # Create the label for the control
        self.pad_x = 0
        self.label = tk.Label(self, width=15, text=self.label_text, font=("Helvetica", 10), anchor="w")
        self.label.grid(row=0, column=0, padx=self.pad_x)

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

    def _handle_value_change(self, event=None):
        """Generic handler for value change events."""
        if self.on_change_object:
            self.value = self.on_change_object.get()  # Update value from the bound widget
        self.trigger_event_handlers('on_change')

    def _extract_event_handlers(self, setting_dict):
        """Dynamically extract all event handlers from the XML setting."""
        event_handlers = {}
        xml_event_handlers = setting_dict.get('event_handlers', {})

        for event_type, handlers in xml_event_handlers.items():
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

    def _extract_setting_dict(self, config_setting):
        """Extract the setting dictionary from the XML for a given setting name."""
        tag_xml = self.font_config_xml.find(f"./setting[@name='{config_setting}']")
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
        print(f"{self.config_setting}: default_on_change_handler fired - New Value: {new_value}")
    
    def default_redraw_font_handler(self):
        print(f"{self.config_setting}: default_redraw_font_handler fired")

    def raster_type_on_change_handler(self):
        new_value = self.value
        print(f"{self.config_setting}: raster_type_on_change_handler fired - New Value: {new_value}")

class FontConfigComboBox(FontConfigWidget):
    """A widget for displaying and selecting from a dropdown list of configuration values."""
    def __init__(self, parent, config_setting, font_config_xml, **kwargs):
        super().__init__(parent, config_setting, font_config_xml, **kwargs)
        self.options = self.setting_dict.get('options', [])
        self.combobox = ttk.Combobox(self, values=self.options, width=20)
        self.combobox.grid(row=0, column=1, padx=self.pad_x)
        self.value_object = self.combobox
        self.value_object.set(self._value)
        self.on_change_object = self.combobox
        self.on_change_object.bind("<<ComboboxSelected>>", self._handle_value_change)

class FontConfigTextBox(FontConfigWidget):
    """A widget for displaying and editing a text-based configuration value."""
    def __init__(self, parent, config_setting, font_config_xml, **kwargs):
        super().__init__(parent, config_setting, font_config_xml, **kwargs)
        self.text_entry = tk.Entry(self, width=22)
        self.text_entry.grid(row=0, column=1, padx=self.pad_x)

        # Set value_object and on_change_object to the entry widget
        self.value_object = self.text_entry
        self.on_change_object = self.text_entry

        # Set initial value
        self.value_object.insert(0, self._value)

        # Bind the generic change handler to focus out and return key events
        self.on_change_object.bind("<FocusOut>", self._handle_value_change)
        self.on_change_object.bind("<Return>", self._handle_value_change)

class FontConfigDeltaControl(FontConfigWidget):
    """A widget for handling delta_value adjustments with custom increment, bounds, and data-driven properties."""
    def __init__(self, parent, config_setting, font_config_xml, **kwargs):
        super().__init__(parent, config_setting, font_config_xml, **kwargs)

        # Extract step, min, and max values from the XML configuration
        self.step_value = get_typed_data(self.data_type, self.setting_dict.get('step_value', '1'))
        self.min_value = get_typed_data(self.data_type, self.setting_dict.get('min_value', '0'))
        self.max_value = get_typed_data(self.data_type, self.setting_dict.get('max_value', '100'))
        
        # Initialize the delta property
        self.delta = 0

        # Decrement button
        self.decrement_button = tk.Button(
            self, text="-", width=4, font=("Helvetica", 6), 
            command=self._decrement
        )
        self.decrement_button.grid(row=0, column=1, padx=self.pad_x)

        # Delta display
        self.delta_display = tk.Label(self, text=self._value, width=6, anchor="center")
        self.delta_display.grid(row=0, column=2, padx=self.pad_x)

        # Set value_object to the delta display
        self.value_object = self.delta_display

        # Increment button
        self.increment_button = tk.Button(
            self, text="+", width=4, font=("Helvetica", 6), 
            command=self._increment
        )
        self.increment_button.grid(row=0, column=3, padx=self.pad_x)

    def _increment(self):
        """Set delta to step_value and trigger the on-change event."""
        self.delta = self.step_value
        self.trigger_event_handlers('on_change')

    def _decrement(self):
        """Set delta to negative step_value and trigger the on-change event."""
        self.delta = -self.step_value
        self.trigger_event_handlers('on_change')

    def default_on_change_handler(self):
        """Override to handle delta adjustment and bounds checking."""
        new_value = self.value + self.delta

        # Check if the new value is within bounds
        if self.min_value <= new_value <= self.max_value:
            self.value = new_value  # Update the value if within bounds
            self.delta_display.config(text=str(self.value))  # Update the display
        else:
            print(f"{self.config_setting}: Value out of bounds ({self.min_value} to {self.max_value})")
        
        # Continue firing other event handlers, regardless of bounds check
        print(f"{self.config_setting}: default_on_change_handler fired - New Value: {self.value}")

class FontConfigColorPicker(FontConfigWidget):
    """A widget for displaying and selecting a color, showing the value as an RGBA tuple."""
    def __init__(self, parent, config_setting, font_config_xml, **kwargs):
        super().__init__(parent, config_setting, font_config_xml, **kwargs)

        # Initialize color_value from the default value
        self.color_value = self.parse_color(self._value)

        # Button to display and select color
        self.color_button = tk.Button(
            self, text=self.value, bg=self.rgb_to_hex(self.color_value),
            command=self.choose_color, width=22
        )
        self.color_button.grid(row=0, column=1, padx=0)

        # Set 'on_change_widget' to the color button for event handler binding
        self.on_change_widget = self.color_button
        self.on_change_event = "<<ColorChanged>>"  # Custom event identifier

        # Initialize specific event handlers
        if self.on_change_widget and self.on_change_event:
            self.on_change_widget.bind(self.on_change_event, self._handle_value_change)

    @property
    def value(self):
        """Get the current color value as an RGBA string."""
        return ','.join(map(str, self.color_value))

    @value.setter
    def value(self, new_value):
        """Set the current color value and update the display."""
        self.color_value = self.parse_color(new_value)

        # Update the button color and text
        self.color_button.config(
            bg=self.rgb_to_hex(self.color_value), 
            text=self.value
        )

    def parse_color(self, color_string):
        """Parse the color string to a tuple of integers (R, G, B, A)."""
        try:
            return tuple(map(int, color_string.split(',')))
        except ValueError:
            return (0, 0, 0, 255)  # Default to opaque black if parsing fails

    def rgb_to_hex(self, rgba):
        """Convert an RGBA tuple to a hex color code (ignoring alpha)."""
        return "#%02x%02x%02x" % (rgba[0], rgba[1], rgba[2])

    def choose_color(self):
        """Open a color chooser dialog to select a new color."""
        initial_color = self.color_value
        palette_control = self.parent.controls.get("palette")
        palette_name = palette_control.value if palette_control else None

        # Open the color chooser
        rgb_color, hex_color = AgonColorPicker.askcolor(
            color=self.rgb_to_hex(self.color_value), 
            parent=self, 
            palette_name=palette_name
        )
        
        if rgb_color:
            new_color_value = (int(rgb_color[0]), int(rgb_color[1]), int(rgb_color[2]), self.color_value[3])

            if new_color_value != initial_color:
                # Update the color value and explicitly set the control value
                self.color_value = new_color_value
                self.value = self.value  # Trigger setter to update UI elements

                # Trigger on_change event if color has changed
                self.on_change_widget.event_generate(self.on_change_event)

if __name__ == "__main__":
    # Load the XML file
    xml_filepath = 'examples/font_editor/src/python/font_config_editor.xml'
    root_element = load_xml(xml_filepath)

    if root_element is not None:
        # Create the Tkinter app
        root = tk.Tk()
        root.title("Font Config Editor")

        # Define setting name
        config_setting = "raster_type"
        font_config_combobox = FontConfigComboBox(root, config_setting, root_element)
        font_config_combobox.pack(padx=10, pady=0)

        config_setting = "font_name"
        font_config_textbox = FontConfigTextBox(root, config_setting, root_element)
        font_config_textbox.pack(padx=10, pady=0)

        config_setting = "point_size"
        font_config_delta = FontConfigDeltaControl(root, config_setting, root_element)
        font_config_delta.pack(padx=10, pady=0)

        config_setting = "fg_color"
        font_config_color = FontConfigColorPicker(root, config_setting, root_element)
        font_config_color.pack(padx=10, pady=0)

        # Start the Tkinter event loop
        root.mainloop()
