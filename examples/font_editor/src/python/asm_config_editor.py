
from build_99_asm_assemble import build_and_deploy_fonts
from config_editor_dialog import ConfigEditorDialog
from config_manager import get_app_config_value
import os

class DoAssemblyDialog(ConfigEditorDialog):
    """
    A modal dialog for assembly configuration that includes the font configuration dictionary.
    """
    def __init__(self, parent, config_editor_file, app_reference, font_config, *args, **kwargs):
        self.font_config = font_config
        font_filepath = get_app_config_value("most_recent_file")
        self.font_filename = os.path.basename(font_filepath)
        super().__init__(parent, config_editor_file, app_reference, *args, **kwargs)

    def init_values(self):
        """Initialize values based on the font configuration."""
        self.editor.controls['font_filename'].value = self.font_filename

    def on_go(self):
        """Handle the GO button click by running the build_and_deploy_fonts function."""
        print("GO button pressed")

        # Extract the current configuration values from the form
        kwargs = self.editor.get_config()

        # Call the build_and_deploy_fonts function with the extracted configuration
        build_and_deploy_fonts(**kwargs)

        # Close the dialog after triggering the build
        self.destroy()

