import tkinter as tk

class FontConfigEditor(tk.Frame):
    """A widget for editing font configurations with optional pre-filled values."""
    
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
        
        # Initialize layout
        self.create_widgets()

        # Load provided config dictionary, if any
        if config_dict:
            self.set_config(config_dict)

        # Configure the close button to trigger the cancel action
        parent.protocol("WM_DELETE_WINDOW", self.cancel)
        self.result = None  # Store the result for retrieval after closing

    def create_widgets(self):
        """Create form entries for each configuration parameter."""
        row = 0
        for param, var in self.config_params.items():
            label = tk.Label(self, text=param.replace('_', ' ').title())
            label.grid(row=row, column=0, sticky="e", padx=5, pady=5)
            entry = tk.Entry(self, textvariable=var)
            entry.grid(row=row, column=1, sticky="w", padx=5, pady=5)
            row += 1

        # "Set" and "Cancel" buttons
        self.set_button = tk.Button(self, text="Set", command=self.set)
        self.set_button.grid(row=row, column=0, pady=10)

        self.cancel_button = tk.Button(self, text="Cancel", command=self.cancel)
        self.cancel_button.grid(row=row, column=1, pady=10)

    def set_config(self, config_dict):
        """Populate the editor with values from the provided configuration dictionary."""
        for param, value in config_dict.items():
            if param in self.config_params:
                try:
                    self.config_params[param].set(value)
                except (ValueError, tk.TclError):
                    print(f"Warning: Could not set {param} to {value}. Check data types.")

    def get_config(self):
        """Retrieve the current configuration as a dictionary."""
        return {param: var.get() for param, var in self.config_params.items()}

    def set(self):
        """Store the current configuration as result."""
        self.result = self.get_config()

    def cancel(self):
        """Cancel editing and set result to None."""
        self.result = None
