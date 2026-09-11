
import os
from tkinter import StringVar, filedialog, messagebox
from config_manager import get_app_config_value, set_app_config_value, load_font_metadata_from_xml, save_font_metadata_to_xml
from agon_font import (read_font, read_png_font, read_agon_font, resolve_font_source,
                       write_agon_font, write_rgba2_font)

# ==========================================================================
# File Menu
# --------------------------------------------------------------------------
# Open
# --------------------------------------------------------------------------
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
            ("RGBA2 Font Files", "*.rgba2"),
            ("PNG Images", "*.png"),
            ("XML Font Config", "*.xml")
        ),
        initialdir=most_recent_open_directory
    )

    if file_path:
        try:
            if not open_file(app_reference, file_path):
                raise FileNotFoundError(file_path)
        except (OSError, ValueError, KeyError, TypeError) as error:
            messagebox.showerror("Cannot open font", str(error), parent=app_reference.master)


def _validate_open_config(config):
    """Reject unusable geometry/colors before rendering or changing Tk controls."""
    for name in ("font_width", "font_height", "font_width_mod", "font_height_mod",
                 "point_size", "chars_per_row"):
        if config[name] <= 0:
            raise ValueError(f"{name} must be positive")
    if not 0 <= config["ascii_start"] <= config["ascii_end"] <= 0x10FFFF:
        raise ValueError("Invalid character range")
    for name in ("fg_color", "bg_color"):
        components = tuple(int(value.strip()) for value in config[name].split(","))
        if len(components) != 4 or any(not 0 <= value <= 255 for value in components):
            raise ValueError(f"{name} must contain four RGBA values from 0 to 255")

def open_file(app_reference, file_path):
    """Prepare a candidate without mutating the document, then install it."""
    requested_path = os.path.abspath(file_path)
    if not os.path.exists(requested_path):
        return False

    saved_bitmap = None
    extension = os.path.splitext(requested_path)[1].lower()
    if extension == ".xml":
        metadata_path = requested_path
        font_config = load_font_metadata_from_xml(metadata_path)
        file_path = resolve_font_source(metadata_path, font_config)
    else:
        file_path = requested_path
        metadata_path = file_path + ".xml"
        if os.path.exists(metadata_path):
            font_config = load_font_metadata_from_xml(metadata_path)
            if extension in {".png", ".font"}:
                saved_bitmap = load_font_metadata_from_xml(metadata_path, bitmap=True)
                if saved_bitmap is None and extension == ".font":
                    _validate_open_config(font_config)
                    saved_bitmap = _bitmap_export_config(font_config, file_path, monochrome=True)
                if saved_bitmap is not None:
                    font_config = saved_bitmap
        else:
            metadata_path = None
            defaults_path = os.path.join(os.path.dirname(__file__), "font_config.xml")
            font_config = load_font_metadata_from_xml(defaults_path)
            font_config["font_name"] = os.path.splitext(os.path.basename(file_path))[0]
            font_config["original_font_path"] = file_path
    # Direct bitmap opening starts from those pixels. XML opening starts from
    # its source recipe; a saved output must never replace that recipe's source.
    font_config["original_font_path"] = file_path

    # Decoding, rasterization, and display-value validation can all fail. None
    # of them should change the open document or write its source metadata.
    _validate_open_config(font_config)
    if saved_bitmap is not None:
        reader = read_png_font if extension == ".png" else read_agon_font
        font_config, font_image = reader(file_path, font_config)
    else:
        font_config, font_image = read_font(file_path, font_config)
        file_path = font_config["original_font_path"]
    font_config["font_width_mod"] = font_config["font_width"] + font_config["offset_width"] + font_config["scale_width"]
    font_config["font_height_mod"] = font_config["font_height"] + font_config["offset_height"] + font_config["scale_height"]
    _validate_open_config(font_config)
    font_image = font_image.convert("RGB")

    app_reference.font_config_editor.set_controls_from_config(font_config)
    app_reference.current_font_file = file_path
    app_reference.current_font_xml_file = metadata_path
    app_reference.master.title(f"Agon Font Editor - {os.path.basename(file_path)}")
    app_reference.image_display.load_image(font_image)
    set_app_config_value("most_recent_open_directory", os.path.dirname(requested_path))
    set_app_config_value("most_recent_file", requested_path)
    return True

