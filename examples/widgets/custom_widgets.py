
import tkinter as tk
from tkinter import ttk
from tkinter import font

class ZoomControl(tk.Frame):
    """A compact widget to control zoom levels with buttons and a dropdown."""
    
    def __init__(self, parent, zoom_levels, current_zoom_index, on_zoom_change, **kwargs):
        super().__init__(parent, **kwargs)
        self.zoom_levels = zoom_levels  # List of available zoom levels
        self.on_zoom_change = on_zoom_change  # Callback for zoom change events
        self.current_zoom_index = current_zoom_index  # Default zoom level index

        # Zoom out button
        self.zoom_out_button = tk.Button(self, text="-", command=self.zoom_out, width=2)
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

class ConfigTextBox(tk.Frame):
    """A widget for displaying and editing a text-based configuration value."""

    def __init__(self, parent, label_text, default_value, **kwargs):
        super().__init__(parent, **kwargs)

        self.pad_x = 0  # Padding for grid layout

        # Main label for the control
        self.label = tk.Label(self, width=15, text=label_text, font=("Helvetica", 10), anchor="w")
        self.label.grid(row=0, column=0, padx=self.pad_x)

        self.text_var = tk.StringVar(value=default_value)
        self.text_entry = tk.Entry(self, textvariable=self.text_var, width=22)
        self.text_entry.grid(row=0, column=1, padx=self.pad_x)

    def get_value(self):
        """Return the current value of the text entry."""
        return self.text_var.get()

    def set_value(self, value):
        """Set the value of the text entry."""
        self.text_var.set(value)

    def clear(self):
        """Clear the text entry."""
        self.text_var.set("")

class ConfigComboBox(tk.Frame):
    """A widget for displaying and selecting from a dropdown list of configuration values."""

    def __init__(self, parent, label_text, options, default_value, **kwargs):
        super().__init__(parent, **kwargs)

        self.pad_x = 0  # Padding for grid layout

        # Main label for the control
        self.label = tk.Label(self, width=15, text=label_text, font=("Helvetica", 10), anchor="w")
        self.label.grid(row=0, column=0, padx=self.pad_x)

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

    def clear(self):
        """Clear the selected value in the combobox."""
        self.selected_var.set("")

class DeltaControl(tk.Frame):
    """A widget for handling delta_value adjustments with custom increment, bounds, and data-driven properties."""

    def __init__(self, parent, label_text, data_type, default_value, min_value, max_value, step_value, **kwargs):
        super().__init__(parent, **kwargs)

        self.data_type = data_type
        self.current_value = default_value
        self.min_value = min_value
        self.max_value = max_value
        self.step_value = step_value

        self.pad_x = 0  # Padding for grid layout

        # Main label for the control
        self.label = tk.Label(self, width=15, text=label_text, font=("Helvetica", 10), anchor="w")
        self.label.grid(row=0, column=0, padx=self.pad_x)

        # Current value display
        self.current_var = tk.StringVar(value=str(self.current_value))
        self.current_display = tk.Label(self, textvariable=self.current_var, width=4, anchor="center")
        self.current_display.grid(row=0, column=1, padx=self.pad_x)

        # Decrement button
        self.decrement_button = tk.Button(self, text="-", width=0, font=("Helvetica",8), command=lambda: self.modify_delta(-self.step_value))
        self.decrement_button.grid(row=0, column=2, padx=self.pad_x)

        # delta_value display
        self.delta_var = tk.StringVar(value="0")
        self.delta_display = tk.Label(self, textvariable=self.delta_var, width=4, anchor="center")
        self.delta_display.grid(row=0, column=3, padx=self.pad_x)

        # Increment button
        self.increment_button = tk.Button(self, text="+", width=0, font=("Helvetica",8), command=lambda: self.modify_delta(self.step_value))
        self.increment_button.grid(row=0, column=4, padx=self.pad_x)

        # Computed value display
        self.modified_var = tk.StringVar(value=str(self.current_value))
        self.modified_display = tk.Label(self, textvariable=self.modified_var, width=4, anchor="center")
        self.modified_display.grid(row=0, column=5, padx=self.pad_x)

    def modify_delta(self, delta_value):
        """Modify the delta, updating the modified value while keeping within constraints and calculating delta from current value."""
        # Convert modified_var to a numeric type for calculation
        current_modified = float(self.modified_var.get()) if self.data_type == 'float' else int(self.modified_var.get())
        # Calculate new delta by adding delta_value to the current delta
        new_delta = current_modified - self.current_value + delta_value
        # Clamp modified value within min and max constraints
        modified_value = max(self.min_value, min(self.max_value, self.current_value + new_delta))
        # Update the modified and delta displays
        self.modified_var.set(str(modified_value))
        self.delta_var.set(str(modified_value - self.current_value))  # Reflect adjusted delta

    def set_default_value(self, value):
        """Set the current (original) value, update displays, and reset delta to zero."""
        self.current_value = value  # Set the original/current value
        self.modified_var.set(str(self.current_value))  # Reset modified value to match
        self.current_var.set(str(self.current_value))  # Update the current display
        self.delta_var.set("0")  # Reset delta since modified equals current
