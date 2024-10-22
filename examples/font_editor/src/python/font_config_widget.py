
import tkinter as tk
from tkinter import ttk
import xml.etree.ElementTree as ET
from config_manager import get_typed_data
from abc import ABC, abstractmethod
from agon_color_picker import AgonColorPicker

class FontConfigWidget(tk.Frame, ABC):
    """Base widget class for common font configuration controls."""

    def __init__(self, parent, config_setting, config_xml, **kwargs):
        super().__init__(parent, **kwargs)

        self.id = config_setting
        self.parent = parent
        self.hidden = False  # Custom attribute to manage visibility state

        # Parse the XML configuration and filter for the specific setting
        self.setting_xml = config_xml.find(f".//setting[@name='{config_setting}']")

        # Extract common properties from the XML
        self.data_type = self.setting_xml.find('data_type').text
        self.label_text = self.setting_xml.find('label_text').text
        self.visible = self._extract_nested_dict('visible')
        self.event_handlers = self._extract_nested_dict('event_handlers')
        self.options_dict = self._extract_nested_dict('options')
        self.description = self.setting_xml.find('description').text if self.setting_xml.find('description') is not None else ""
        self._default_value = get_typed_data(self.data_type, self.setting_xml.find('default_value').text)

        # Value properties
        self._value = self._default_value
        self.value_display_object = None

        # Create the common label for the setting type
        self.pad_x = 0
        self.config_label = tk.Label(self, width=15, text=self.label_text, font=("Helvetica", 10), anchor="w")
        self.config_label.grid(row=0, column=0, padx=self.pad_x)

        # Initialize event handlers
        self.on_change_event = None  # Define on_change_event in the base class
        self.on_change_widget = None  # Define on_change_widget in the base class
        self._initialize_event_handlers()

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        self._value = get_typed_data(self.data_type, new_value)
        if self.value_display_object:
            self.value_display_object.set(self._value)

    @property
    def default_value(self):
        return self._default_value

    @default_value.setter
    def default_value(self, value):
        self._default_value = get_typed_data(self.data_type, value)

    @abstractmethod
    def create_value_display_object(self):
        """Abstract method to create and assign the value display widget."""
        pass

    @abstractmethod
    def bind_on_change_event(self):
        """Abstract method to bind value change events to the specific widget."""
        pass

    def _extract_nested_dict(self, tag_name):
        """Extract nested dictionary structure from XML for a given tag."""
        def recurse_element(element):
            nested_dict = {}
            for child in element:
                if child.tag == 'item':
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

    def _bind_event_handler(self, event_name, handler_name):
        """Bind an event handler dynamically and support multiple handlers for the same event."""
        handler = getattr(self, handler_name, None)
        if callable(handler):
            widget = self.on_change_widget
            if widget:
                if not hasattr(widget, '_event_handlers'):
                    widget._event_handlers = {}
                if event_name not in widget._event_handlers:
                    widget._event_handlers[event_name] = []

                widget._event_handlers[event_name].append(handler)

                def combined_handler(event, handlers=widget._event_handlers[event_name]):
                    for h in handlers:
                        h(event)

                if event_name == 'on_change' and self.on_change_event:
                    widget.bind(self.on_change_event, combined_handler)

    def _initialize_event_handlers(self):
        """Initialize specific event handlers for events."""
        # Initialize event handlers after widget setup
        for event_name, handlers in self.event_handlers.items():
            if isinstance(handlers, list):
                for handler_name in handlers:
                    self._bind_event_handler(event_name, handler_name)
            else:
                self._bind_event_handler(event_name, handlers)

    # Default change handler
    def default_on_change_handler(self, event):
        """Default handler for on_change events."""
        print(f"Default on_change handler called for {self.id} ({self.label_text}) with value: {self.value}")
        self.parent.set_visible(self.id)

    # Default hover handlers
    def default_on_mouse_enter(self, event):
        """Display a tooltip with the description on hover."""
        self.tooltip = tk.Toplevel(self)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{event.x_root}+{event.y_root - 30}")
        label = tk.Label(self.tooltip, text=self.description, background="cyan", relief="solid", borderwidth=1, font=("Helvetica", 8))
        label.pack()

    def default_on_mouse_leave(self, event):
        """Destroy the tooltip on mouse leave."""
        if hasattr(self, 'tooltip'):
            self.tooltip.destroy()
            del self.tooltip

    # Default redraw font handler
    def default_redraw_font_handler(self, event):
        """Default handler for redrawing the font image."""
        print(f"Redrawing font image for {self.id} ({self.label_text})")
        self.parent.render_font()

