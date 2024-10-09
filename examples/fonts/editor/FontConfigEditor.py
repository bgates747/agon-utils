import tkinter as tk

class FontConfigEditor(tk.Frame):
    """A widget for viewing and editing font configurations, with numeric adjustment controls and apply functionality."""

    def __init__(self, parent, config_dict=None, **kwargs):
        super().__init__(parent, **kwargs)

        # Configuration parameters with Tkinter variable types for easy binding to Entry widgets
        self.config_params = {
            'font_name': tk.StringVar(),
            'font_variant': tk.StringVar(),
            'font_width': tk.IntVar(),
            'font_height': tk.IntVar(),
            'offset_left': tk.IntVar(),
            'offset_top': tk.IntVar(),
            'offset_width': tk.IntVar(),
            'offset_height': tk.IntVar(),
            'ascii_range_start': tk.IntVar(),
            'ascii_range_end': tk.IntVar()
        }

        # Initialize original and current config dictionaries
        self.orig_config = config_dict.copy() if config_dict else {}
        self.curr_config = config_dict.copy() if config_dict else {}

        # Initialize layout
        self.create_widgets()

        # Load provided config dictionary, if any
        if config_dict:
            self.set_config(config_dict)

    def create_widgets(self):
        """Create form entries for each configuration parameter."""
        row = 0
        for param, var in self.config_params.items():
            label = tk.Label(self, text=param.replace('_', ' ').title())
            label.grid(row=row, column=0, sticky="e", padx=5, pady=0)

            if isinstance(var, tk.IntVar):  # Numeric fields with adjustment controls
                self.create_numeric_controls(row, param, var)
            else:  # Standard entry for text fields
                entry = tk.Entry(self, textvariable=var)
                entry.grid(row=row, column=1, columnspan=3, sticky="w", padx=5, pady=0)
                var.trace("w", self.check_apply_needed)  # Trace for enabling Apply Changes button

            row += 1

        # Apply Changes button at the bottom, initially disabled
        self.apply_button = tk.Button(self, text="Apply Changes", state=tk.DISABLED, command=self.apply_changes)
        self.apply_button.grid(row=row, column=0, columnspan=5, pady=10)

    def create_numeric_controls(self, row, param, var):
        """Creates a three-column layout with Original, Delta, and New values, and +/- controls."""
        # Original value display
        orig_value = self.orig_config.get(param, 0)
        orig_label = tk.Label(self, text=str(orig_value))  # Show original value
        orig_label.grid(row=row, column=1, padx=5)

        # Change (delta) display and +/- buttons
        delta_var = tk.IntVar(value=0)
        minus_button = tk.Button(self, text="-", command=lambda v=var, d=delta_var: self.update_new_value(v, d, -1))
        minus_button.grid(row=row, column=2, sticky="e", padx=2)
        
        delta_label = tk.Label(self, textvariable=delta_var)
        delta_label.grid(row=row, column=3)

        plus_button = tk.Button(self, text="+", command=lambda v=var, d=delta_var: self.update_new_value(v, d, 1))
        plus_button.grid(row=row, column=4, sticky="w", padx=2)

        # New value entry
        new_var = tk.IntVar(value=orig_value)  # Initially set to original value
        new_entry = tk.Entry(self, textvariable=new_var, width=5)
        new_entry.grid(row=row, column=5, padx=5)

        # Link new_var to update delta and check if Apply Changes button is needed
        new_var.trace("w", lambda *args, o=orig_value, n=new_var, d=delta_var: self.update_delta(o, n, d, param))

    def update_new_value(self, new_var, delta_var, increment):
        """Update the new value by increment/decrement and adjust delta accordingly."""
        new_value = new_var.get() + increment
        new_var.set(new_value)  # Update new value
        self.check_apply_needed()  # Check if Apply Changes should be enabled

    def update_delta(self, orig_value, new_var, delta_var, param):
        """Update delta value when new value changes and check if Apply Changes is needed."""
        try:
            new_value = int(new_var.get())
            delta_var.set(new_value - orig_value)  # Set delta to difference between new and original
            self.curr_config[param] = new_value  # Update current configuration
            self.check_apply_needed()  # Enable Apply if there are changes
        except ValueError:
            pass  # Ignore if new_var is not a valid integer

    def set_config(self, config_dict):
        """Populate the editor with values from the provided configuration dictionary."""
        self.orig_config = config_dict.copy()
        self.curr_config = config_dict.copy()
        for param, value in config_dict.items():
            if param in self.config_params:
                try:
                    self.config_params[param].set(value)
                except (ValueError, tk.TclError):
                    print(f"Warning: Could not set {param} to {value}. Check data types.")

    def get_config(self):
        """Retrieve the current configuration as a dictionary."""
        return {param: var.get() for param, var in self.config_params.items()}

    def check_apply_needed(self):
        """Check if Apply Changes button should be enabled based on unsaved changes."""
        changes_exist = any(self.orig_config.get(param) != var.get() for param, var in self.config_params.items())
        self.apply_button.config(state=tk.NORMAL if changes_exist else tk.DISABLED)

    def apply_changes(self):
        """Apply changes by updating original config to match current config."""
        for param, var in self.config_params.items():
            self.orig_config[param] = var.get()  # Update orig_config with the new values
        self.check_apply_needed()  # Update button state after applying changes
