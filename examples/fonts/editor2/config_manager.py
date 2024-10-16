import xml.etree.ElementTree as ET
import os

def read_xml_file(file_path, tag=None):
    """
    Extracts specified elements from an XML file. If `tag` is None, returns the full XML root element.
    """
    tree = ET.parse(file_path)
    root = tree.getroot()
    
    # If a specific tag is requested, return a list of elements with that tag
    if tag:
        return [element for element in root.findall(f".//{tag}")]
    
    # If no specific tag is requested, return the full root element directly
    return root

def xml_element_to_dict(element):
    """
    Converts an XML element and its children into a nested dictionary.
    """
    node = {}

    # Add element's attributes to the dictionary
    if element.attrib:
        node.update(element.attrib)

    # Include text content if it exists and is non-empty
    if element.text and element.text.strip():
        node['text'] = element.text.strip()

    # Recursively add child elements
    for child in element:
        child_dict = xml_element_to_dict(child)
        if child.tag not in node:
            node[child.tag] = child_dict
        else:
            # Handle multiple children with the same tag by storing them as a list
            if isinstance(node[child.tag], list):
                node[child.tag].append(child_dict)
            else:
                node[child.tag] = [node[child.tag], child_dict]

    return node

def xml_to_dict(xml_input):
    """
    Converts an XML input (string or Element) to a nested dictionary.
    """
    # If the input is a string, parse it to an Element
    if isinstance(xml_input, str):
        root = ET.fromstring(xml_input)
    else:
        root = xml_input  # Assume it's already an Element
    
    return xml_element_to_dict(root)

def gather_includes(file_path, loaded_files=None):
    """
    Recursively gathers XML content from include files specified by <IncludeFileConfig> elements.
    Only includes child elements of <FontConfig> to avoid nested <FontConfig> tags in the output.
    """
    if loaded_files is None:
        loaded_files = {}

    # Avoid re-processing already loaded files
    if file_path in loaded_files:
        return loaded_files

    # Read and process the main XML file
    base_elements = read_xml_file(file_path)
    loaded_files[file_path] = base_elements

    # Look for <IncludeFileConfig> elements in the base XML file
    include_elements = read_xml_file(file_path, tag="IncludeFileConfig")
    script_dir = os.path.dirname(__file__)

    for include in include_elements:
        # Resolve relative path from the script's directory
        include_filename = include.get('filename')
        if include_filename:
            include_path = os.path.join(script_dir, include_filename)
            if os.path.exists(include_path):
                # Recursively gather includes from the specified file
                gather_includes(include_path, loaded_files)

    return loaded_files

def combine_xml_files(loaded_files, root_tag=None):
    """
    Combines XML elements from multiple files into a single XML structure.
    Returns the combined XML Element, allowing for further processing.
    """
    # Determine the root tag: use provided root_tag or fall back to the first file's root tag
    if root_tag is None:
        first_file_elements = next(iter(loaded_files.values()), None)
        if first_file_elements:
            root_tag = first_file_elements[0].tag
        else:
            raise ValueError("No files found to combine and no root tag specified.")

    combined_root = ET.Element(root_tag)

    # Add child elements from each loaded file, ensuring valid XML with a single root
    for file_elements in loaded_files.values():
        for element in file_elements:
            if element.tag == root_tag:
                # Add only the child elements if the element tag matches the root
                for child in element:
                    combined_root.append(child)
            else:
                # Directly add if the element tag doesn't match the root
                combined_root.append(element)

    # Return the combined XML Element for further use
    return combined_root

def save_xml(file_path, xml_element):
    """
    Saves an entire XML structure to the specified file path.
    
    Parameters:
    - file_path (str): The file path to save the XML.
    - xml_element (Element): The root XML element to be saved as-is.
    """
    tree = ET.ElementTree(xml_element)
    tree.write(file_path, encoding="utf-8", xml_declaration=True)

def dict_to_text(config_dict, indent=0):
    """
    Converts a Python dictionary to a formatted text string with proper indentation.
    """
    text = "config = {\n"
    text += _dict_to_text(config_dict, indent + 4)
    text += "}\n"
    return text

def _dict_to_text(d, indent):
    """
    Helper function to recursively format dictionary contents as a string with indentation.
    """
    text = ""
    for key, value in d.items():
        if isinstance(value, dict):
            text += " " * indent + f"'{key}': {{\n"
            text += _dict_to_text(value, indent + 4)
            text += " " * indent + "},\n"
        elif isinstance(value, list):
            text += " " * indent + f"'{key}': [\n"
            for item in value:
                if isinstance(item, dict):
                    text += " " * (indent + 4) + "{\n"
                    text += _dict_to_text(item, indent + 8)
                    text += " " * (indent + 4) + "},\n"
                else:
                    text += " " * (indent + 4) + f"{repr(item)},\n"
            text += " " * indent + "],\n"
        else:
            text += " " * indent + f"'{key}': {repr(value)},\n"
    return text

def flatten_config(nested_config,target_key, key_attr, value_attr, type_attr):
    """
    Flattens a nested configuration dictionary, extracting specified attributes.
    
    Parameters:
    - nested_config (dict): The nested dictionary to flatten.
    - target_key (str): The key in `nested_config` to process (e.g., 'Setting').
    - key_attr (str): The attribute in each item to use as the dictionary key (e.g., 'name').
    - value_attr (str): The attribute in each item to use as the dictionary value (e.g., 'default').
    - type_attr (str): The attribute to determine the data type for value conversion (e.g., 'type').
    
    Returns:
    - dict: A flattened dictionary with specified keys and default values, converted to appropriate types.
    """
    flat_config = {}

    # Extract the list of settings to process based on target_key
    items = nested_config.get(target_key, [])
    for item in items:
        # Extract the specified key and value attributes
        name = item.get(key_attr)
        default_value = item.get(value_attr)
        data_type = item.get(type_attr)

        # Convert default value to the specified type if possible
        if default_value is not None:
            if data_type == 'int':
                default_value = int(default_value)
            elif data_type == 'float':
                default_value = float(default_value)
            elif data_type == 'bool':
                default_value = default_value.lower() == 'true'
            # Add more conversions as needed

        if name and default_value is not None:
            flat_config[name] = default_value

    return flat_config

# Test function
if __name__ == "__main__":
    config_directory = 'examples/fonts/editor2/data'
    config_filename = 'cfg.font.type.ttf.xml'
    config_filepath = os.path.join(config_directory, config_filename)
    combined_xml_filepath = os.path.join(config_directory, 'combined_config.xml')
    combined_python_filepath = os.path.join(config_directory, 'combined_config.py')

    # Gather includes and combine XML files, specifying the root tag
    loaded_files = gather_includes(config_filepath)
    combined_xml = combine_xml_files(loaded_files, root_tag="FontConfig")

    # Save the combined XML to a file for verification purposes
    save_xml(combined_xml_filepath, combined_xml)

    # Convert the combined XML element directly to a dictionary
    config_dict = xml_element_to_dict(combined_xml)

    # Flatten the configuration dictionary
    flattened_config = flatten_config(config_dict, target_key="Setting", key_attr="name", value_attr="default", type_attr="type")

    # Save the flattened dictionary to a .py file for reference
    config_dict_text = dict_to_text(flattened_config)
    with open(f'{combined_python_filepath}', 'w') as file:
        file.write(config_dict_text)

    # Print confirmation
    print(f"Combined XML saved to: {combined_xml_filepath}")
    print(f"Configuration dictionary saved to: {combined_python_filepath}")
