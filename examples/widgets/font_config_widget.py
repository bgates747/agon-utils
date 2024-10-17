import tkinter as tk
from tkinter import ttk
import xml.etree.ElementTree as ET
from config_manager import get_typed_data
from agon_color_picker import AgonColorPicker

class FontConfigWidget(tk.Frame):
    """Base widget class for common font configuration controls."""

    def __init__(self, parent, config_setting, config_xml, **kwargs):
        super().__init__(parent, **kwargs)

        self.parent = parent
        self.hidden = False  # Custom attribute to manage visibility state
        
        # Parse the XML configuration and filter for the specific setting
        self.setting_xml = config_xml.find(f".//setting[@name='{config_setting}']")
        self.id = config_setting

        # Extract common properties from the XML
        self.data_type = self.setting_xml.find('data_type').text
        self.default_value = get_typed_data(self.data_type, self.setting_xml.find('default_value').text)
        self.label_text = self.setting_xml.find('label_text').text
        self.visible = self._extract_nested_dict('visible')
        self.event_handlers = self._extract_nested_dict('event_handlers')
        self.options_dict = self._extract_nested_dict('options')
        self.description = self.setting_xml.find('description').text if self.setting_xml.find('description') is not None else ""

        # Create the control based on the specific widget type
        self.pad_x = 0
        self.label = tk.Label(self, width=15, text=self.label_text, font=("Helvetica", 10), anchor="w")
        self.label.grid(row=0, column=0, padx=self.pad_x)

        # Set the value objects for easier access to get/set methods
        self.value_object = None
        self.original_value_object = None

        # Initialize event handlers
        self.on_change_event = None  # Define on_change_event in the base class
        self.on_change_widget = None  # Define on_change_widget in the base class
        self._initialize_event_handlers()

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

    def get_value(self):
        """Return the current value of the control."""
        if self.value_object:
            return get_typed_data(self.data_type, self.value_object.get())
        return None

    def set_value(self, value):
        """Set the current value of the control."""
        value = get_typed_data(self.data_type, value)
        if self.value_object:
            self.value_object.set(value)

    def set_default_value(self):
        """Set the default value for the control."""
        self.set_value(self.default_value)

    def get_original_value(self):
        """Return the original value of the control."""
        if self.original_value_object:
            return get_typed_data(self.data_type, self.original_value_object.get())
        return None

    def set_original_value(self, value):
        """Set the original value of the control."""
        value = get_typed_data(self.data_type, value)
        if self.original_value_object:
            self.original_value_object.set(value)

    def _initialize_event_handlers(self):
        """Initialize event handlers for generic and specific events."""
        if self.on_change_widget:
            # Bind a default on_change event handler if no specific handler is defined
            if 'on_change' in self.event_handlers and self.on_change_event:
                self._bind_event_handler("on_change", "default_on_change_handler")

        # Bind the on_hover event handlers if present
        if 'on_hover' in self.event_handlers:
            self.label.bind("<Enter>", self.default_on_mouse_enter)
            self.label.bind("<Leave>", self.default_on_mouse_leave)

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

    def _initialize_specific_event_handlers(self):
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
        print(f"Default on_change handler called for {self.id} ({self.label_text}) with value: {self.get_value()}")
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

    # Custom on_change handlers
    def font_name_on_change_handler(self, event):
        """Custom on_change handler for the font_name setting."""
        print(f"Font name ({self.id}) changed to: {self.get_value()}")

    def font_variant_on_change_handler(self, event):
        """Custom on_change handler for the font_variant setting."""
        print(f"Font variant ({self.id}) changed to: {self.get_value()}")

    def point_size_on_change_handler(self, event):
        """Custom on_change handler for the point_size setting."""
        print(f"Point size ({self.id}) changed to: {self.get_value()}")

    def font_width_on_change_handler(self, event):
        """Custom on_change handler for the font_width setting."""
        print(f"Font width ({self.id}) changed to: {self.get_value()}")

    def font_height_on_change_handler(self, event):
        """Custom on_change handler for the font_height setting."""
        print(f"Font height ({self.id}) changed to: {self.get_value()}")

    def offset_left_on_change_handler(self, event):
        """Custom on_change handler for the offset_left setting."""
        print(f"Offset left ({self.id}) changed to: {self.get_value()}")

    def offset_top_on_change_handler(self, event):
        """Custom on_change handler for the offset_top setting."""
        print(f"Offset top ({self.id}) changed to: {self.get_value()}")

    def offset_width_on_change_handler(self, event):
        """Custom on_change handler for the offset_width setting."""
        print(f"Offset width ({self.id}) changed to: {self.get_value()}")

    def offset_height_on_change_handler(self, event):
        """Custom on_change handler for the offset_height setting."""
        print(f"Offset height ({self.id}) changed to: {self.get_value()}")

    def scale_width_on_change_handler(self, event):
        """Custom on_change handler for the scale_width setting."""
        print(f"Scale width ({self.id}) changed to: {self.get_value()}")

    def scale_height_on_change_handler(self, event):
        """Custom on_change handler for the scale_height setting."""
        print(f"Scale height ({self.id}) changed to: {self.get_value()}")

    def raster_type_on_change_handler(self, event):
        """Custom on_change handler for the raster_type setting."""
        print(f"Raster type ({self.id}) changed to: {self.get_value()}")

    def threshold_on_change_handler(self, event):
        """Custom on_change handler for the threshold setting."""
        print(f"Threshold ({self.id}) changed to: {self.get_value()}")

    def palette_on_change_handler(self, event):
        """Custom on_change handler for the palette setting."""
        print(f"Palette ({self.id}) changed to: {self.get_value()}")

    def fg_color_on_change_handler(self, event):
        """Custom on_change handler for the fg_color setting."""
        print(f"Foreground color ({self.id}) changed to: {self.get_value()}")

    def bg_color_on_change_handler(self, event):
        """Custom on_change handler for the bg_color setting."""
        print(f"Background color ({self.id}) changed to: {self.get_value()}")

    def ascii_start_on_change_handler(self, event):
        """Custom on_change handler for the ascii_start setting."""
        print(f"ASCII start ({self.id}) changed to: {self.get_value()}")

    def ascii_end_on_change_handler(self, event):
        """Custom on_change handler for the ascii_end setting."""
        print(f"ASCII end ({self.id}) changed to: {self.get_value()}")

    def chars_per_row_on_change_handler(self, event):
        """Custom on_change handler for the chars_per_row setting."""
        print(f"Characters per row ({self.id}) changed to: {self.get_value()}")

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

        # Set the value objects for easier access
        self.value_object = self.selected_var
        self.original_value_object = self.selected_var

        # Set 'on_change_widget' to the combobox for event handler binding
        self.on_change_widget = self.combobox
        self.on_change_event = "<<ComboboxSelected>>"

        # Initialize specific event handlers
        self._initialize_specific_event_handlers()

    def set_combo_options(self, options):
        """Set the available options for the ComboBox."""
        if isinstance(options, (list, dict)):
            self.combobox['values'] = list(options)

