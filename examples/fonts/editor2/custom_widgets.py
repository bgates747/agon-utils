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
        
        # Store callback as an instance attribute, not as a Tkinter option
        self.callback = callback  

        # Retrieve configuration values from the dictionary
        label_text = config.get("label", {}).get("text")
        label_width = config.get("label", {}).get("width")
        label_anchor = config.get("label", {}).get("anchor")

        # Use get_data_type to interpret the data_type string from config
        self.data_type = self.get_data_type(config.get("value", {}).get("data_type"))
        self.precision = int(config.get("value", {}).get("precision", 2))
        self.step = float(config.get("value", {}).get("step", 1))
        self.min_value = float(config.get("value", {}).get("min", float('-inf')))
        self.max_value = float(config.get("value", {}).get("max", float('inf')))
        self.value = float(config.get("value", {}).get("initial", 0))
        self.default_value = float(config.get("value", {}).get("default", self.value))

        # Parse font settings for buttons
        button_font = config.get("button", {}).get("font", "Helvetica,8").split(",")
        button_font = (button_font[0], int(button_font[1])) if len(button_font) == 2 else ("Helvetica", 8)
        button_width = int(config.get("button", {}).get("width", 3))

        # Label for the control description
        self.label = tk.Label(self, text=label_text, width=int(label_width), anchor=label_anchor)
        self.label.grid(row=0, column=0, padx=(0, 5))

        # Label for displaying the current value (instead of entry)
        self.var = tk.StringVar(value=self.format_value(self.value))
        value_display_width = int(config.get("display", {}).get("value_display", {}).get("width", 10))
        value_display_anchor = config.get("display", {}).get("value_display", {}).get("anchor", "center")
        self.value_display = tk.Label(self, textvariable=self.var, width=value_display_width, anchor=value_display_anchor)
        self.value_display.grid(row=0, column=1)

        # Decrement button with smaller font
        decrement_text = config.get("button", {}).get("text_decrement", "-")
        self.decrement_button = tk.Button(self, text=decrement_text, width=button_width, font=button_font,
                                          command=lambda: self.modify_value(-self.step))
        self.decrement_button.grid(row=0, column=2, padx=2)

        # Delta display label between the decrement and increment buttons
        delta_display_width = int(config.get("display", {}).get("delta_display", {}).get("width", 10))
        delta_display_anchor = config.get("display", {}).get("delta_display", {}).get("anchor", "center")
        self.delta_display = tk.Label(self, text=self.calculate_delta_display(), width=delta_display_width, anchor=delta_display_anchor)
        self.delta_display.grid(row=0, column=3, padx=2)

        # Increment button with smaller font
        increment_text = config.get("button", {}).get("text_increment", "+")
        self.increment_button = tk.Button(self, text=increment_text, width=button_width, font=button_font,
                                          command=lambda: self.modify_value(self.step))
        self.increment_button.grid(row=0, column=4, padx=2)

        # Label for the net (current) value right of delta controls
        net_display_width = int(config.get("display", {}).get("net_display", {}).get("width", 10))
        net_display_anchor = config.get("display", {}).get("net_display", {}).get("anchor", "center")
        self.net_display = tk.Label(self, text=self.calculate_net_display(), width=net_display_width, anchor=net_display_anchor)
        self.net_display.grid(row=0, column=5, padx=(10, 0))

    def get_data_type(self, type_str):
        """Return the correct data type based on a string (int or float)."""
        return int if type_str == "int" else float

    def format_value(self, value):
        """Format the value according to the data type and precision."""
        return f"{value:.{self.precision}f}" if self.data_type == float else str(int(value))

    def calculate_delta_display(self):
        """Calculate and format the delta value (current - original)."""
        delta_value = self.value - self.default_value
        return f"{self.format_value(delta_value)}"

    def calculate_net_display(self):
        """Calculate and format the net display (original value + delta)."""
        return f"{self.format_value(self.value)}"

    def modify_value(self, delta):
        """Modify the current value by a delta, respecting bounds."""
        new_value = self.value + delta
        self.set_value(new_value)

    def set_value(self, new_value):
        """Set the current value, enforce bounds, and update displays."""
        new_value = max(self.min_value, min(self.max_value, new_value))
        self.value = self.data_type(new_value)
        self.var.set(self.format_value(self.value))
        self.delta_display.config(text=self.calculate_delta_display())
        self.net_display.config(text=self.calculate_net_display())
        
        # Trigger the callback if provided
        if self.callback:
            self.callback(self.value)

    def reset_to_default(self):
        """Reset the value to the default."""
        self.set_value(self.default_value)

    def get_value(self):
        """Get the current value."""
        return self.value

    def set_callback(self, callback):
        """Set the callback function."""
        self.callback = callback



if __name__ == "__main__":
    root = tk.Tk()
    root.title("Custom Widgets Example")

    def on_zoom_change(index):
        print(f"Zoom level changed to: {index}")

    def on_grid_toggle(state):
        print(f"Grid toggled to: {'ON' if state else 'OFF'}")

    def on_delta_change(value):
        print(f"Delta value changed to: {value}")

    zoom_control = ZoomControl(root, zoom_levels=[50, 75, 100, 125, 150], current_zoom_index=2, on_zoom_change=on_zoom_change)
    zoom_control.pack(pady=10)

    grid_toggle_button = GridToggleButton(root, on_toggle=on_grid_toggle)
    grid_toggle_button.pack(pady=10)

    console_display = ConsoleDisplay(root)
    console_display.pack(pady=10)
    console_display.append_message("Console initialized.")

    delta_config = {
        "label": {"text": "Delta Control", "width": 15, "anchor": "w"},
        "value": {"data_type": "float", "precision": 2, "step": 0.1, "min": 0.0, "max": 10.0, "initial": 5.0, "default": 5.0},
        "button": {"text_decrement": "-", "text_increment": "+", "width": 3, "font": "Helvetica,8"},
        "display": {
            "value_display": {"width": 10, "anchor": "e"},
            "delta_display": {"width": 10, "anchor": "e"},
            "net_display": {"width": 10, "anchor": "e"}
        }
    }
    delta_control = DeltaControl(root, config=delta_config)
    delta_control.set_callback(on_delta_change)
    delta_control.pack(pady=10)

    root.mainloop()
