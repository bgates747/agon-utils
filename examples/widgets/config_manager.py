import xml.etree.ElementTree as ET
import json

def get_typed_data(data_type, value):
    if data_type == 'int':
        return int(value)
    elif data_type == 'float':
        return float(value)
    elif data_type == 'string':
        return str(value)
    return value

def dict_to_text(data_dict):
    """Return a nicely formatted string version of the dictionary, suitable for console printing or pasting into code."""
    return json.dumps(data_dict, indent=4, sort_keys=False)


def dict_to_xml(data_dict, root_tag):
    """
    Convert a dictionary to an XML ElementTree structure with a specified root tag.

    Parameters:
        data_dict (dict): The dictionary to convert.
        root_tag (str): The tag name for the XML root element.

    Returns:
        ET.Element: The root XML element representing the dictionary structure.
    """
    root = ET.Element(root_tag)

    def build_xml_element(element, data):
        if isinstance(data, dict):
            for key, value in data.items():
                child = ET.SubElement(element, key)
                build_xml_element(child, value)
        elif isinstance(data, list):
            for item in data:
                item_element = ET.SubElement(element, "item")
                build_xml_element(item_element, item)
        else:
            element.text = str(data)

    build_xml_element(root, data_dict)
    return root