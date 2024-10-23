import os
import xml.etree.ElementTree as ET

# Directory to scan
directory = 'examples/font_editor/tgt'

def check_font_paths(directory):
    # Loop through all files in the directory
    for filename in os.listdir(directory):
        if filename.endswith('.xml'):
            xml_path = os.path.join(directory, filename)
            
            try:
                # Parse the XML file
                tree = ET.parse(xml_path)
                root = tree.getroot()

                # Find the 'original_font_path' setting
                setting = root.find(".//setting[@name='original_font_path']")
                
                if setting is not None:
                    font_path = setting.get('value')
                    
                    # Check if the file exists
                    if not os.path.exists(font_path):
                        print(f"File not found: {font_path} (in {xml_path})")
            
            except ET.ParseError:
                print(f"Failed to parse XML file: {xml_path}")

# Run the function
check_font_paths(directory)
