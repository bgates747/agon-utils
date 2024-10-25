
from config_editor_dialog import ConfigEditorDialog
from config_manager import save_values_dict_to_xml, generate_blank_font_config, update_dict_from_dict
from agon_font import read_font, write_agon_font, save_font_metadata_to_xml
import os

class BatchConvertDialog(ConfigEditorDialog):
    """
    A modal dialog for batch conversion that includes the font configuration dictionary.
    """
    def __init__(self, parent, config_editor_file, app_reference, values_dict, xml_values_filepath, *args, **kwargs):
        self.values_dict = values_dict
        self.xml_values_filepath = xml_values_filepath
        super().__init__(parent, config_editor_file, app_reference, *args, **kwargs)

    def init_values(self):
        """Initialize values based on the font configuration."""
        self.editor.set_controls_from_config(self.values_dict)

    def on_set(self):
        """Handle the Set button click."""
        self.values_dict = self.editor.get_config()
        save_values_dict_to_xml(self.values_dict, self.xml_values_filepath)

    def on_cancel(self):
        """Handle the Cancel button click."""
        print("Cancel button pressed")
        self.destroy()

    def on_go(self):
        """Handle the GO button click."""
        print("GO button pressed")
        self.values_dict = self.editor.get_config()
        font_tgt_dir = self.values_dict['font_tgt_dir']
        if not os.path.exists(font_tgt_dir):
            os.makedirs(font_tgt_dir)
        file_paths = generate_file_list(self.values_dict)
        for file_path in file_paths:
            font_config = generate_blank_font_config()
            font_config = update_dict_from_dict(self.values_dict, font_config)
            font_config['original_font_path'] = file_path
            font_config, font_image = read_font(file_path, font_config)
            font_config.update({
                'font_variant': '',
                'font_width_mod': font_config['font_width'], 
                'font_height_mod': font_config['font_height'],
                })
            tgt_png_filename = f"{os.path.splitext(os.path.basename(file_path))[0]}.png"
            font_image.save(os.path.join(font_tgt_dir, tgt_png_filename))
            tgt_font_filename = f"{os.path.splitext(os.path.basename(file_path))[0]}.font"
            tgt_font_filepath = os.path.join(font_tgt_dir, tgt_font_filename)
            write_agon_font(font_config, font_image, tgt_font_filepath)
            tgt_xml_filepath = f"{tgt_font_filepath}.xml"
            save_font_metadata_to_xml(font_config, tgt_xml_filepath)
            self.destroy()

def generate_file_list(batch_convert_dict):
    """
    Generates a list of font files to process based on the given batch conversion dictionary.

    :param batch_convert_dict: Dictionary containing batch conversion settings.
    :return: List of files matching the criteria.
    """
    font_src_dir = batch_convert_dict['font_src_dir']
    recursive = batch_convert_dict['recursive']
    ttf = batch_convert_dict['ttf']
    otf = batch_convert_dict['otf']
    psf = batch_convert_dict['psf']

    file_list = []

    # Define the file extensions to look for
    file_extensions = []
    if ttf:
        file_extensions.append('.ttf')
    if otf:
        file_extensions.append('.otf')
    if psf:
        file_extensions.append('.psf')

    # Walk through the directory (recursively or not)
    for root, _, files in os.walk(font_src_dir):
        if not recursive and root != font_src_dir:
            continue

        for file in files:
            if any(file.endswith(ext) for ext in file_extensions):
                file_list.append(os.path.join(root, file))

    file_list.sort()
    return file_list