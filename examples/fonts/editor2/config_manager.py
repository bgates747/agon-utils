import xml.etree.ElementTree as ET
import os

def read_xml_file(file_path, tag=None):
    """
    Extracts specified elements from an XML file. If `tag` is None, returns the full XML structure.
    Returns elements in XML format.
    """
    tree = ET.parse(file_path)
    root = tree.getroot()
    
    # If a specific tag is requested, return a list of elements with that tag
    if tag:
        return [element for element in root.findall(f".//{tag}")]
    
    # If no specific tag is requested, return the full root element
    return [root]

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

def save_combined_xml(loaded_files, output_path):
    """
    Combines XML elements from multiple files into a single XML structure and saves to output_path.
    """
    combined_root = ET.Element("FontConfig")

    # Flatten structure: add only child elements of each root's <FontConfig> children
    for file_elements in loaded_files.values():
        for element in file_elements:
            for child in element:
                combined_root.append(child)

    # Save the combined XML to the specified output path
    tree = ET.ElementTree(combined_root)
    tree.write(output_path, encoding="utf-8", xml_declaration=True)

def save_dict_as_text(file_path, config_dict, indent=0):
    """
    Saves a Python dictionary as a formatted text file with proper indentation.
    """
    with open(file_path, 'w') as file:
        file.write("config = {\n")
        _write_dict(config_dict, file, indent + 4)
        file.write("}\n")

def _write_dict(d, file, indent):
    """
    Helper function to recursively write dictionary contents with indentation.
    """
    for key, value in d.items():
        if isinstance(value, dict):
            file.write(" " * indent + f"'{key}': {{\n")
            _write_dict(value, file, indent + 4)
            file.write(" " * indent + "},\n")
        elif isinstance(value, list):
            file.write(" " * indent + f"'{key}': [\n")
            for item in value:
                if isinstance(item, dict):
                    file.write(" " * (indent + 4) + "{\n")
                    _write_dict(item, file, indent + 8)
                    file.write(" " * (indent + 4) + "},\n")
                else:
                    file.write(" " * (indent + 4) + f"{repr(item)},\n")
            file.write(" " * indent + "],\n")
        else:
            file.write(" " * indent + f"'{key}': {repr(value)},\n")

def flatten_config(
    nested_config,
    target_key="Setting",
    key_attr="name",
    value_attr="default",
    type_attr="type"
):
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

    # Gather includes and save the combined XML to the specified path
    loaded_files = gather_includes(config_filepath)
    save_combined_xml(loaded_files, combined_xml_filepath)

    # Parse the assembled XML back to a dictionary
    full_xml = read_xml_file(combined_xml_filepath)[0]
    config_dict = xml_element_to_dict(full_xml)

    flattened_config = flatten_config(config_dict)

    # Save the parsed dictionary to a .py file
    save_dict_as_text(f'{combined_python_filepath}.flat.py', flattened_config)

    # Print confirmation
    print(f"Combined XML saved to: {combined_xml_filepath}")
    print(f"Configuration dictionary saved to: {combined_python_filepath}")
