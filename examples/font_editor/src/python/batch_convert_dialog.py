
from config_editor_dialog import ConfigEditorDialog

class BatchConvertDialog(ConfigEditorDialog):
    """
    A modal dialog for batch conversion that includes the font configuration dictionary.
    """
    def __init__(self, parent, config_editor_file, app_reference, last_config, *args, **kwargs):
        last_config_filepath = 'examples/font_editor/src/python/batch_convert_values.xml'
        self.last_config = last_config
        super().__init__(parent, config_editor_file, app_reference, *args, **kwargs)

    def init_values(self):
        """Initialize values based on the font configuration."""
        font_filepath = self.font_config['original_font_path']

    def on_set(self):
        """Handle the Set button click."""
        print("Set button pressed")
        self.destroy()

    def on_cancel(self):
        """Handle the Cancel button click."""
        print("Cancel button pressed")
        self.destroy()

    def on_go(self):
        """Handle the GO button click."""
        print("GO button pressed")
        self.destroy()