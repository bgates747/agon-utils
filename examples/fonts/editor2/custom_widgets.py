import tkinter as tk
from tkinter import font, messagebox

class ZoomControl(tk.Frame):
    """A compact widget to control zoom levels with buttons and a dropdown."""
    
    def __init__(self, parent, zoom_levels, current_zoom_index, on_zoom_change, **kwargs):
        super().__init__(parent, **kwargs)
        self.zoom_levels = zoom_levels  # List of available zoom levels
        self.on_zoom_change = on_zoom_change  # Callback for zoom change events
        self.current_zoom_index = current_zoom_index  # Default zoom level index

        # Zoom out button
        self.zoom_out_button = tk.Button(self, text="–", command=self.zoom_out, width=2)
        self.zoom_out_button.pack(side=tk.LEFT, padx=2)

        # Dropdown for selecting zoom levels
        self.zoom_var = tk.StringVar(value=f"{zoom_levels[current_zoom_index]}%")
        self.zoom_dropdown = tk.OptionMenu(
            self, self.zoom_var, *[f"{level}%" for level in zoom_levels], command=self._on_dropdown_change
        )
        self.zoom_dropdown.config(width=6)
        self.zoom_dropdown.pack(side=tk.LEFT, padx=2)

        # Zoom in button
        self.zoom_in_button = tk.Button(self, text="+", command=self.zoom_in, width=2)
        self.zoom_in_button.pack(side=tk.LEFT, padx=2)

    def _on_dropdown_change(self, selected_value):
        """Handle dropdown changes by updating the zoom level."""
        new_zoom_level = int(selected_value.strip('%'))
        self.current_zoom_index = self.zoom_levels.index(new_zoom_level)
        self.on_zoom_change(self.current_zoom_index)  # Trigger zoom change callback

    def zoom_in(self):
        """Increase the zoom level if possible."""
        if self.current_zoom_index < len(self.zoom_levels) - 1:
            self.current_zoom_index += 1
            self.update_zoom()

    def zoom_out(self):
        """Decrease the zoom level if possible."""
        if self.current_zoom_index > 0:
            self.current_zoom_index -= 1
            self.update_zoom()

    def update_zoom(self):
        """Update the zoom level display and invoke the callback."""
        new_zoom_level = self.zoom_levels[self.current_zoom_index]
        self.zoom_var.set(f"{new_zoom_level}%")  # Update dropdown display
        self.on_zoom_change(self.current_zoom_index)  # Trigger zoom level change callback

class GridToggleButton(tk.Button):
    """A custom toggle button to control grid display, toggling between bold and regular text."""
    
    def __init__(self, parent, on_toggle, **kwargs):
        super().__init__(parent, text="#", command=self.toggle, **kwargs)
        self.on_toggle = on_toggle  # Callback to notify parent of toggle state
        self.grid_on = False  # Initial state of the grid display

        # Configure fonts for the regular and bold states
        self.regular_font = font.nametofont("TkDefaultFont")
        self.bold_font = self.regular_font.copy()
        self.bold_font.configure(weight="bold")

        # Initialize with regular font
        self.config(font=self.regular_font)

    def toggle(self):
        """Toggle the grid state and update the button's appearance."""
        self.grid_on = not self.grid_on  # Toggle the state
        self.config(font=self.bold_font if self.grid_on else self.regular_font)
        self.on_toggle(self.grid_on)  # Notify the parent widget of the new state

