from config_manager import read_xml_file, xml_to_dict, dict_to_text

if __name__ == "__main__":
    delta_config_xml = read_xml_file("examples/fonts/editor2/data/cfg.ui.delta_control.xml")
    delta_config_dict = xml_to_dict(delta_config_xml)
    delta_config_text = dict_to_text(delta_config_dict)
    print(delta_config_text)