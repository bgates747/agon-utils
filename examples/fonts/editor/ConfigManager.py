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
        """Retrieve and return the default directory, interpreting relative paths correctly."""
        default_dir = self.get_setting('default_directory', 'fabfont/Regular')
        # Convert to absolute path if it's relative
        if not os.path.isabs(default_dir):
            default_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), default_dir)
        return default_dir

    def get_default_font_file(self):
        """Retrieve and return the default font file path, interpreting relative paths correctly."""
        default_file = self.get_setting('default_font_file', 'fabfont/Regular/fabfont_9x15.png')
        # Convert to absolute path if it's relative
        if not os.path.isabs(default_file):
            default_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), default_file)
        return default_file

    def get_most_recent_directory(self):
        """Get the most recent directory if valid, or fall back to default directory."""
        most_recent_dir = self.get_setting('most_recent_directory')
        if most_recent_dir and os.path.isdir(most_recent_dir):
            return most_recent_dir
        # If not valid, use default directory
        return self.get_default_directory()

    def set_most_recent_directory(self, directory):
        """Set a new most recent directory."""
        self.set_setting('most_recent_directory', directory)

    def get_most_recent_file(self):
        """Retrieve the most recent file path if it exists, otherwise return the default font file."""
        most_recent_file = self.get_setting('most_recent_file')
        
        # Check if the most recent file exists and is valid
        if most_recent_file and os.path.isfile(most_recent_file):
            return most_recent_file
        
        # Fall back to the default font file
        return self.get_default_font_file()

    def set_most_recent_file(self, file_path):
        """Set the most recent file path."""
        self.set_setting('most_recent_file', file_path)
