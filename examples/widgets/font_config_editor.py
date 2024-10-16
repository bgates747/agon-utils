import tkinter as tk
from tkinter import ttk, Button
import xml.etree.ElementTree as ET
from custom_widgets import DeltaControl, ConfigTextBox, ConfigComboBox, ConfigColorPicker
from config_manager import get_typed_data, dict_to_text

class FontConfigEditor(tk.Frame):
    """
    A dynamic editor for font configurations, creating controls based on data-driven configuration.
    """
    def __init__(self, parent, config_file, app_reference, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.app_reference = app_reference
        self.config_file = config_file
        self.controls = {}
        self.visibility_rules = []
        self.event_handlers = {}
        self.create_widgets()
        self.create_buttons()

    def create_buttons(self):
        """Add buttons to print current and modified values to the console."""
        self.print_current_button = Button(self, text="Print Current Values", command=self.print_current_values)
        self.print_current_button.grid(row=100, column=0, pady=10, sticky="w")

        self.print_modified_button = Button(self, text="Print Modified Values", command=self.print_modified_values)
        self.print_modified_button.grid(row=100, column=1, pady=10, sticky="w")

    def create_widgets(self):
        # Parse the XML configuration file
        tree = ET.parse(self.config_file)
        root = tree.getroot()

        # Loop through each setting and create the appropriate control
        row = 0
        for setting in root.findall("setting"):
            setting_name = setting.get("name")  # Retrieve the setting name attribute
            widget_type = setting.find("widget_type").text
            label_text = setting.find("label_text").text
            data_type = setting.find("data_type").text
            default_value = get_typed_data(data_type, setting.find("default_value").text)
            
            # Initialize the control based on widget_type
            setting_control = None
            if widget_type == "DeltaControl":
                # DeltaControl requires min, max, and step values
                min_value = get_typed_data(data_type, setting.find("min_value").text)
                max_value = get_typed_data(data_type, setting.find("max_value").text)
                step_value = get_typed_data(data_type, setting.find("step_value").text)
                setting_control = DeltaControl(self, label_text, data_type, default_value, min_value, max_value, step_value)

            elif widget_type == "ConfigTextBox":
                # ConfigTextBox with only label and default value
                setting_control = ConfigTextBox(self, label_text, default_value)
                
            elif widget_type == "ConfigComboBox":
                # ConfigComboBox requires additional options
                options = [opt.text for opt in setting.find("options").findall("value")]
                setting_control = ConfigComboBox(self, label_text, options, default_value)
                # Bind the change event for ConfigComboBox if event handlers are defined
                event_handlers_element = setting.find("event_handlers")
                if event_handlers_element is not None:
                    self.event_handlers[setting_name] = {}
                    for event_type in event_handlers_element:
                        self.event_handlers[setting_name][event_type.tag] = [
                            handler.text for handler in event_type.findall("handler")
                        ]
                    if "on_change" in self.event_handlers[setting_name]:
                        setting_control.bind_combobox_event("<<ComboboxSelected>>", self.make_combobox_callback(setting_name))

            elif widget_type == "ConfigColorPicker":
                # ConfigColorPicker for color selection
                setting_control = ConfigColorPicker(self, label_text, default_value)

            # Place control in the grid if it was created
            if setting_control:
                setting_control.grid(row=row, column=0, pady=0, padx=10, sticky="w")
                setting_control.hidden = False  # Custom attribute to manage visibility state
                setting_control.grid_info = setting_control.grid_info()  # Store original grid information
                self.controls[setting_name] = setting_control
                row += 1

            # Handle visibility rules for the control
            visible_element = setting.find("visible")
            if visible_element is not None:
                dependent_setting = visible_element.find("setting").get("name")
                target_values = [val.text for val in visible_element.find("setting").findall("list")]
                self.visibility_rules.append({
                    "setting_name": setting_name,
                    "dependent_setting": dependent_setting,
                    "target_values": target_values
                })

    def make_combobox_callback(self, setting_name):
        """Generate a callback function for the combobox change event."""
        def callback(event):
            print(f"Combobox changed for: {setting_name}")  # Debug print to verify event firing
            self.on_combobox_change(setting_name)
        return callback

    def on_combobox_change(self, setting_name):
        """Handle changes in combobox controls and adjust visibility of dependent controls."""
        control = self.controls[setting_name]
        current_value = control.get_value()

        # Check visibility rules to determine visibility of controls
        for rule in self.visibility_rules:
            if rule["dependent_setting"] == setting_name:
                dependent_control = self.controls[rule["setting_name"]]
                if current_value in rule["target_values"]:
                    if dependent_control.hidden:
                        dependent_control.grid(**dependent_control.grid_info)
                        dependent_control.hidden = False
                else:
                    if not dependent_control.hidden:
                        dependent_control.grid_remove()
                        dependent_control.hidden = True

        # Check if there are specific event handlers for the change
        if setting_name in self.event_handlers and "on_change" in self.event_handlers[setting_name]:
            handlers = self.event_handlers[setting_name]["on_change"]
            for handler_name in handlers:
                if handler_name == "default":
                    self.default_handler(setting_name, "on_change")
                else:
                    handler = getattr(self, handler_name, None)
                    if handler:
                        handler(setting_name)
                    else:
                        print(f"No handler named {handler_name} found for setting: {setting_name}, event type: on_change")

    def handle_event(self, setting_name, event_type):
        """Handle an event for a specific setting, executing all specified handlers in order."""
        if setting_name in self.event_handlers and event_type in self.event_handlers[setting_name]:
            handlers = self.event_handlers[setting_name][event_type]
            for handler_name in handlers:
                if handler_name == "default":
                    self.default_handler(setting_name, event_type)
                else:
                    handler = getattr(self, handler_name, None)
                    if handler:
                        handler(setting_name)
                    else:
                        print(f"No handler named {handler_name} found for setting: {setting_name}, event type: {event_type}")
        else:
            self.default_handler(setting_name, event_type)

    def default_handler(self, setting_name, event_type):
        """Default handler for events without a specific handler."""
        print(f"Default handling for setting: {setting_name}, event type: {event_type}")

    def get_current_values(self):
        """Return a dictionary of current values for all controls, with setting_name as the key."""
        current_values = {}
        for setting_name, control in self.controls.items():
            if isinstance(control, DeltaControl):
                current_values[setting_name] = control.current_value
            else:
                current_values[setting_name] = control.get_value()
        return current_values

    def get_modified_values(self):
        """Return a dictionary of modified values for all controls, with setting_name as the key."""
        modified_values = {}
        for setting_name, control in self.controls.items():
            if isinstance(control, DeltaControl):
                modified_values[setting_name] = float(control.modified_var.get()) if control.data_type == 'float' else int(control.modified_var.get())
            else:
                modified_values[setting_name] = control.get_value()
        return modified_values

    def get_config(self):
        """Return a dictionary of modified values for all controls, with setting_name as the key."""
        return self.get_modified_values()

    def print_current_values(self):
        """Print the current values dictionary to the console."""
        print("Current Values:\n", dict_to_text(self.get_current_values()))

    def print_modified_values(self):
        """Print the modified values dictionary to the console."""
        print("Modified Values:\n", dict_to_text(self.get_modified_values()))

    def setup_ui_from_config(self, font_config):
        """Set the control values based on the provided font configuration dictionary."""
        for setting_name, control in self.controls.items():
            if setting_name in font_config:
                control.set_value(font_config[setting_name])
