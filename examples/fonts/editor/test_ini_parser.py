import tkinter as tk
from ConfigManager import ConfigManager  # Update path if necessary
from FileManager import FileManager
from FontEditor import FontEditorApp  # Update path if necessary

# Mock root Tk object
root = tk.Tk()
root.withdraw()  # Hide the main Tkinter window

# Initialize ConfigManager
config_manager = ConfigManager(app_config_file='data/config.ini', font_meta_file='data/fontmeta.cfg')

# Initialize the FontEditorApp without launching the UI components
app = FontEditorApp(root, config_manager)

# Only initialize FileManager by manually passing the app reference
file_manager = FileManager(app)

# Path to the .ini file you want to load
ini_file_path = 'examples/fonts/tgt/ttf/amiga_forever_8x8.font.ini'  # Update to your .ini file path

# Load font metadata from the .ini file
font_metadata = file_manager.load_font_metadata_from_ini(ini_file_path)

# Print the resulting font metadata dictionary
print("Font Metadata:", font_metadata)

# Destroy root to clean up after testing
root.destroy()

