import configparser
import os

class ConfigManager:
    def __init__(self, config_file='config.ini'):
        # Ensure the config file is always relative to the script directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_file = os.path.join(script_dir, config_file)
        self.config = configparser.ConfigParser()

        # Load the config file
        self.load_config()

    def load_config(self):
        """Load the configuration from the config file."""
        self.config.read(self.config_file)

    def save_config(self):
        """Write the current config to the file."""
        with open(self.config_file, 'w') as file:
            self.config.write(file)

    def get_default(self, key, fallback=None):
        """Get a generic default value from the config file, with an optional fallback."""
        return self.config['settings'].get(key, fallback)

    def set_setting(self, key, value):
        """Set a new setting in the config and save it."""
        if 'settings' not in self.config:
            self.config['settings'] = {}
        self.config['settings'][key] = str(value)
        self.save_config()  # Save the updated config

    def get_default_directory(self):
        """Get the default directory from the config, or use the directory containing the application."""
        return self.get_default('default_directory', os.path.dirname(os.path.abspath(__file__)))
    
    def set_default_directory(self, directory):
        """Set a new default directory and update the config file."""
        self.config['settings']['default_directory'] = directory
        self.save_config()

    def get_default_zoom_level(self):
        """Get the default zoom level from the config."""
        return int(self.get_default('default_zoom_level', '200'))

    def set_default_zoom_level(self, zoom_level):
        """Set a new default zoom level and update the config file."""
        self.config['settings']['default_zoom_level'] = str(zoom_level)
        self.save_config()

    def get_default_ascii_range(self):
        """Get the default ASCII range from the config."""
        start = int(self.get_default('ascii_range_start', '32'))
        end = int(self.get_default('ascii_range_end', '127'))
        return (start, end)

    def set_default_ascii_range(self, start, end):
        """Set a new default ASCII range and update the config file."""
        self.config['settings']['ascii_range_start'] = str(start)
        self.config['settings']['ascii_range_end'] = str(end)
        self.save_config()

    def get_default_font_width(self):
        """Get the default font width from the config."""
        return int(self.get_default('default_font_width', '8'))

    def get_default_font_height(self):
        """Get the default font height from the config."""
        return int(self.get_default('default_font_height', '11'))

    def get_default_offset_left(self):
        """Get the default left offset from the config."""
        return int(self.get_default('default_offset_left', '0'))

    def get_default_offset_top(self):
        """Get the default top offset from the config."""
        return int(self.get_default('default_offset_top', '0'))

    def get_default_offset_width(self):
        """Get the default width offset from the config."""
        return int(self.get_default('default_offset_width', '0'))

    def get_default_offset_height(self):
        """Get the default height offset from the config."""
        return int(self.get_default('default_offset_height', '0'))
