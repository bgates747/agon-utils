import xml.etree.ElementTree as ET
from config_manager import save_font_metadata_to_xml

if __name__ == "__main__":
    # Your current parameters
    settings = {
        'font_filename': 'Apple Chancery_Narrow_16x32.font',
        'screen_mode': 19,
        'asm_dir': 'examples/font_editor/src/asm',
        'asm_file': 'app.asm',
        'tgt_bin_dir': 'examples/font_editor/tgt',
        'tgt_bin_file': 'font.bin',
        'emulator_dir': '/home/smith/Agon/.emulator',
        'emulator_tgt_dir': '/mystuff/agon-utils/examples/font_editor/tgt',
        'sdcard_tgt_dir': '/media/smith/AGON/mystuff/agon-utils/examples/font_editor/tgt',
        'emulator_exec': './fab-agon-emulator',
        'build_fonts': True,
        'assemble': True,
        'copy_emulator': False,
        'copy_sdcard': False,
        'run_emulator': True
    }

    xml_filepath = 'examples/font_editor/src/python/asm_config.xml'
    save_font_metadata_to_xml(settings, xml_filepath)

    xml_filepath = 'examples/font_editor/src/python/asm_config_editor.xml'
    with open(xml_filepath, 'w') as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<settings>\n')

        for key, value in settings.items():
            print(f"{key}: {value}")

            xml_string = f"""
            <setting name="{key}">
                <widget_type>FontConfigTextBox</widget_type>
                <label_text></label_text>
                <data_type>string</data_type>
                <default_value>{value}</default_value>
                <description></description>
                <event_handlers>
                    <on_change>
                        <item>default_on_change_handler</item>
                        <!-- <item>{key}_on_change_handler</item> -->
                    </on_change>
                    <on_hover>
                        <item>default_on_mouse_enter</item>
                    </on_hover>
                </event_handlers>
            </setting>
            """
            f.write(xml_string)

        f.write('</settings>\n')