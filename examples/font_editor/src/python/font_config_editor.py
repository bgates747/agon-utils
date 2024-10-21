import tkinter as tk
from tkinter import Button
import xml.etree.ElementTree as ET
from font_config_widget import FontConfigDeltaControl, FontConfigTextBox, FontConfigComboBox, FontConfigColorPicker
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
        """Add buttons to print current and  values to the console."""
        self.print_values_button = Button(self, text="Print Current Values", command=self.print_values)
        self.print_values_button.grid(row=100, column=0, pady=10, sticky="w")

    def create_widgets(self):
        # Loop through each setting and create the appropriate control
        row = 0
        for setting in self.font_config_xml.findall("setting"):
            config_setting = setting.get("name")
            widget_type = setting.find("widget_type").text
            if widget_type == "FontConfigDeltaControl":
                control = FontConfigDeltaControl(self, config_setting, self.font_config_xml)
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
            
    def get_config(self):
        """Return a dictionary of  values for all controls, with config_setting as the key."""
        values = {}
        for config_setting, control in self.controls.items():
            values[config_setting] = control.value
        return values

    def print_values(self):
        """Print the current values dictionary to the console."""
        print("Current Values:\n", dict_to_text(self.get_config()))

    def set_controls_from_config(self, font_config):
        """Set the control values based on the provided font configuration dictionary."""
        for config_setting, control in self.controls.items():
            if config_setting in font_config:
                control.value = font_config[config_setting]

    def set_visible(self, setting_name):
        """Handle changes in controls and adjust visibility of dependent controls."""
        control = self.controls[setting_name]
        original_value = control.value

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

    def render_font(self):
        """Redraw the font image based on the current configuration."""        
        file_path = self.app_reference.current_font_file
        font_config = self.get_config()
        font_config, font_image = read_font(file_path, font_config)
        self.compute_font_size_from_offsets(font_config)
        self.set_controls_from_config(font_config)
        self.app_reference.image_display.original_image = font_image
        self.app_reference.image_display.working_image = font_image

        if font_config['offset_left'] != 0 or font_config['offset_top'] != 0 or font_config['offset_width'] != 0 or font_config['offset_height'] != 0:
            self.resample_font()
        else:
            self.update_font_image(font_image)

    def resample_font(self):
        font_config = self.get_config()
        font_config = self.compute_font_size_from_offsets(font_config)
        self.set_controls_from_config(font_config)
        font_image = resample_image(font_config, self.app_reference.image_display.original_image)
        self.update_font_image(font_image)
    
    def update_font_image(self, font_image):
        self.app_reference.image_display.working_image = font_image
        self.app_reference.image_display.load_image(font_image)
        self.app_reference.editor_widget.initialize_grid()
        self.app_reference.image_display.trigger_click_on_ascii_code(self.app_reference.image_display.current_ascii_code)

    def compute_font_size_from_offsets(self, font_config):
        """Compute the font size based on offsets and update the font configuration."""
        font_config['font_width_mod'] = font_config['font_width'] + font_config['offset_width']
        font_config['font_height_mod'] = font_config['font_height'] + font_config['offset_height']
        return font_config