# --------------------------------------------------------------------------        
# Save
# --------------------------------------------------------------------------
def save_file(app_reference):
    """Save a font file."""
    font_config, file_path, filetype = get_save_filename(app_reference)
    print("Font filepath: ", file_path)
    if not file_path:
        return
    if filetype != "xml":
        source = font_config.get("original_font_path")
        if (source and os.path.exists(source) and os.path.exists(file_path)
                and os.path.samefile(source, file_path)):
            messagebox.showerror(
                "Cannot overwrite original source",
                "Choose a different output filename to retain the original font source.",
                parent=app_reference.master,
            )
            return
    if filetype == "xml":
        save_font_xml(font_config, file_path)
    elif filetype == "font":
        save_agon_font(app_reference, font_config, file_path)
    elif filetype == "png":
        save_png_font(app_reference, font_config, file_path)
    elif filetype == "rgba2":
        font_config = save_rgba2_font(app_reference, font_config, file_path)
    else:
        raise NotImplementedError(f"Saving {filetype} files is not supported.")

    set_app_config_value("most_recent_save_directory", os.path.dirname(file_path))
    recipe_path = file_path if filetype == "xml" else f"{file_path}.xml"
    set_app_config_value("most_recent_file", os.path.abspath(recipe_path))
    app_reference.current_font_xml_file = os.path.abspath(recipe_path)
    app_reference.font_config_editor.set_controls_from_config(font_config)

def save_font_xml(font_config, file_path):
    """Save the font configuration to an XML file."""
    save_font_metadata_to_xml(_source_recipe(font_config), file_path)

def _source_recipe(font_config):
    recipe = font_config.copy()
    source = recipe.get('original_font_path')
    if not source:
        raise ValueError("The font has no original source path")
    recipe['original_font_path'] = os.path.abspath(source)
    return recipe

def _bitmap_export_config(font_config, file_path, *, monochrome=False):
    """Describe saved pixels without baking source transforms into metadata."""
    export_config = font_config.copy()
    export_config.update({
        'original_font_path': os.path.abspath(file_path),
        'font_width': font_config['font_width_mod'],
        'font_height': font_config['font_height_mod'],
        'offset_left': 0,
        'offset_top': 0,
        'offset_width': 0,
        'offset_height': 0,
        'scale_width': 0,
        'scale_height': 0,
    })
    if monochrome:
        export_config.update({
            'raster_type': 'threshold',
            'fg_color': '255, 255, 255, 255',
            'bg_color': '0, 0, 0, 255',
        })
    return export_config


def save_agon_font(app_reference, font_config, file_path):
    """Export the current bitmap as a monochrome Agon font."""
    font_image = app_reference.image_display.working_image
    config_filepath = f'{file_path}.xml'
    export_config = _bitmap_export_config(font_config, file_path, monochrome=True)
    # Write the .font file and the corresponding XML metadata file
    write_agon_font(export_config, font_image, file_path)
    save_font_metadata_to_xml(_source_recipe(font_config), config_filepath,
                              bitmap_config=export_config)
    return export_config


def save_png_font(app_reference, font_config, file_path):
    """Save visible atlas pixels and their raster settings without thresholding."""
    export_config = _bitmap_export_config(font_config, file_path)
    app_reference.image_display.working_image.save(file_path, format="PNG")
    save_font_metadata_to_xml(_source_recipe(font_config), f'{file_path}.xml',
                              bitmap_config=export_config)
    return export_config

