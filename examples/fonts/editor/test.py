import os
from ConfigManager import ConfigManager

# Assuming that fontmeta.cfg is in the same directory as this script
def main():
    # Initialize ConfigManager with specified config file names
    config_manager = ConfigManager(app_config_file='config.ini', font_meta_file='fontmeta.cfg')
    
    # Get defaults from fontmeta.cfg
    try:
        fontmeta_defaults = config_manager.get_config_defaults('fontmeta.cfg')
        print("Font Metadata Defaults:")
        for key, value in fontmeta_defaults.items():
            print(f"{key}: {value}")
    except FileNotFoundError as e:
        print(e)
    except Exception as e:
        print(f"Error reading font metadata defaults: {e}")

if __name__ == "__main__":
    main()
