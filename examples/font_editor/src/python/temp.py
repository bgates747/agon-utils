from config_manager import dict_to_text, get_typed_data, xml_to_dict, load_xml
import xml.etree.ElementTree as ET
from xml.dom import minidom

def xml_defaults_to_dict(xml_defaults_filepath):
    """
    Reads an XML file of settings and returns a dictionary where the key is the setting's 'name'
    attribute and the value is the 'default_value' element.

    :param xml_defaults_filepath: Path to the XML settings file.
    :return: Dictionary with setting names as keys and default values as values.
    """
    settings_dict = {}

    tree = ET.parse(xml_defaults_filepath)
    root = tree.getroot()

    # Iterate through each <setting> element under <settings>
    for setting in root.findall('setting'):
        setting_name = setting.get('name')
        if not setting_name:
            continue

        # Find the <default_value> element
        data_type = setting.findtext('data_type', 'string').strip()
        default_value = setting.findtext('default_value', '').strip()
        default_value = get_typed_data(data_type, default_value)

        # Add to dictionary
        settings_dict[setting_name] = default_value

    return settings_dict


def dict_to_xml_defaults(values_dict, xml_defaults_filepath):
    """
    Updates the <default_value> elements in an XML defaults file based on the provided flat dictionary.
    If a key in values_dict is not found in the XML, a warning is logged.

    :param values_dict: Flat dictionary containing settings with their new values.
    :param xml_defaults_filepath: Path to the XML file to be updated.
    """
    try:
        # Parse the existing XML file
        tree = ET.parse(xml_defaults_filepath)
        root = tree.getroot()

        found_keys = set()

        # Iterate through each <setting> element in the XML
        for setting in root.findall('setting'):
            setting_name = setting.get('name')

            # If the setting is in the values dictionary, update the <default_value>
            if setting_name in values_dict:
                found_keys.add(setting_name)

                # Find the <default_value> element and update it
                default_value_elem = setting.find('default_value')
                if default_value_elem is not None:
                    # Get current data type to ensure correct type conversion
                    data_type = setting.findtext('data_type', 'string').strip()
                    new_value = get_typed_data(data_type, values_dict[setting_name])
                    default_value_elem.text = str(new_value)

        # Log warnings for any keys in values_dict that were not found in the XML
        for key in values_dict:
            if key not in found_keys:
                print(f"Warning: Setting '{key}' not found in the defaults XML. Attempted value: {values_dict[key]}")

        # Write the updated XML back to the file, preserving the original structure
        tree.write(xml_defaults_filepath, encoding="utf-8", xml_declaration=True)
        print(f"Defaults XML updated successfully at {xml_defaults_filepath}")

    except ET.ParseError as e:
        print(f"Error parsing XML file: {e}")
    except Exception as e:
        print(f"Error updating XML file: {e}")


def xml_values_to_dict(xml_defaults_filepath, xml_values_filepath):
    """Load font metadata from an XML file, converting values based on types in the general XML config file."""
    values_dict_xml = load_xml(xml_values_filepath)
    defaults_dict = load_xml(xml_defaults_filepath)
    
    # Parse XML settings to a dictionary using xml_to_dict
    values_dict = xml_to_dict(values_dict_xml, defaults_dict)
    
    return values_dict

def save_values_dict_to_xml(values_dict, xml_values_filepath):
    """Save font metadata to an XML file based on the provided dictionary with pretty formatting."""
    root = ET.Element("settings")
    
    for key, value in values_dict.items():
        setting = ET.SubElement(root, "setting", name=key, value=str(value))
    
    # Convert to a string and pretty-print using minidom
    rough_string = ET.tostring(root, encoding="utf-8")
    reparsed = minidom.parseString(rough_string)
    pretty_xml = reparsed.toprettyxml(indent="  ")
    # Write the pretty-printed XML to the file
    with open(xml_values_filepath, "w", encoding="utf-8") as f:
        f.write(pretty_xml)

if __name__ == "__main__":
    xml_values_filepath = 'examples/font_editor/src/python/batch_convert_values.xml'
    xml_defaults_filepath = 'examples/font_editor/src/python/batch_convert_dialog.xml'

    defaults_dict = xml_defaults_to_dict(xml_defaults_filepath)
    print(dict_to_text(defaults_dict))
    save_values_dict_to_xml(defaults_dict, xml_values_filepath)
    processed_config_dict = xml_values_to_dict(xml_defaults_filepath, xml_values_filepath)
    processed_config_dict['recursive'] = False
    print(dict_to_text(processed_config_dict))
    save_values_dict_to_xml(processed_config_dict, xml_values_filepath)