class FontConfigComboBox(FontConfigWidget):
    """A widget for displaying and selecting from a dropdown list of configuration values."""

    def __init__(self, parent, config_setting, font_config_xml, **kwargs):
        super().__init__(parent, config_setting, font_config_xml, **kwargs)

        # Extract options and default value from the XML
        options = [get_typed_data(self.data_type, option.text) for option in self.setting_xml.findall("options/item")] if self.setting_xml is not None else []

        # Create and assign the value display object
        self.create_value_display_object(options)

        # Set 'on_change_widget' to the combobox for event handler binding
        self.on_change_widget = self.combobox
        self.on_change_event = "<<ComboboxSelected>>"

        # Initialize specific event handlers
        self.bind_on_change_event()
        self._initialize_event_handlers()

    def create_value_display_object(self, options):
        """Create and assign the value display widget."""
        self.selected_var = tk.StringVar(value=self.default_value)
        self.combobox = ttk.Combobox(self, textvariable=self.selected_var, values=options, width=20, state="readonly")
        self.combobox.grid(row=0, column=1, padx=self.pad_x)
        self.combobox.set(self.default_value)
        self.value_display_object = self.selected_var

    def bind_on_change_event(self):
        """Bind value change events to the specific widget."""
        if self.on_change_widget and self.on_change_event:
            self.on_change_widget.bind(self.on_change_event, self.default_on_change_handler)

    def set_combo_options(self, options):
        """Set the available options for the ComboBox."""
        if isinstance(options, (list, dict)):
            self.combobox['values'] = list(options)

class FontConfigTextBox(FontConfigWidget):
    """A widget for displaying and editing a text-based configuration value."""

    def __init__(self, parent, config_setting, font_config_xml, **kwargs):
        super().__init__(parent, config_setting, font_config_xml, **kwargs)

        # Create and assign the value display object
        self.create_value_display_object()

        # Set 'on_change_widget' to the text entry for event handler binding
        self.on_change_widget = self.text_entry
        self.on_change_event = "<FocusOut>"  # Set the event type for text entry

        # Initialize specific event handlers
        self.bind_on_change_event()
        self._initialize_event_handlers()

        # Bind the Enter key to trigger focus out
        self.text_entry.bind("<Return>", self.trigger_focus_out)

    def create_value_display_object(self):
        """Create and assign the value display widget."""
        self.text_var = tk.StringVar(value=self.default_value)
        self.text_entry = tk.Entry(self, textvariable=self.text_var, width=22)
        self.text_entry.grid(row=0, column=1, padx=self.pad_x)
        self.value_display_object = self.text_var

        # Bind the variable to trigger value update when it changes
        self.text_var.trace_add("write", self._on_text_change)

    def bind_on_change_event(self):
        """Bind value change events to the specific widget."""
        if self.on_change_widget and self.on_change_event:
            self.on_change_widget.bind(self.on_change_event, self.default_on_change_handler)

    def _on_text_change(self, *args):
        """Callback when the text variable changes."""
        new_value = self.text_var.get()
        self.value = new_value  # Update the value property

    def trigger_focus_out(self, event=None):
        """Trigger a focus out event to activate the on_change event."""
        self.on_change_widget.event_generate("<FocusOut>")

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        # Update the internal value and the display object
        self._value = get_typed_data(self.data_type, new_value)
        if self.value_display_object:
            self.value_display_object.set(self._value)


