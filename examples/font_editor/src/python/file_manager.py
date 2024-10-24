
import os
from tkinter import filedialog
from config_manager import get_app_config_value, set_app_config_value, load_font_metadata_from_xml, save_font_metadata_to_xml
from agon_font import write_agon_font

# ==========================================================================
# File Menu
# --------------------------------------------------------------------------
# Open
# --------------------------------------------------------------------------
import os
from tkinter import filedialog

def get_open_filename(app_reference):
    """Open a font file and load its configuration from XML."""
    # Retrieve the most recent open directory from app configuration XML
    most_recent_open_directory = get_app_config_value("most_recent_open_directory")
    
    # Open file dialog to select a font file
    file_path = filedialog.askopenfilename(
        title="Open File",
        filetypes=(
            ("All Files", "*.*"),
            ("TrueType Font Files", "*.ttf"),
            ("OpenType Font Files", "*.otf"),
            ("PSF Font Files", "*.psf"),
            ("Agon Font Files", "*.font"),
            ("PNG Images", "*.png"),
            ("XML Font Config", "*.xml")
        ),
        initialdir=most_recent_open_directory
    )

    if file_path:
        open_file(app_reference, file_path)

def open_file(app_reference, file_path):
        if not os.path.exists(file_path):
            return
        
        font_type = os.path.splitext(file_path)[1].lower()

        if font_type == ".xml":
            font_config = load_font_metadata_from_xml(file_path)
            font_config_filepath = file_path
            # Update the most recent directory and file in the app configuration
            set_app_config_value("most_recent_open_directory", os.path.dirname(file_path))
            set_app_config_value("most_recent_file", file_path)
            file_path = font_config.get('original_font_path', '')
        else:
            font_config_filepath = file_path + '.xml'
            if os.path.exists(font_config_filepath):
                app_reference.current_font_xml_file = font_config_filepath
                font_config = load_font_metadata_from_xml(font_config_filepath)
            else:
                font_config_filepath = os.path.join(os.path.dirname(__file__), "font_config.xml")
                font_config = load_font_metadata_from_xml(font_config_filepath)
                font_config["font_name"] = os.path.splitext(os.path.basename(file_path))[0]
                font_config["original_font_path"] = file_path
            # Update the most recent directory and file in the app configuration
            set_app_config_value("most_recent_open_directory", os.path.dirname(file_path))
            set_app_config_value("most_recent_file", file_path)

        # Update the app current font file path
        app_reference.current_font_file = file_path

        # Save the font metadata to the "standard" font metadata file
        save_font_metadata_to_xml(font_config, font_config_filepath)

        # Update the main window title with the file name
        filename = os.path.basename(file_path)
        app_reference.master.title(f"Agon Font Editor - {filename}")

        # Pass the font configuration to the UI and update it
        app_reference.font_config_editor.set_controls_from_config(font_config)
        app_reference.image_display.render_font()

# --------------------------------------------------------------------------        
# Save
# --------------------------------------------------------------------------
def save_file(app_reference):
    """Save a font file."""
    font_config, file_path, filetype = get_save_filename(app_reference)
    print("Font filepath: ", file_path)
    if not file_path:
        return
    if filetype == "xml":
        save_font_xml(font_config, file_path)
    elif filetype == "font":
        save_agon_font(app_reference, font_config, file_path)
    else:
        raise NotImplementedError(f"Saving {filetype} files is not supported.")

    set_app_config_value("most_recent_save_directory", os.path.dirname(file_path))
    set_app_config_value("most_recent_file", file_path)

def save_font_xml(font_config, file_path):
    """Save the font configuration to an XML file."""
    save_font_metadata_to_xml(font_config, file_path)

def save_agon_font(app_reference, font_config, file_path):
    """Save the font configuration to an Agon font file."""
    font_image = app_reference.image_display.working_image
    config_filepath = f'{file_path}.xml'
    # Update font_config with the modified dimensions
    font_config.update({
        'original_font_path': file_path,
        'font_width': font_config['font_width_mod'],
        'font_height': font_config['font_height_mod'],
        'offset_left': 0,
        'offset_top': 0,
        'offset_width': 0,
        'offset_height': 0,
        'scale_width': 0,
        'scale_height': 0,
        'raster_type': 'threshold',
        'fg_color': '255, 255, 255, 255',
        'bg_color': '0, 0, 0, 255',
    })
    # Write the .font file and the corresponding XML metadata file
    write_agon_font(font_config, font_image, file_path)
    save_font_metadata_to_xml(font_config, config_filepath)

def get_save_filename(app_reference):
    """Open a save file dialog with a default filename and automatically append the correct extension."""
    # Retrieve the most recent save directory from app configuration XML
    most_recent_save_directory = get_app_config_value("most_recent_save_directory")
    font_config = app_reference.font_config_editor.get_config()
    base_filename = make_filename_from_config(font_config)

    # Define file types and their extensions
    filetypes = [
        ("Agon Font Files", "*.font"),
        ("PNG Images", "*.png"),
        ("XML Font Config", "*.xml"),
        ("All Files", "*.*")
    ]
    
    # Open file dialog to select a font file with a default filename
    file_path = filedialog.asksaveasfilename(
        title="Save File",
        filetypes=filetypes,
        initialdir=most_recent_save_directory,
        initialfile=base_filename  # Set the default filename here
    )

    # If the user cancels the dialog, return None
    if not file_path:
        return None, None, None

    # Get the selected file type from the dialog (based on the chosen filter)
    selected_filetype = file_path.split('.')[-1].lower()
    extensions = {
        "font": ".font",
        "png": ".png", 
        "xml": ".xml"
    }

    # Append the correct extension if not already present
    if not any(file_path.lower().endswith(ext) for ext in extensions.values()):
        for description, pattern in filetypes:
            ext = pattern.lstrip("*")  # Extract the extension from pattern
            if selected_filetype in ext:
                file_path += ext
                break
        else:
            file_path += ".xml"  # Default to .xml if none matches

    return font_config, file_path, selected_filetype

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

# ==========================================================================
# Helper Functions
# --------------------------------------------------------------------------
def make_filename_from_config(font_config):
    """Generate a filename based on the font configuration."""
    font_name = font_config['font_name']
    font_variant = font_config['font_variant']
    font_width = font_config['font_width_mod']
    font_height = font_config['font_height_mod']
    
    return f"{font_name}_{font_variant}_{font_width}x{font_height}"