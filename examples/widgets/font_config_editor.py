import tkinter as tk
from tkinter import Button
import xml.etree.ElementTree as ET
from font_config_widget import FontConfigDeltaControl, FontConfigDeltaDisplay, FontConfigTextBox, FontConfigComboBox, FontConfigColorPicker
from config_manager import dict_to_text, load_xml
from agon_font import resample_image, read_font

class FontConfigEditor(tk.Frame):
    """
    A dynamic editor for font configurations, creating controls based on data-driven configuration.
    """
    def __init__(self, parent, config_editor_file, app_reference, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.app_reference = app_reference
        self.config_editor_file = config_editor_file
        self.font_config_xml = load_xml(self.config_editor_file)
        self.controls = {}
        self.visibility_rules = []
        self.event_handlers = {}
        self.create_widgets()
        self.create_buttons()

    def create_buttons(self):
        """Add buttons to print current and modified values to the console."""
        self.print_current_button = Button(self, text="Print Current Values", command=self.print_modified_values)
        self.print_current_button.grid(row=100, column=0, pady=10, sticky="w")

        self.print_modified_button = Button(self, text="Print Modified Values", command=self.print_modified_values)
        self.print_modified_button.grid(row=101, column=0, pady=10, sticky="w")

        self.print_original_button = Button(self, text="Print Original Values", command=self.print_original_values)
        self.print_original_button.grid(row=102, column=0, pady=10, sticky="w")

    def create_widgets(self):
        # Loop through each setting and create the appropriate control
        row = 0
        for setting in self.font_config_xml.findall("setting"):
            config_setting = setting.get("name")
            widget_type = setting.find("widget_type").text
            if widget_type == "FontConfigDeltaControl":
                control = FontConfigDeltaControl(self, config_setting, self.font_config_xml)
            elif widget_type == "FontConfigDeltaDisplay":
                control = FontConfigDeltaDisplay(self, config_setting, self.font_config_xml)
            elif widget_type == "FontConfigTextBox":
                control = FontConfigTextBox(self, config_setting, self.font_config_xml)
            elif widget_type == "FontConfigComboBox":
                control = FontConfigComboBox(self, config_setting, self.font_config_xml)
            elif widget_type == "FontConfigColorPicker":
                control = FontConfigColorPicker(self, config_setting, self.font_config_xml)
            else:
                raise ValueError(f"Unsupported widget type: {widget_type}")
            
            # Create visibility rules for the control
            visible_element = setting.find("visible")
            if visible_element is not None:
                dependent_setting = visible_element.find("setting").get("name")
                target_values = [val.text for val in visible_element.find("setting").findall("item")]
                self.visibility_rules.append({
                    "setting_name": config_setting,
                    "dependent_setting": dependent_setting,
                    "target_values": target_values
                })
            
            control.grid(row=row, column=0, sticky="w")
            self.controls[config_setting] = control
            row += 1

    def get_original_config(self):
        """Return a dictionary of original values for all controls, with config_setting as the key."""
        original_values = {}
        for config_setting, control in self.controls.items():
            original_values[config_setting] = control.get_original_value()
        return original_values
            
    def get_modified_config(self):
        """Return a dictionary of modified values for all controls, with config_setting as the key."""
        modified_values = {}
        for config_setting, control in self.controls.items():
            modified_values[config_setting] = control.get_value()
        return modified_values

    def print_modified_values(self):
        """Print the current values dictionary to the console."""
        print("Current Values:\n", dict_to_text(self.get_modified_config()))

    def print_modified_values(self):
        """Print the modified values dictionary to the console."""
        print("Modified Values:\n", dict_to_text(self.get_modified_config()))

    def print_original_values(self):
        """Print the original values dictionary to the console."""
        print("Original Values:\n", dict_to_text(self.get_original_config()))

    def set_controls_from_config(self, font_config):
        """Set the control values based on the provided font configuration dictionary."""
        for config_setting, control in self.controls.items():
            if config_setting in font_config:
                control.set_value(font_config[config_setting])

    def set_controls_original_from_config(self, font_config):
        """Set the control values based on the provided font configuration dictionary."""
        for config_setting, control in self.controls.items():
            if config_setting in font_config:
                control.set_original_value(font_config[config_setting])

    def set_visible(self, setting_name):
        """Handle changes in controls and adjust visibility of dependent controls."""
        control = self.controls[setting_name]
        original_value = control.get_value()

        # Check visibility rules to determine visibility of controls
        for rule in self.visibility_rules:
            if rule["dependent_setting"] == setting_name:
                dependent_control = self.controls[rule["setting_name"]]
                if original_value in rule["target_values"]:
                    if dependent_control.hidden:
                        dependent_control.grid(**dependent_control.grid_info())  # Corrected here
                        dependent_control.hidden = False
                else:
                    if not dependent_control.hidden:
                        dependent_control.grid_remove()
                        dependent_control.hidden = True

    # =========================================================================
    # Parameter Modification Methods
    # =========================================================================

    def changes_exist(self):
        """Check if any changes have been made to the configuration."""
        original_values = self.get_original_config()
        modified_values = self.get_modified_config()
        return original_values != modified_values

    def resample_font(self):
        """Adjust the modified value based on the delta and update displays."""
        # Check if Apply Changes should be enabled
        changes_exist = self.changes_exist()

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

    def redraw_font(self):
        """Redraw the font image based on the current configuration."""
        self.app_reference.image_display.pre_resample_image = None
        
        file_path = self.app_reference.current_font_file
        font_config = self.get_modified_config()
        font_config, font_image = read_font(file_path, font_config)

        self.set_controls_original_from_config(font_config)
        self.app_reference.image_display.load_image(font_image)
        self.resample_working_image()
        self.app_reference.editor_widget.initialize_grid()
        self.app_reference.image_display.trigger_click_on_ascii_code(self.app_reference.current_ascii_code)
