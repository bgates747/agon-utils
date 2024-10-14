
import tkinter as tk

class DeltaControl(tk.Frame):
    """A widget for handling delta_value adjustments with custom increment, bounds, and data-driven properties."""

    def __init__(self, parent, label_text, data_type, default_value, min_value, max_value, step_value, **kwargs):
        super().__init__(parent, **kwargs)

        self.data_type = data_type
        self.current_value = default_value
        self.min_value = min_value
        self.max_value = max_value
        self.step_value = step_value

        # Main label for the control
        self.label = tk.Label(self, width=15, text=label_text, font=("Helvetica", 10))
        self.label.grid(row=0, column=0, padx=5)

        # Current value display
        self.current_var = tk.StringVar(value=str(self.current_value))
        self.current_display = tk.Label(self, textvariable=self.current_var, width=4, anchor="center")
        self.current_display.grid(row=0, column=1, padx=5)

        # Decrement button
        self.decrement_button = tk.Button(self, text="-", width=0, font=("Helvetica",8), command=lambda: self.modify_delta(-self.step_value))
        self.decrement_button.grid(row=0, column=2, padx=5)

        # delta_value display
        self.delta_var = tk.StringVar(value="0")
        self.delta_display = tk.Label(self, textvariable=self.delta_var, width=4, anchor="center")
        self.delta_display.grid(row=0, column=3, padx=5)

        # Increment button
        self.increment_button = tk.Button(self, text="+", width=0, font=("Helvetica",8), command=lambda: self.modify_delta(self.step_value))
        self.increment_button.grid(row=0, column=4, padx=5)

        # Computed value display
        self.modified_var = tk.StringVar(value=str(self.current_value))
        self.modified_display = tk.Label(self, textvariable=self.modified_var, width=4, anchor="center")
        self.modified_display.grid(row=0, column=5, padx=5)

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
