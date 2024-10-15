
import os
from tkinter import filedialog
from config_manager import get_xml_value, set_xml_value, load_font_metadata_from_xml, dict_to_text

# ==========================================================================
# File Menu
# --------------------------------------------------------------------------
# Open
# --------------------------------------------------------------------------
import os
from tkinter import filedialog

def open_file(app_reference):
    """Open a font file and load its configuration from XML."""
    # Retrieve the most recent open directory from app configuration XML
    most_recent_open_directory = get_xml_value("app_config.xml", "settings", "most_recent_open_directory")
    
    # Open file dialog to select a font file
    file_path = filedialog.askopenfilename(
        title="Open File",
        filetypes=(
            ("All Files", "*.*"),
            ("TrueType Font Files", "*.ttf"),
            ("OpenType Font Files", "*.otf"),
            ("PSF Font Files", "*.psf"),
            ("Agon Font Files", "*.font"),
            ("PNG Images", "*.png")
        ),
        initialdir=most_recent_open_directory
    )

    if file_path:
        # Define the corresponding XML config path
        font_config_filepath = file_path + '.xml'
        
        # Load font metadata from XML or derive it if XML doesn't exist
        if os.path.exists(font_config_filepath):
            font_config = load_font_metadata_from_xml(font_config_filepath)
            print(dict_to_text(font_config))
        # else:
        #     font_config = app_reference.parse_font_filename(file_path)  # Custom function for fallback parsing

        # # Load the font data using the font metadata
        # font_config, font_image = read_font(file_path, font_config)

        # # Pass the font configuration to the UI components
        # app_reference.font_config_editor.setup_ui_from_config(font_config)
        # app_reference.image_display.load_image(font_image)
        # app_reference.editor_widget.initialize_grid()
        
        # Update the most recent directory and file in the app configuration
        set_xml_value("app_config.xml", "settings", "most_recent_open_directory", os.path.dirname(file_path))
        set_xml_value("app_config.xml", "settings", "most_recent_file", file_path)

        # Update the main window title with the file name
        filename = os.path.basename(file_path)
        app_reference.master.title(f"Agon Font Editor - {filename}")

# --------------------------------------------------------------------------        
# Save
# --------------------------------------------------------------------------
def save_file():
    """Save a font file."""
    pass  # Implement file save functionality here

# --------------------------------------------------------------------------        
# Import
# --------------------------------------------------------------------------
def import_file():
    """Handle the 'Import' menu option to import data from an external file."""
    pass  # Implement import functionality here

# --------------------------------------------------------------------------
# Export
# --------------------------------------------------------------------------
def export_file():
    """Handle the 'Export' menu option to export data to an external file."""
    pass  # Implement export functionality here

# --------------------------------------------------------------------------
# Revert
# --------------------------------------------------------------------------
def revert_changes():
    """Handle the 'Revert' menu option to undo changes to the last saved state."""
    pass  # Implement revert functionality here