import xml.etree.ElementTree as ET

class FontConfigWidget:
    @staticmethod
    def _extract_nested_dict(setting_xml, tag_name):
        """Extract nested dictionary structure from XML for a given tag."""
        def recurse_element(element):
            nested_dict = {}
            for child in element:
                if len(child):
                    nested_dict[child.tag] = recurse_element(child)
                else:
                    if child.tag in nested_dict:
                        if isinstance(nested_dict[child.tag], list):
                            nested_dict[child.tag].append(child.text)
                        else:
                            nested_dict[child.tag] = [nested_dict[child.tag], child.text]
                    else:
                        nested_dict[child.tag] = child.text if len(element.findall(child.tag)) == 1 else [child.text]
            return nested_dict

        tag_xml = setting_xml.find(tag_name) if setting_xml is not None else None
        return recurse_element(tag_xml) if tag_xml is not None else {}

# Sample XML configuration in memory
font_config_xml = """
<settings>
    <setting name="palette">
        <widget_type>ConfigComboBox</widget_type>
        <label_text>Palette</label_text>
        <data_type>string</data_type>
        <default_value>Agon64</default_value>
        <options>
            <value>Agon64</value>
            <value>Agon16</value>
            <value>Agon4</value>
            <value>32-bit RGBA</value>
        </options>
        <description>Color Palette</description>
        <visible>
            <setting name="raster_type">
                <list>palette</list>
            </setting>
        </visible>
        <event_handlers>
            <on_change>
                <handler>default</handler>
                <handler>foo_handler</handler>
                <handler>bar_handler</handler>
                <handler>baz_handler</handler>
                <handler>qux_handler</handler>
                <handler>quux_handler</handler>
                <handler>kludge_handler</handler>
            </on_change>
        </event_handlers>
    </setting>
</settings>
"""

# Parse the XML
config_xml = ET.fromstring(font_config_xml)
setting_xml = config_xml.find(".//setting[@name='palette']")

# Extract nested dictionaries for 'visible', 'event_handlers', and 'options'
visible_dict = FontConfigWidget._extract_nested_dict(setting_xml, 'visible')
event_handlers_dict = FontConfigWidget._extract_nested_dict(setting_xml, 'event_handlers')
options_dict = FontConfigWidget._extract_nested_dict(setting_xml, 'options')

# Print the resulting dictionaries
print("Visible Dictionary:")
print(visible_dict)
print("\nEvent Handlers Dictionary:")
print(event_handlers_dict)
print("\nOptions Dictionary:")
print(options_dict)
