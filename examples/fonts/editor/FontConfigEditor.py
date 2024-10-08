import tkinter as tk
from tkinter import filedialog, messagebox
import configparser
import os

class FontConfigEditor(tk.Frame):
    """A widget for editing and saving font configurations in .ini files."""
    
    def __init__(self, parent, config_file=None, **kwargs):
        super().__init__(parent, **kwargs)
        
        # Configuration parameters
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

        # Initialize the layout
        self.create_widgets()

        # Load config from file if provided
        if config_file and os.path.exists(config_file):
            self.load_config(config_file)

    def create_widgets(self):
        """Create form entries for each configuration parameter."""
        row = 0
        for param, var in self.config_params.items():
            label = tk.Label(self, text=param.replace('_', ' ').title())
            label.grid(row=row, column=0, sticky="e", padx=5, pady=5)
            entry = tk.Entry(self, textvariable=var)
            entry.grid(row=row, column=1, sticky="w", padx=5, pady=5)
            row += 1

        # Save and Load buttons
        self.load_button = tk.Button(self, text="Load Config", command=self.load_config_dialog)
        self.load_button.grid(row=row, column=0, pady=10)

        self.save_button = tk.Button(self, text="Save Config", command=self.save_config_dialog)
        self.save_button.grid(row=row, column=1, pady=10)

    def load_config(self, config_file):
        """Load font configuration from an .ini file."""
        config = configparser.ConfigParser()
        config.read(config_file)

        # Update entry fields with values from the config file
        if 'font' in config:
            font_config = config['font']
            for param, var in self.config_params.items():
                value = font_config.get(param)
                if value is not None:
                    # Set variable type accordingly
                    if isinstance(var, tk.IntVar):
                        try:
                            var.set(int(value))
                        except ValueError:
                            messagebox.showerror("Invalid Value", f"{param} should be an integer.")
                    else:
                        var.set(value)
        else:
            messagebox.showerror("Invalid Config", "No [font] section found in the file.")

    def save_config(self, config_file):
        """Save font configuration to an .ini file."""
        config = configparser.ConfigParser()
        config['font'] = {param: str(var.get()) for param, var in self.config_params.items()}

        with open(config_file, 'w') as file:
            config.write(file)

    def load_config_dialog(self):
        """Open a dialog to select a configuration file to load."""
        config_file = filedialog.askopenfilename(
            title="Select Config File",
            filetypes=(("INI files", "*.ini"), ("All files", "*.*"))
        )
        if config_file:
            self.load_config(config_file)

    def save_config_dialog(self):
        """Open a dialog to select a location to save the configuration file."""
        config_file = filedialog.asksaveasfilename(
            title="Save Config File",
            defaultextension=".ini",
            filetypes=(("INI files", "*.ini"), ("All files", "*.*"))
        )
        if config_file:
            self.save_config(config_file)

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