class FontConfigDeltaControl(FontConfigWidget):
    """A widget for handling delta_value adjustments with custom increment, bounds, and data-driven properties."""

    def __init__(self, parent, config_setting, font_config_xml, **kwargs):
        super().__init__(parent, config_setting, font_config_xml, **kwargs)

        # Extract configuration from XML
        self.step_value = get_typed_data(self.data_type, self.setting_xml.find('step_value').text)

        # Create and assign the value display object
        self.create_value_display_object()

        # Set 'on_change_widget' to the delta display for event handler binding
        self.on_change_widget = self.delta_display
        self.on_change_event = "<<ValueChanged>>"  # Custom event identifier

        # Initialize specific event handlers
        self.bind_on_change_event()
        self._initialize_event_handlers()

    def create_value_display_object(self):
        """Create and assign the value display widget."""
        # Set button width property
        self.button_width = 4  # Define a fixed width for the buttons

        # Main label for the control
        self.config_label = tk.Label(self, width=15, text=self.label_text, font=("Helvetica", 10), anchor="w")
        self.config_label.grid(row=0, column=0, padx=self.pad_x)

        # Decrement button
        self.decrement_button = tk.Button(self, text="-", width=self.button_width, font=("Helvetica", 6), command=lambda: self.step_delta(-self.step_value))
        self.decrement_button.grid(row=0, column=2, padx=self.pad_x)

        # Delta display
        self.delta_var = tk.StringVar(value="0")
        self.delta_display = tk.Label(self, textvariable=self.delta_var, width=4, anchor="center")
        self.delta_display.grid(row=0, column=3, padx=self.pad_x)
        self.value_display_object = self.delta_var

        # Increment button
        self.increment_button = tk.Button(self, text="+", width=self.button_width, font=("Helvetica", 6), command=lambda: self.step_delta(self.step_value))
        self.increment_button.grid(row=0, column=4, padx=self.pad_x)

    def bind_on_change_event(self):
        """Bind value change events to the specific widget."""
        if self.on_change_widget and self.on_change_event:
            self.on_change_widget.bind(self.on_change_event, self.default_on_change_handler)

    def step_delta(self, step_value):
        """Modify the delta, updating the modified value within constraints and calculating delta from current value."""
        self.value += step_value 
        self.on_change_widget.event_generate(self.on_change_event)

class FontConfigColorPicker(FontConfigWidget):
    """A widget for displaying and selecting a color, showing the value as an RGBA tuple."""

    def __init__(self, parent, config_setting, font_config_xml, **kwargs):
        super().__init__(parent, config_setting, font_config_xml, **kwargs)

        # Create and assign the value display object
        self.create_value_display_object()

        # Set 'on_change_widget' to the color button for event handler binding
        self.on_change_widget = self.color_button
        self.on_change_event = "<<ColorChanged>>"  # Custom event identifier

        # Initialize specific event handlers
        self.bind_on_change_event()
        self._initialize_event_handlers()

    def create_value_display_object(self):
        """Create and assign the value display widget."""
        # Parse the color value from XML
        self.color_value = self.parse_color(self.default_value)

        # StringVar to hold the current color value
        self.color_var = tk.StringVar(value=self.value)

        # Button to display and select color
        self.color_button = tk.Button(self, text=self.color_var.get(), bg=self.rgb_to_hex(self.color_value), command=self.choose_color, width=22)
        self.color_button.grid(row=0, column=1, padx=0)
        self.value_display_object = self.color_var

    def bind_on_change_event(self):
        """Bind value change events to the specific widget."""
        if self.on_change_widget and self.on_change_event:
            self.on_change_widget.bind(self.on_change_event, self.default_on_change_handler)

    @property
    def value(self):
        return ','.join(map(str, self.color_value))

    @value.setter
    def value(self, new_value):
        self.color_value = self.parse_color(new_value)
        if self.value_display_object:
            self.value_display_object.set(self.value)
        self.color_button.config(bg=self.rgb_to_hex(self.color_value), text=self.color_var.get())

    def parse_color(self, color_string):
        """Parse the color string to a tuple of integers (R, G, B, A)."""
        return tuple(map(int, color_string.split(',')))

    def rgb_to_hex(self, rgba):
        """Convert an RGBA tuple to a hex color code (ignoring alpha)."""
        return "#%02x%02x%02x" % (rgba[0], rgba[1], rgba[2])

    def choose_color(self):
        """Open a color chooser dialog to select a new color."""
        initial_color = self.color_value
        palette_control = self.parent.controls.get("palette")
        palette_name = palette_control.value if palette_control else None

        # Open the color chooser
        rgb_color, hex_color = AgonColorPicker.askcolor(color=self.rgb_to_hex(self.color_value), parent=self, palette_name=palette_name)
        
        if rgb_color:
            self.color_value = (int(rgb_color[0]), int(rgb_color[1]), int(rgb_color[2]), self.color_value[3])
            self.color_var.set(self.value)  # Update the StringVar
            self.color_button.config(bg=self.rgb_to_hex(self.color_value), text=self.color_var.get())
            self.value = self.value  # Explicitly trigger the setter to ensure all UI elements are updated

            # Trigger on_change event if color has changed
            if self.color_value != initial_color:
                self.on_change_widget.event_generate(self.on_change_event)
