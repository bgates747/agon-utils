import os

def rename_png_files(base_dir):
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith(".png"):
                # Determine the font name and variant based on directory structure
                path_parts = os.path.normpath(root).split(os.sep)
                
                # Check that there are enough directories above to get font name and variant
                if len(path_parts) >= 2:
                    font_name = path_parts[-2]
                    font_variant = path_parts[-1]

                    # Construct the new filename
                    original_path = os.path.join(root, file)
                    filename_parts = file.split('_')
                    dimensions = filename_parts[-1]
                    new_filename = f"{font_name}_{font_variant}_{dimensions}"

                    # Rename the file
                    new_path = os.path.join(root, new_filename)
                    os.rename(original_path, new_path)
                    print(f"Renamed '{original_path}' to '{new_path}'")
                else:
                    print(f"Skipping '{file}': Insufficient directory depth")

# Specify the base directory to start the scan
base_dir = "examples/fonts/editor/fonts/ttf"
rename_png_files(base_dir)
