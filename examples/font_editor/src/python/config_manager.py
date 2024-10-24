import xml.etree.ElementTree as ET
from xml.dom import minidom
import json
import os

# def get_typed_data(data_type, value):
#     if data_type == 'int':
#         return int(value)
#     elif data_type == 'float':
#         return float(value)
#     elif data_type == 'string':
#         return str(value)
#     elif data_type == 'bool':
#         return bool(value)
#     return value

def get_typed_data(data_type, value):
    """
    Converts the value to the specified data type.
    """
    if data_type == 'bool':
        return value.lower() in ('true', '1')
    elif data_type == 'int':
        return int(value)
    elif data_type == 'float':
        return float(value)
    else:  # default to string
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

def xml_to_dict(font_config_xml, general_config_xml):
    """
    Convert XML settings from ElementTree Elements to a dictionary with typed data,
    using a general config XML element to look up data types.
    
    Parameters:
        font_config_xml (ET.Element): Parsed XML element of the individual font config.
        general_config_xml (ET.Element): Parsed XML element of the general config specifying data types.
    
    Returns:
        dict: Dictionary containing settings with appropriate data types.
    """
    settings_dict = {}
    
    # Function to find the data type in the general config
    def find_data_type(setting_name):
        element = general_config_xml.find(f".//setting[@name='{setting_name}']")
        return element.find("data_type").text if element is not None else None

    # Process each setting in the font config XML
    for setting in font_config_xml.findall("setting"):
        name = setting.get("name")
        value = setting.get("value")

        # Look up the data type in the general config
        data_type = find_data_type(name)

        # Convert the value using the found data type, default to string if not found
        typed_value = get_typed_data(data_type, value) if data_type else value
        settings_dict[name] = typed_value

    return settings_dict

def get_xml_value(file_name, element_name, tag_name):
    """
    Retrieve the value of a specified tag within an element from an XML file.
    Handles cases where the element_name is the root tag.
    
    Parameters:
        file_name (str): Filename to the XML file relative to application file location.
        element_name (str): Name of the element to search, or the root tag.
        tag_name (str): Name of the tag whose value is to be retrieved.
    
    Returns:
        str: The value of the specified tag, or None if not found.
    """
    file_path = os.path.join(os.path.dirname(__file__), file_name)
    
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()

        # Check if the root tag matches the element_name
        if root.tag == element_name:
            # Look for tag_name directly within the root
            tag = root.find(tag_name)
        else:
            # Look for element_name as a child of the root, then find tag_name within it
            element = root.find(element_name)
            tag = element.find(tag_name) if element is not None else None

        # Return the tag's text if found
        return tag.text if tag is not None else None

    except ET.ParseError:
        print(f"Error: Could not parse XML file {file_path}")
        return None
    except FileNotFoundError:
        print(f"Error: File not found - {file_path}")
        return None

def set_xml_value(file_name, element_name, tag_name, value):
    """
    Set the value of a specified tag within an element in an XML file.
    Handles cases where the element_name is the root tag.
    
    Parameters:
        file_name (str): Filename of the XML file relative to the application file location.
        element_name (str): Name of the element to search, or the root tag.
        tag_name (str): Name of the tag whose value is to be set.
        value (str): The value to set for the specified tag.
    
    Returns:
        bool: True if the operation was successful, False otherwise.
    """
    file_path = os.path.join(os.path.dirname(__file__), file_name)
    
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()

        # Check if the root tag matches the element_name
        if root.tag == element_name:
            # Look for tag_name directly within the root
            tag = root.find(tag_name)
            if tag is None:
                # If the tag doesn't exist, create it
                tag = ET.SubElement(root, tag_name)
            tag.text = value
        else:
            # Look for element_name as a child of the root
            element = root.find(element_name)
            if element is None:
                # If the element doesn't exist, create it
                element = ET.SubElement(root, element_name)
            # Find or create the tag within the element
            tag = element.find(tag_name)
            if tag is None:
                tag = ET.SubElement(element, tag_name)
            tag.text = value

        # Save the updated XML to file
        tree.write(file_path, encoding="utf-8", xml_declaration=True)
        return True

    except ET.ParseError:
        print(f"Error: Could not parse XML file {file_path}")
        return False
    except FileNotFoundError:
        print(f"Error: File not found - {file_path}")
        return False

# =========================================================================
# Application Configuration Handling
# =========================================================================

def get_app_config_value(tag_name):
    """Retrieve a value from the application configuration XML file."""
    return get_xml_value("app_config.xml", "settings", tag_name)

def set_app_config_value(tag_name, value):
    """Set a value in the application configuration XML file."""
    return set_xml_value("app_config.xml", "settings", tag_name, value)

# =========================================================================
# Font Configuration and Metadata Handling
# =========================================================================

def parse_font_filename(file_path):
    """Parse font configuration from a font filename and return as a dictionary."""
    file_name = os.path.basename(file_path)
    base_name, ext = os.path.splitext(file_name)
    
    # Check extensions we do parsing for
    if ext not in {'.png', '.font'}:
        # Return minimal configuration for unsupported file types
        return {
            'font_name': base_name,
            'font_variant': "",
        }
    
    # Parse details from .png or .font file name
    parts = base_name.split('_')
    try:
        dimensions_part = parts[-1]
        width, height = map(int, dimensions_part.split('x'))
    except ValueError:
        print("Warning: Unable to parse width and height from filename.")
        width, height = 0, 0

    font_variant = parts[-2] if len(parts) >= 2 else "Regular"
    font_name = '_'.join(parts[:-2]) if len(parts) > 2 else "unknown_font"

    return {
        'font_name': font_name,
        'font_variant': font_variant,
        'font_width': width,
        'font_height': height,
    }

def load_font_metadata_from_xml(xml_filepath):
    """Load font metadata from an XML file, converting values based on types in the general XML config file."""
    font_config_xml = load_xml(xml_filepath)
    
    # Load general XML config (data types) as parsed XML
    general_config_path = os.path.join(os.path.dirname(__file__), "font_config_editor.xml")
    general_config_xml = load_xml(general_config_path)
    
    # Parse XML settings to a dictionary using xml_to_dict
    font_metadata = xml_to_dict(font_config_xml, general_config_xml)
    
    return font_metadata

def save_font_metadata_to_xml(font_config, xml_filepath):
    """Save font metadata to an XML file based on the provided dictionary with pretty formatting."""
    root = ET.Element("settings")
    
    for key, value in font_config.items():
        setting = ET.SubElement(root, "setting", name=key, value=str(value))
    
    # Convert to a string and pretty-print using minidom
    rough_string = ET.tostring(root, encoding="utf-8")
    reparsed = minidom.parseString(rough_string)
    pretty_xml = reparsed.toprettyxml(indent="  ")

    # Write the pretty-printed XML to the file
    with open(xml_filepath, "w", encoding="utf-8") as f:
        f.write(pretty_xml)

# Load XML file and get root element
def load_xml(xml_filepath):
    """Load an XML file and return the root XML element."""
    try:
        tree = ET.parse(xml_filepath)
        return tree.getroot()
    except FileNotFoundError:
        print(f"Error: Could not find XML file {xml_filepath}")
        return None
    except ET.ParseError:
        print(f"Error: Could not parse XML file {xml_filepath}")
        return None
