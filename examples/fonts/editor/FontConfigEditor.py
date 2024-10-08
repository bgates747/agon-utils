import tkinter as tk
from AgonFont import resample_image

class FontConfigEditor(tk.Frame):
    """A widget for viewing and editing font configurations, with numeric adjustment controls and apply functionality."""

    def __init__(self, parent, app_reference, default_font_config, **kwargs):
        super().__init__(parent, **kwargs)
        self.app_reference = app_reference
        # Initialize current config and modified config dictionary
        self.curr_config = default_font_config
        self.mod_config = self.curr_config.copy()

        # Tkinter variables for UI
        self.config_params = {
            param: (tk.StringVar() if isinstance(val, str) else tk.IntVar())
            for param, val in self.curr_config.items()
        }
        self.delta_vars = {
            param: tk.IntVar(value=0) for param, val in self.curr_config.items() if isinstance(val, int)
        }

        # Bind traces to update dictionaries when font_name or font_variant are modified
        self.config_params['font_name'].trace("w", self.update_string_params)
        self.config_params['font_variant'].trace("w", self.update_string_params)

        # Dictionary to hold references to numeric labels
        self.curr_labels = {}

        # Initialize layout
        self.create_widgets()

        # Set initial values in the editor
        self.update_config_display()

    def update_string_params(self, *args):
        """Handler to update font_name and font_variant in the configuration dictionaries."""
        self.curr_config['font_name'] = self.config_params['font_name'].get()
        self.curr_config['font_variant'] = self.config_params['font_variant'].get()
        self.mod_config['font_name'] = self.curr_config['font_name']
        self.mod_config['font_variant'] = self.curr_config['font_variant']
        # Enable the Apply button since there's a change
        self.update_apply_button_state()

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

            row += 1

        # Apply Changes button at the bottom, initially disabled
        self.apply_button = tk.Button(self, text="Apply Changes", state=tk.DISABLED, command=self.apply_changes)
        self.apply_button.grid(row=row, column=0, columnspan=5, pady=10)

    def create_numeric_controls(self, row, param, var):
        """Creates a three-column layout with current, Delta, and Mod labels, and +/- controls."""
        curr_value = self.curr_config.get(param, 0)

        # Current value display, store reference in curr_labels for later updating
        curr_label = tk.Label(self, text=str(curr_value))
        curr_label.grid(row=row, column=1, padx=5)
        self.curr_labels[param] = curr_label  # Store the label reference for numeric fields only

        # Change (delta) display and +/- buttons
        delta_var = self.delta_vars[param]
        minus_button = tk.Button(self, text="-", command=lambda p=param, d=-1: self.modify_value(p, d))
        minus_button.grid(row=row, column=2, sticky="e", padx=2)

        delta_label = tk.Label(self, textvariable=delta_var)
        delta_label.grid(row=row, column=3)

        plus_button = tk.Button(self, text="+", command=lambda p=param, d=1: self.modify_value(p, d))
        plus_button.grid(row=row, column=4, sticky="w", padx=2)

        # Modified value display
        mod_label = tk.Label(self, textvariable=var)
        mod_label.grid(row=row, column=5, padx=5)

    def modify_value(self, param, delta):
        """Adjust the modified value based on the delta and update displays."""
        # Apply delta to modified config value
        new_value = self.curr_config[param] + self.delta_vars[param].get() + delta
        self.mod_config[param] = new_value

        # Check if Apply Changes should be enabled
        changes_exist = self.update_apply_button_state()

        # Helper for setting up or destroying pre_resample_image based on changes
        if changes_exist:
            # If pre_resample_image doesn't exist, create a backup from working_image
            if self.app_reference.image_display.pre_resample_image is None:
                self.app_reference.image_display.pre_resample_image = self.app_reference.image_display.working_image.copy()

            # Resample the working image with current config and modified values
            self.resample_working_image()

        else:
            # If no changes and pre_resample_image exists, revert to pre_resample_image and clear it
            if self.app_reference.image_display.pre_resample_image is not None:
                self.app_reference.image_display.working_image = self.app_reference.image_display.pre_resample_image.copy()
                self.app_reference.image_display.pre_resample_image = None

        # Update the modified and delta displays consistently
        self.update_mod_display(param)
        self.update_delta_display(param)
        self.app_reference.image_display.redraw()
        self.app_reference.editor_widget.initialize_grid()
        self.app_reference.image_display.trigger_click_on_ascii_code(self.app_reference.current_ascii_code)

    def resample_working_image(self):
        """Helper function to resample working image based on modified config."""
        curr_config = self.get_original_config()  # Using current image config as a base
        mod_config = self.get_modified_config()
        pre_resample_image = self.app_reference.image_display.pre_resample_image

        # Call resample_image to adjust the working image
        resampled_image = resample_image(curr_config, mod_config, pre_resample_image)
        
        # Update the working image and refresh display
        self.app_reference.image_display.working_image = resampled_image

    def set_config(self, config_dict):
        """Set the current configuration and update all displays accordingly."""
        self.curr_config = config_dict.copy()
        self.mod_config = config_dict.copy()
        self.update_config_display()

    def update_config_display(self):
        """Refresh all display fields based on the current configuration."""
        for param, value in self.curr_config.items():
            self.config_params[param].set(value)
            # Only update curr_labels for numeric fields
            if param in self.curr_labels:
                self.curr_labels[param].config(text=str(value))
            # Reset delta to 0 for numeric fields
            if param in self.delta_vars:
                self.delta_vars[param].set(0)

    def update_mod_display(self, param):
        """Update the modified display field for a single parameter."""
        mod_value = self.mod_config[param]
        self.config_params[param].set(mod_value)

    def update_delta_display(self, param):
        """Update the delta display field for a single parameter."""
        delta_value = self.mod_config[param] - self.curr_config[param]
        self.delta_vars[param].set(delta_value)

    def update_apply_button_state(self):
        """Enable or disable the Apply Changes button based on changes in modified values."""
        changes_exist = any(self.curr_config.get(param) != self.mod_config.get(param) for param in self.curr_config)
        self.apply_button.config(state=tk.NORMAL if changes_exist else tk.DISABLED)
        return changes_exist

    def apply_changes(self):
        """Apply changes by updating current config to match modified config, reset deltas, and clear offsets."""
        # Set all offset-related parameters to zero in the modified config
        for key in self.mod_config:
            if key.startswith("offset"):
                self.mod_config[key] = 0

        # Copy the modified config to the current config
        self.curr_config = self.mod_config.copy()

        # Update the display to reflect the applied changes and reset deltas
        self.update_config_display()
        self.update_apply_button_state()

        # Clear the pre_resample_image and refresh the working image
        self.app_reference.image_display.pre_resample_image = None

    def get_config(self):
        """Return the modified configuration as a dictionary."""
        return self.mod_config.copy()

    def get_original_config(self):
        """Return the current configuration as a dictionary (unmodified)."""
        return self.curr_config.copy()

    def get_modified_config(self):
        """Return the modified configuration as a dictionary."""
        return self.mod_config.copy()
