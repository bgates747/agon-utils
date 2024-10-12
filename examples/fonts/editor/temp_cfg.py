import configparser
import os
import glob

def create_specific_cfg(template_cfg, specific_ini, output_cfg):
    """Generates a specific .cfg file based on the template and a given .ini file."""
    # Load the template data/fontmeta.cfg
    template = configparser.ConfigParser()
    template.read(template_cfg)
    
    # Load the specific .ini file
    specific = configparser.ConfigParser()
    specific.read(specific_ini)

    # Prepare the output .cfg file based on the template
    output = configparser.ConfigParser()

    # Track any missing entries to be added to the template as comments
    missing_entries = []

    # Process each option in the [font] section of the .ini file
    if specific.has_section("font"):
        for option, value in specific["font"].items():
            if template.has_section(option):
                # Copy the section to output and set the default to the specific value
                output.add_section(option)
                for key, template_value in template[option].items():
                    output.set(option, key, template_value)
                output.set(option, 'default', value)
            else:
                # Add as a new section to output and mark as missing in the template
                output.add_section(option)
                output.set(option, 'type', 'string')  # Default type as 'string'
                output.set(option, 'default', value)
                missing_entries.append(f"[{option}] section added from {specific_ini}")

    # Write the specific output .cfg file
    with open(output_cfg, 'w') as configfile:
        output.write(configfile)
    print(f"Generated {output_cfg} based on {template_cfg} and {specific_ini}")

    # Append missing entries to the template if there are any
    if missing_entries:
        with open(template_cfg, 'a') as template_file:
            template_file.write("\n# Missing entries added from specific .ini files\n")
            for entry in missing_entries:
                template_file.write(f"{entry}\n")
        print(f"Appended missing entries to {template_cfg}")

# Main function to process all font_*.ini files
def process_all_ini_files(directory, template_cfg):
    ini_files = glob.glob(os.path.join(directory, "font_*.ini"))

    for ini_file in ini_files:
        output_cfg = ini_file.replace(".ini", ".cfg")
        create_specific_cfg(template_cfg, ini_file, output_cfg)

# Run the function
if __name__ == "__main__":
    directory = "examples/fonts/editor/"  # Directory to scan for .ini files
    # Delete all font_*.cfg files in the directory
    cfg_files = glob.glob(os.path.join(directory, "font_*.cfg"))
    for cfg_file in cfg_files:
        os.remove(cfg_file)
        template_cfg_path = os.path.join(directory, "data/fontmeta.cfg")  # Path to template data/fontmeta.cfg

    process_all_ini_files(directory, template_cfg_path)
