import os
import tkinter as tk
from tkinter import ttk
from config_manager import read_xml_file, xml_element_to_dict
from custom_widgets import DeltaControl

class FontConfigEditor(ttk.Frame):
    """
    A dynamic editor for font configurations, creating controls based on configuration types.
    """
    def __init__(self, parent, config, delta_control_config, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.config = config  # The flattened configuration dictionary
        self.delta_control_config = delta_control_config
        self.canvas = tk.Canvas(self, borderwidth=0, background="#ffffff")
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.create_widgets()

        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def create_widgets(self):
        """
        Create DeltaControls for numeric settings and Entry widgets for string settings.
        """
        row = 0
        for key, value in self.config.items():
            if isinstance(value, (int, float)):
                # Make a copy of delta_control_config for the current control
                control_config = self.delta_control_config.copy()
                
                # Update control_config with specific values for the current DeltaControl
                control_config['label']['text'] = key.replace('_', ' ').capitalize()
                control_config['value']['initial'] = value
                control_config['value']['data_type'] = "int" if isinstance(value, int) else "float"

                # Create DeltaControl with the updated config
                control = DeltaControl(
                    self.scrollable_frame,
                    config=control_config,
                    callback=lambda v, k=key: self.update_config(k, v)
                )
                control.grid(row=row, column=0, pady=0, padx=10, sticky="w")

            elif isinstance(value, str):
                label = ttk.Label(self.scrollable_frame, text=key.replace('_', ' ').capitalize())
                label.grid(row=row, column=0, pady=0, padx=10, sticky="w")

                entry_var = tk.StringVar(value=value)
                entry = ttk.Entry(self.scrollable_frame, textvariable=entry_var, width=25)
                entry.grid(row=row, column=1, pady=0, padx=10, sticky="w")
                entry.bind("<FocusOut>", lambda e, k=key, var=entry_var: self.update_config(k, var.get()))

            row += 1

    def update_config(self, key, value):
        """
        Update the configuration dictionary with the new value from the controls.
        """
        self.config[key] = value
        print(f"Updated {key} to {value}")

# Main testing block
if __name__ == "__main__":
    import os
    import tkinter as tk
    from config_manager import gather_includes, save_combined_xml, read_xml_file, xml_element_to_dict, save_dict_as_text, flatten_config
    from font_config_editor import FontConfigEditor

    # Define paths for configuration files
    config_directory = 'examples/fonts/editor2/data'
    config_filename = 'cfg.font.type.ttf.xml'
    config_filepath = os.path.join(config_directory, config_filename)
    combined_xml_filepath = os.path.join(config_directory, 'combined_config.xml')
    combined_python_filepath = os.path.join(config_directory, 'combined_config.py')
    delta_control_config_path = os.path.join(config_directory, 'cfg.ui.delta_control.xml')

    # Gather includes and save the combined XML to the specified path
    loaded_files = gather_includes(config_filepath)
    save_combined_xml(loaded_files, combined_xml_filepath)

    # Parse the assembled XML back to a dictionary and flatten it
    full_xml = read_xml_file(combined_xml_filepath)[0]
    config_dict = xml_element_to_dict(full_xml)
    flattened_config = flatten_config(config_dict)

    # Save the flattened configuration dictionary to a .py file for reference
    save_dict_as_text(f'{combined_python_filepath}.flat.py', flattened_config)

    # Load DeltaControl configuration from XML for dynamic widgets
    delta_control_xml = read_xml_file(delta_control_config_path)[0]
    delta_control_config = xml_element_to_dict(delta_control_xml)

    # Initialize and run the Tkinter application
    root = tk.Tk()
    root.title("Font Configuration Editor")

    # Initialize FontConfigEditor with the full flattened configuration and DeltaControl config
    editor = FontConfigEditor(root, flattened_config, delta_control_config)
    editor.pack(fill="both", expand=True)

    root.mainloop()