class FontConfigTextBox(FontConfigWidget):
    """A widget for displaying and editing a text-based configuration value."""

    def __init__(self, parent, config_setting, font_config_xml, **kwargs):
        super().__init__(parent, config_setting, font_config_xml, **kwargs)
        
        # Additional setup for Text Entry
        self.text_var = tk.StringVar(value=self.default_value)
        self.text_entry = tk.Entry(self, textvariable=self.text_var, width=22)
        self.text_entry.grid(row=0, column=1, padx=self.pad_x)

        # Set the value objects for easier access
        self.value_object = self.text_var
        self.original_value_object = self.text_var

        # Set 'on_change_widget' to the text entry for event handler binding
        self.on_change_widget = self.text_entry
        self.on_change_event = "<FocusOut>"  # Set the event type for text entry

        # Initialize specific event handlers
        self._initialize_specific_event_handlers()

        # Bind the Enter key to trigger focus out
        self.text_entry.bind("<Return>", self.trigger_focus_out)

    def trigger_focus_out(self, event=None):
        """Trigger a focus out event to activate the on_change event."""
        self.on_change_widget.event_generate("<FocusOut>")

class FontConfigDeltaControl(FontConfigWidget):
    """A widget for handling delta_value adjustments with custom increment, bounds, and data-driven properties."""

    def __init__(self, parent, config_setting, font_config_xml, **kwargs):
        super().__init__(parent, config_setting, font_config_xml, **kwargs)
        
        # Extract configuration from XML
        self.data_type = self.setting_xml.find('data_type').text
        self.default_value = get_typed_data(self.data_type, self.setting_xml.find('default_value').text)
        self.min_value = get_typed_data(self.data_type, self.setting_xml.find('min_value').text)
        self.max_value = get_typed_data(self.data_type, self.setting_xml.find('max_value').text)
        self.step_value = get_typed_data(self.data_type, self.setting_xml.find('step_value').text)

        # Initialize state variables
        self.current_value = self.default_value

        # Main label for the control
        self.label = tk.Label(self, width=15, text=self.label_text, font=("Helvetica", 10), anchor="w")
        self.label.grid(row=0, column=0, padx=self.pad_x)

        # Current value display
        self.current_var = tk.StringVar(value=str(self.current_value))
        self.current_display = tk.Label(self, textvariable=self.current_var, width=4, anchor="center")
        self.current_display.grid(row=0, column=1, padx=self.pad_x)

        # Decrement button
        self.decrement_button = tk.Button(self, text="-", width=0, font=("Helvetica", 8), command=lambda: self.modify_delta(-self.step_value))
        self.decrement_button.grid(row=0, column=2, padx=self.pad_x)

        # Delta display
        self.delta_var = tk.StringVar(value="0")
        self.delta_display = tk.Label(self, textvariable=self.delta_var, width=4, anchor="center")
        self.delta_display.grid(row=0, column=3, padx=self.pad_x)

        # Increment button
        self.increment_button = tk.Button(self, text="+", width=0, font=("Helvetica", 8), command=lambda: self.modify_delta(self.step_value))
        self.increment_button.grid(row=0, column=4, padx=self.pad_x)

        # Computed value display
        self.modified_var = tk.StringVar(value=str(self.current_value))
        self.modified_display = tk.Label(self, textvariable=self.modified_var, width=4, anchor="center")
        self.modified_display.grid(row=0, column=5, padx=self.pad_x)

        # Set value object and on_change_widget for tracking changes
        self.value_object = self.modified_var
        self.original_value_object = self.current_var
        self.on_change_widget = self.modified_display
        self.on_change_event = "<<ModifiedValueChanged>>"  # Custom event identifier

        # Initialize specific event handlers
        self._initialize_specific_event_handlers()

    def modify_delta(self, delta_value):
        """Modify the delta, updating the modified value within constraints and calculating delta from current value."""
        # Convert modified_var to a numeric type for calculation
        current_modified = float(self.modified_var.get()) if self.data_type == 'float' else int(self.modified_var.get())
        # Calculate new delta by adding delta_value to the current delta
        new_delta = current_modified - self.current_value + delta_value
        # Clamp modified value within min and max constraints
        modified_value = max(self.min_value, min(self.max_value, self.current_value + new_delta))
        
        # Update the modified and delta displays
        self.modified_var.set(str(modified_value))
        self.delta_var.set(str(modified_value - self.current_value))  # Reflect adjusted delta
        
        # Trigger the custom on_change event
        self.on_change_widget.event_generate(self.on_change_event)

    def set_default_value(self, value):
        """Set the current (original) value, update displays, and reset delta to zero."""
        self.current_value = value  # Set the original/current value
        self.modified_var.set(str(self.current_value))  # Reset modified value to match
        self.current_var.set(str(self.current_value))  # Update the current display
        self.delta_var.set("0")  # Reset delta since modified equals current

    def set_value(self, value):
        """Set the current (original) value, update displays, and reset delta to zero."""
        self.set_default_value(value)