class ConsoleDisplay(tk.Frame):
    """A console-like text display widget with a method to append messages."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        # Create a frame to hold the text display and scrollbar
        text_frame = tk.Frame(self)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Initialize text widget for console output
        self.text_display = tk.Text(text_frame, wrap='word', height=5, width=70, state='disabled', bg='black', fg='white')
        self.text_display.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Add scrollbar within the text_frame, aligned to the right
        self.scrollbar = tk.Scrollbar(text_frame, command=self.text_display.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_display.config(yscrollcommand=self.scrollbar.set)

    def append_message(self, message):
        """Append a new message to the console display."""
        self.text_display.config(state='normal')  # Enable editing
        self.text_display.insert(tk.END, message + "\n")  # Add the message
        self.text_display.config(state='disabled')  # Disable editing
        self.text_display.see(tk.END)  # Scroll to the end

class DeltaControl(tk.Frame):
    """A flexible widget for handling delta adjustments with custom increment, bounds, and callbacks."""

    def __init__(self, parent, config, callback=None, **kwargs):
        super().__init__(parent, **kwargs)
        
        # Store callback as an instance attribute
        self.callback = callback

        # Initialize values from XML config
        self.data_type = self.get_data_type(config.get("value", {}).get("data_type"))
        self.precision = int(config.get("value", {}).get("precision", 0))
        self.step = float(config.get("value", {}).get("step", 1))
        self.min_value = float(config.get("value", {}).get("min", float('-Inf')))
        self.max_value = float(config.get("value", {}).get("max", float('inf')))
        
        # Store initial and default values, set delta to 0
        self.initial_value = float(config.get("value", {}).get("initial", 0))
        self.default_value = float(config.get("value", {}).get("default", 0))
        self.delta = 0
        self.computed_value = self.initial_value

        # Button configuration
        button_config = config.get("button", {})
        button_font = button_config.get("font", "Helvetica,8").split(",")
        button_font = (button_font[0], int(button_font[1])) if len(button_font) == 2 else ("Helvetica", 8)
        button_width = int(button_config.get("width", 3))

        # Display configurations
        display_config = config.get("display", {})
        value_display_config = display_config.get("value_display", {})
        delta_display_config = display_config.get("delta_display", {})
        net_display_config = display_config.get("net_display", {})

        # Original value display
        self.var_original = tk.StringVar(value=self.format_value(self.initial_value))
        self.original_display = tk.Label(self, textvariable=self.var_original,
                                         width=int(value_display_config.get("width", 4)),
                                         anchor=value_display_config.get("anchor", "center"))
        self.original_display.grid(row=0, column=0)

        # Decrement button
        decrement_text = button_config.get("text_decrement", "-")
        self.decrement_button = tk.Button(self, text=decrement_text, width=button_width, font=button_font,
                                          command=lambda: self.modify_delta(-self.step))
        self.decrement_button.grid(row=0, column=1, padx=2)

        # Delta display
        self.var_delta = tk.StringVar(value=self.format_value(self.delta))
        self.delta_display = tk.Label(self, textvariable=self.var_delta,
                                      width=int(delta_display_config.get("width", 4)),
                                      anchor=delta_display_config.get("anchor", "center"))
        self.delta_display.grid(row=0, column=2, padx=2)

        # Increment button
        increment_text = button_config.get("text_increment", "+")
        self.increment_button = tk.Button(self, text=increment_text, width=button_width, font=button_font,
                                          command=lambda: self.modify_delta(self.step))
        self.increment_button.grid(row=0, column=3, padx=2)

        # Net (computed) display
        self.var_computed = tk.StringVar(value=self.format_value(self.computed_value))
        self.net_display = tk.Label(self, textvariable=self.var_computed,
                                    width=int(net_display_config.get("width", 4)),
                                    anchor=net_display_config.get("anchor", "center"))
        self.net_display.grid(row=0, column=4)

    def get_data_type(self, type_str):
        """Return the correct data type based on a string (int or float)."""
        return int if type_str == "int" else float

    def format_value(self, value):
        """Format the value according to the data type and precision."""
        return f"{value:.{self.precision}f}" if self.data_type == float else str(int(value))

    def modify_delta(self, delta):
        """Modify the delta, update the computed value, and refresh displays."""
        self.delta += delta
        self.computed_value = max(self.min_value, min(self.max_value, self.initial_value + self.delta))
        
        # Update the delta and computed value displays
        self.var_delta.set(self.format_value(self.delta))
        self.var_computed.set(self.format_value(self.computed_value))

    def get_computed_value(self):
        """Retrieve the current computed value."""
        return self.computed_value
