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

class DeltaControl(tk.Frame):
    """A flexible widget for handling delta adjustments with custom increment, bounds, and callbacks."""

    def __init__(self, parent, label, initial_value=0, min_value=float('-inf'), max_value=float('inf'),
                 step=1, data_type=int, precision=2, callback=None, default_value=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.data_type = data_type  # int or float
        self.precision = precision  # Decimal places for float display
        self.callback = callback  # Callback function to notify on value change
        self.step = step  # Default step size
        self.min_value = min_value
        self.max_value = max_value
        self.value = initial_value  # Initialize current value
        self.default_value = default_value if default_value is not None else initial_value  # Store default value

        # Label for the control
        self.label = tk.Label(self, text=label)
        self.label.grid(row=0, column=0, padx=(0, 5))

        # Entry for displaying the current value with validation
        self.var = tk.StringVar(value=self.format_value(self.value))
        self.entry = tk.Entry(self, textvariable=self.var, width=8, justify='center')
        self.entry.grid(row=0, column=1)
        self.entry.bind('<Return>', self.validate_entry)  # Update value on Enter

        # Increment and decrement buttons
        self.decrement_button = tk.Button(self, text='-', width=2, command=lambda: self.modify_value(-self.step))
        self.decrement_button.grid(row=0, column=2, padx=2)

        self.increment_button = tk.Button(self, text='+', width=2, command=lambda: self.modify_value(self.step))
        self.increment_button.grid(row=0, column=3, padx=2)

        # Reset button to restore the default value
        self.reset_button = tk.Button(self, text='Reset', width=5, command=self.reset_to_default)
        self.reset_button.grid(row=0, column=4, padx=(10, 0))

        # Bind for step multipliers with Shift, Ctrl, and Alt keys
        self.bind_all("<Shift-Up>", lambda e: self.modify_value(self.step * 10))
        self.bind_all("<Shift-Down>", lambda e: self.modify_value(-self.step * 10))
        self.bind_all("<Control-Up>", lambda e: self.modify_value(self.step * 5))
        self.bind_all("<Control-Down>", lambda e: self.modify_value(-self.step * 5))
        self.bind_all("<Alt-Up>", lambda e: self.modify_value(self.step * 2))
        self.bind_all("<Alt-Down>", lambda e: self.modify_value(-self.step * 2))

    def format_value(self, value):
        """Format the value according to the data type and precision."""
        return f"{value:.{self.precision}f}" if self.data_type == float else str(value)

    def modify_value(self, delta):
        """Modify the current value by a delta, respecting bounds."""
        new_value = self.value + delta
        self.set_value(new_value)

    def set_value(self, new_value):
        """Set the current value, enforce bounds, and update the display."""
        # Ensure the value is within bounds and of the correct data type
        new_value = max(self.min_value, min(self.max_value, new_value))
        self.value = self.data_type(new_value)

        # Update display
        self.var.set(self.format_value(self.value))
        
        # Trigger the callback if provided
        if self.callback:
            self.callback(self.value)

    def reset_to_default(self):
        """Reset the value to the default."""
        self.set_value(self.default_value)

    def validate_entry(self, event=None):
        """Validate the entry and update the value if valid."""
        try:
            # Parse the entered value according to the data type
            new_value = self.data_type(self.var.get())
            self.set_value(new_value)
        except ValueError:
            # Revert to the current valid value if entry is invalid
            self.var.set(self.format_value(self.value))
            messagebox.showerror("Invalid Input", f"Please enter a valid {self.data_type.__name__}.")

    def get_value(self):
        """Get the current value."""
        return self.value

    def set_callback(self, callback):
        """Set the callback function."""
        self.callback = callback