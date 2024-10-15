
import tkinter as tk
from tkinter import ttk

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
