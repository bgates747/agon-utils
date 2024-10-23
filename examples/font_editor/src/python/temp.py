import os

# Directory to scan
base_directory = 'examples/font_editor/src/fonts/net/ttf'

def remove_metadata_files(base_directory):
    # Loop through all directories in the base directory
    for dir_name in os.listdir(base_directory):
        dir_path = os.path.join(base_directory, dir_name)
        
        if os.path.isdir(dir_path):
            # Loop through files in the directory
            for file_name in os.listdir(dir_path):
                # Check if the file ends with '_metadata.txt'
                if file_name.endswith('_metadata.txt'):
                    file_path = os.path.join(dir_path, file_name)
                    
                    try:
                        os.remove(file_path)
                        print(f"Deleted: {file_path}")
                    except Exception as e:
                        print(f"Failed to delete {file_path}: {e}")

# Run the function
remove_metadata_files(base_directory)
