
from config_editor_dialog import ConfigEditorDialog
from config_manager import save_values_dict_to_xml

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
        self.destroy()