def save_rgba2_font(app_reference, font_config, file_path):
    """Save the font configuration to an Agon font file."""
    font_image = app_reference.image_display.working_image
    config_filepath = f'{file_path}.xml'
    # # Update font_config with the modified dimensions
    # font_config.update({
    #     'original_font_path': file_path,
    #     'font_width': font_config['font_width_mod'],
    #     'font_height': font_config['font_height_mod'],
    #     'offset_left': 0,
    #     'offset_top': 0,
    #     'offset_width': 0,
    #     'offset_height': 0,
    #     'scale_width': 0,
    #     'scale_height': 0,
    #     'raster_type': 'palette',
    # })
    # Write the .rgba2 file and the corresponding XML metadata file
    write_rgba2_font(font_config, font_image, file_path)
    save_font_metadata_to_xml(_source_recipe(font_config), config_filepath)
    return font_config

def get_save_filename(app_reference):
    """Open a save file dialog with a default filename and automatically append the correct extension."""
    # Retrieve the most recent save directory from app configuration XML
    most_recent_save_directory = get_app_config_value("most_recent_save_directory")
    font_config = app_reference.font_config_editor.get_config()
    base_filename = make_filename_from_config(font_config)

    # A one-bit .font cannot retain quantized gray levels or palette colors.
    default_type = "font" if font_config['raster_type'] == 'threshold' else "png"
    formats = [
        ("font", "Agon Font Files (monochrome)"),
        ("png", "PNG Font Atlas (preserve shades and colors)"),
        ("rgba2", "RGBA2 Font Files"),
        ("xml", "XML Font Config"),
    ]
    formats.sort(key=lambda item: item[0] != default_type)
    type_variable = StringVar(master=app_reference.master, value=formats[0][1])
    filetypes = [(label, f"*.{kind}") for kind, label in formats]
    filetypes.append(("All Files", "*.*"))
    
    # Open file dialog to select a font file with a default filename
    file_path = filedialog.asksaveasfilename(
        title="Save File",
        filetypes=filetypes,
        initialdir=most_recent_save_directory,
        initialfile=base_filename,
        # Let Tk derive the extension from the active filter. A fixed value
        # would keep appending .png even after selecting the monochrome filter.
        defaultextension="",
        typevariable=type_variable,
        parent=app_reference.master,
    )

    # If the user cancels the dialog, return None
    if not file_path:
        return None, None, None

    # An explicit supported extension wins. Otherwise use the actual selected
    # filter, rather than interpreting the entire extensionless path as a type.
    selected_filetype = os.path.splitext(file_path)[1].lstrip('.').lower()
    if selected_filetype not in {kind for kind, _ in formats}:
        selected_filetype = {label: kind for kind, label in formats}.get(type_variable.get(), default_type)
        file_path += f".{selected_filetype}"

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
    font_variant = font_config.get('font_variant', '')
    font_width = font_config.get('font_width_mod', None)
    font_height = font_config.get('font_height_mod', None)

    # Construct the filename step by step
    filename_parts = [font_name]

    # Add font_variant if it's not None or empty
    if font_variant:
        filename_parts.append(font_variant)

    # Add width and height only if both are present
    if font_width is not None and font_height is not None:
        filename_parts.append(f"{font_width}x{font_height}")

    # Join parts with underscores
    return "_".join(filename_parts)

def compute_relative_path(from_path, to_path):
    """
    Compute the relative path from 'from_path' to 'to_path'.
    
    Parameters:
    - from_path (str): The starting file path.
    - to_path (str): The target file path.
    
    Returns:
    - str: The relative path from 'from_path' to 'to_path'.
    """
    # Get the directory names of the input paths
    from_dir = os.path.dirname(from_path)
    to_dir = os.path.dirname(to_path)

    # Compute the relative path
    relative_path = os.path.relpath(to_dir, start=from_dir)

    # Include the target file in the result
    relative_path = os.path.join(relative_path, os.path.basename(to_path))

    return relative_path
