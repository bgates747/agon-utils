# import os

# def rename_png_files(base_dir):
#     for root, dirs, files in os.walk(base_dir):
#         for file in files:
#             if file.endswith(".png"):
#                 # Determine the font name and variant based on directory structure
#                 path_parts = os.path.normpath(root).split(os.sep)
                
#                 # Check that there are enough directories above to get font name and variant
#                 if len(path_parts) >= 2:
#                     font_name = path_parts[-2]
#                     font_variant = path_parts[-1]

#                     # Construct the new filename
#                     original_path = os.path.join(root, file)
#                     filename_parts = file.split('_')
#                     dimensions = filename_parts[-1]
#                     new_filename = f"{font_name}_{font_variant}_{dimensions}"

#                     # Rename the file
#                     new_path = os.path.join(root, new_filename)
#                     os.rename(original_path, new_path)
#                     print(f"Renamed '{original_path}' to '{new_path}'")
#                 else:
#                     print(f"Skipping '{file}': Insufficient directory depth")

# def delete_txt_ini_in_leaf_dirs(base_dir):
#     for root, dirs, files in os.walk(base_dir):
#         # Check if the directory has no subdirectories (i.e., a leaf directory)
#         if not dirs:
#             for file in files:
#                 if file.endswith(".txt") or file.endswith(".ini"):
#                     file_path = os.path.join(root, file)
#                     os.remove(file_path)
#                     print(f"Deleted '{file_path}'")

# # Specify the base directory to start the scan
# base_dir = "examples/fonts/editor/fonts/ttf"

# # rename_png_files(base_dir)

# delete_txt_ini_in_leaf_dirs(base_dir)

# import os
# import shutil

# # Source directory containing the files
# source_dir = '/home/smith/Agon/mystuff/mac'

# # Loop through each file in the source directory
# for filename in os.listdir(source_dir):
#     # Construct full file path
#     file_path = os.path.join(source_dir, filename)

#     # Skip directories, process only files
#     if os.path.isfile(file_path):
#         # Extract the file extension, skipping if no extension
#         file_extension = os.path.splitext(filename)[1].lower()
#         if not file_extension:
#             continue  # Skip files without an extension

#         # Define the target directory based on the file extension
#         target_dir = os.path.join(source_dir, file_extension[1:])  # Remove the leading dot

#         # Create the directory if it doesn't exist
#         os.makedirs(target_dir, exist_ok=True)

#         # Move the file to the new directory
#         shutil.move(file_path, os.path.join(target_dir, filename))

# print("Files organized by extension!")

import os
from fontTools.ttLib import TTCollection

# Directory containing the .ttc files
source_dir = '/home/smith/Agon/mystuff/mac/ttc'

# Loop through each .ttc file in the source directory
for filename in os.listdir(source_dir):
    # Process only .ttc files
    if filename.endswith('.ttc'):
        ttc_path = os.path.join(source_dir, filename)
        base_name = os.path.splitext(filename)[0]

        # Create a new directory with the base name of the .ttc file
        target_dir = os.path.join(source_dir, base_name)
        os.makedirs(target_dir, exist_ok=True)

        # Open the .ttc file
        ttc = TTCollection(ttc_path)

        # Extract each font in the collection as a separate .ttf
        for i, font in enumerate(ttc.fonts):
            ttf_filename = f"{base_name}_{i+1}.ttf"
            ttf_path = os.path.join(target_dir, ttf_filename)
            font.save(ttf_path)

        print(f"Extracted {len(ttc.fonts)} .ttf files from {filename} into {target_dir}")

print("Extraction completed!")
