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

    def get_setting(self, key, fallback=None):
        """Retrieve a setting from the config file with an optional fallback."""
        return self.config['settings'].get(key, fallback)

    def set_setting(self, key, value):
        """Set a new setting in the config and save it."""
        if 'settings' not in self.config:
            self.config['settings'] = {}
        self.config['settings'][key] = str(value)
        self.save_config()

    def get_default_directory(self):
        """Get the default directory, or use the directory containing the application."""
        return self.get_setting('default_directory', os.path.dirname(os.path.abspath(__file__)))

    def set_default_directory(self, directory):
        """Set a new default directory."""
        self.set_setting('default_directory', directory)

    def get_default_ascii_range(self):
        """Get the default ASCII range from the config, with a specific fallback."""
        start = int(self.get_setting('ascii_range_start', '32'))
        end = int(self.get_setting('ascii_range_end', '127'))
        return (start, end)

    def set_default_ascii_range(self, start, end):
        """Set a new default ASCII range."""
        self.set_setting('ascii_range_start', start)
        self.set_setting('ascii_range_end', end)