import configparser
import os

class ConfigManager:
    def __init__(self, app_config_file='data/config.ini', font_meta_file='data/font.cfg'):
        # Paths to config files, relative to the script directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.app_config_file = os.path.join(script_dir, app_config_file)
        self.font_meta_file = os.path.join(script_dir, font_meta_file)
        
        # ConfigParser instances for each config file
        self.app_config = configparser.ConfigParser()
        self.font_meta_config = configparser.ConfigParser()
        
        # Load both config files
        self.load_config()

    def load_config(self):
        """Load both application and font metadata configurations."""
        self.app_config.read(self.app_config_file)
        self.font_meta_config.read(self.font_meta_file)

    def save_config(self, config_type='app'):
        """Save configuration to the specified file."""
        config = self.app_config if config_type == 'app' else self.font_meta_config
        config_file = self.app_config_file if config_type == 'app' else self.font_meta_file
        with open(config_file, 'w') as file:
            config.write(file)

    # =========================================================================
    # Application settings methods (config.ini)
    # =========================================================================
    
    def get_setting(self, key, fallback=None):
        """Retrieve an application setting with an optional fallback."""
        return self.app_config['settings'].get(key, fallback)

    def set_setting(self, key, value):
        """Set a new application setting and save it."""
        if 'settings' not in self.app_config:
            self.app_config['settings'] = {}
        self.app_config['settings'][key] = str(value)
        self.save_config(config_type='app')

    # Directory-related methods (remain as is)
    def get_default_directory(self):
        default_dir = self.get_setting('default_directory', 'fabfont/Regular')
        if not os.path.isabs(default_dir):
            default_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), default_dir)
        return default_dir

    def get_default_font_file(self):
        default_file = self.get_setting('default_font_file', 'fabfont/Regular/fabfont_9x15.png')
        if not os.path.isabs(default_file):
            default_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), default_file)
        return default_file

    def get_most_recent_open_directory(self):
        most_recent_open_dir = self.get_setting('most_recent_open_directory')
        if most_recent_open_dir and os.path.isdir(most_recent_open_dir):
            return most_recent_open_dir
        return self.get_default_directory()

    def set_most_recent_open_directory(self, directory):
        self.set_setting('most_recent_open_directory', directory)

    def get_most_recent_save_directory(self):
        most_recent_save_dir = self.get_setting('most_recent_save_directory')
        if most_recent_save_dir and os.path.isdir(most_recent_save_dir):
            return most_recent_save_dir
        return self.get_default_directory()

    def set_most_recent_save_directory(self, directory):
        self.set_setting('most_recent_save_directory', directory)

    def get_most_recent_file(self):
        most_recent_file = self.get_setting('most_recent_file')
        if most_recent_file and os.path.isfile(most_recent_file):
            return most_recent_file
        return self.get_default_font_file()

    def set_most_recent_file(self, file_path):
        self.set_setting('most_recent_file', file_path)

    # =========================================================================
    # General method to get default values from any config file
    # =========================================================================

    def get_config_defaults(self, config_file):
        """Retrieve default values from a specified configuration file."""
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), config_file)
        parser = configparser.ConfigParser()
        
        # Dictionary to hold default values
        default_config = {}
        
        # Read the configuration file
        if not parser.read(config_path):
            raise FileNotFoundError(f"Configuration file '{config_file}' not found.")

        for section in parser.sections():
            # Check if the section has a 'default' option
            if parser.has_option(section, 'default'):
                default = parser.get(section, 'default')
                datatype = parser.get(section, 'type').lower()
                default_config[section] = self._parse_value(default, datatype)
            else:
                # Handle sections without 'default' as needed
                print(f"Warning: No 'default' option found in section '{section}' of {config_file}")
        
        return default_config

    # =========================================================================
    # Font metadata methods (data/font.cfg)
    # =========================================================================

    def get_font_meta(self, key, fallback=None):
        """Retrieve a font metadata setting with an optional fallback."""
        return self.font_meta_config['font_metadata'].get(key, fallback)

    def set_font_meta(self, key, value):
        """Set a new font metadata setting and save it."""
        if 'font_metadata' not in self.font_meta_config:
            self.font_meta_config['font_metadata'] = {}
        self.font_meta_config['font_metadata'][key] = str(value)
        self.save_config(config_type='font_meta')

    def get_default_ascii_range(self):
        """Retrieve the default ASCII range for font metadata."""
        start = int(self.get_font_meta('ascii_range_start', '32'))
        end = int(self.get_font_meta('ascii_range_end', '127'))
        return start, end

    def set_default_ascii_range(self, start, end):
        """Set the default ASCII range in the font metadata file."""
        self.set_font_meta('ascii_range_start', start)
        self.set_font_meta('ascii_range_end', end)
        self.save_config(config_type='font_meta')

    # =========================================================================
    # Helper Methods
    # =========================================================================

    def _parse_value(self, value, datatype):
        """Parse the given value according to the specified data type, handling +Inf and -Inf."""
        if value == '+Inf':
            return float('inf')
        elif value == '-Inf':
            return float('-inf')

        if datatype == 'int':
            return int(value)
        elif datatype == 'float':
            return float(value)
        elif datatype == 'string':
            return value
        elif datatype == 'bool':
            return value.lower() in ['true', '1', 'yes']
        else:
            raise ValueError(f"Unsupported data type '{datatype}'")