class FontConfigColorPicker(FontConfigWidget):
    """A widget for displaying and selecting a color, showing the value as an RGBA tuple."""

    def __init__(self, parent, config_setting, font_config_xml, **kwargs):
        super().__init__(parent, config_setting, font_config_xml, **kwargs)

        # Parse the color value from the XML
        self.color_value = self.parse_color(self.default_value)

        # Button to display and select color
        self.color_button = tk.Button(self, text=str(self.color_value), bg=self.rgb_to_hex(self.color_value),
                                      command=self.choose_color, width=22)
        self.color_button.grid(row=0, column=1, padx=self.pad_x)

        # Set the value object for easier access
        self.value_object = self.color_button

        # Set 'on_change_widget' to the color button for event handler binding
        self.on_change_widget = self.color_button
        self.on_change_event = "<<ColorChanged>>"

        # Initialize specific event handlers
        self._initialize_specific_event_handlers()

    def parse_color(self, color_string):
        """Parse the color string to a tuple of integers (R, G, B, A)."""
        return tuple(map(int, color_string.split(',')))

    def rgb_to_hex(self, rgba):
        """Convert an RGBA tuple to a hex color code (ignoring alpha)."""
        return "#%02x%02x%02x" % (rgba[0], rgba[1], rgba[2])

    def get_value(self):
        """Return the current color value as a string."""
        return ','.join(map(str, self.color_value))

    def set_value(self, value):
        """Set the current color value."""
        self.color_value = self.parse_color(value)
        self.color_button.config(bg=self.rgb_to_hex(self.color_value), text=str(self.color_value))

    def choose_color(self):
        """Open a color chooser dialog to select a new color."""
        initial_color = self.color_value
        palette_control = self.parent.controls.get("palette")
        palette_name = palette_control.get_value() if palette_control else None

        # Open the color chooser
        rgb_color, hex_color = AgonColorPicker.askcolor(color=self.rgb_to_hex(self.color_value), parent=self, palette_name=palette_name)
        
        if rgb_color:
            self.color_value = (int(rgb_color[0]), int(rgb_color[1]), int(rgb_color[2]), self.color_value[3])
            self.color_button.config(bg=self.rgb_to_hex(self.color_value), text=str(self.color_value))

            if self.color_value != initial_color:
                self.on_change_widget.event_generate(self.on_change_event)