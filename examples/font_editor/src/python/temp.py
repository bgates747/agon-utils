# def find_optimal_font_sizes(resolutions, target_aspect_ratio, 
#                             min_char_width, min_char_height, 
#                             max_char_width, max_char_height, 
#                             min_cols, min_rows, max_cols, max_rows):
#     """
#     Finds optimal font sizes for given resolutions based on parameters.

#     :param resolutions: List of tuples (width, height)
#     :param target_aspect_ratio: Target aspect ratio for character width:height
#     :param min_char_width: Minimum character width
#     :param min_char_height: Minimum character height
#     :param max_char_width: Maximum character width
#     :param max_char_height: Maximum character height
#     :param min_cols: Minimum number of columns
#     :param min_rows: Minimum number of rows
#     :param max_cols: Maximum number of columns
#     :param max_rows: Maximum number of rows
#     :return: Dictionary of optimal font sizes for each resolution
#     """
#     optimal_sizes = {}

#     for width, height in resolutions:
#         best_size = None

#         # Iterate over possible character widths
#         for char_width in range(min_char_width, max_char_width + 1):
#             char_height = int(char_width / target_aspect_ratio)

#             # Check if char_height is within the allowed range
#             if not (min_char_height <= char_height <= max_char_height):
#                 continue

#             # Calculate max possible rows and columns for this font size
#             cols = width // char_width
#             rows = height // char_height

#             # Check if within the specified row and column limits
#             if (min_cols <= cols <= max_cols) and (min_rows <= rows <= max_rows):
#                 # Update best size if it provides more characters on screen
#                 if not best_size or (cols * rows > best_size[0] * best_size[1]):
#                     best_size = (cols, rows, char_width, char_height)

#         # Store the best size found for this resolution or use the minimum size as fallback
#         if best_size:
#             optimal_sizes[(width, height)] = best_size
#         else:
#             # Use minimum character size to calculate fallback rows and columns
#             fallback_cols = width // min_char_width
#             fallback_rows = height // min_char_height
#             optimal_sizes[(width, height)] = (fallback_cols, fallback_rows, min_char_width, min_char_height)

#     return optimal_sizes


# if __name__ == "__main__":
#     # Define screen resolutions as tuples (width, height)
#     resolutions = [
#         (320, 240), (512, 384), (640, 240), (640, 480),
#         (800, 600), (1024, 768)
#     ]

#     # Minimum and maximum character dimensions (in pixels)
#     min_char_width, min_char_height = 7, 14
#     target_aspect_ratio = min_char_width / min_char_height

#     # Calculate maximum character dimensions based on scaling factor
#     max_factor = 1024 / 320
#     max_char_width, max_char_height = int(min_char_width * max_factor), int(min_char_height * max_factor)

#     # Minimum and maximum number of rows and columns
#     min_cols, min_rows = 40, 24
#     max_cols, max_rows = 80, 48

#     # Find optimal font sizes for each resolution
#     optimal_font_sizes = find_optimal_font_sizes(
#         resolutions, target_aspect_ratio, min_char_width, min_char_height, 
#         max_char_width, max_char_height, min_cols, min_rows, max_cols, max_rows
#     )

#     # Print results
#     for res, (cols, rows, char_w, char_h) in optimal_font_sizes.items():
#         print(f"Resolution {res[0]}x{res[1]}: {cols} cols x {rows} rows, "
#               f"Character size: {char_w}x{char_h} pixels")


# import tkinter as tk
# from tkinter import ttk

# # Multi-line text string
# data = """
# ; 11    320   240   2     60hz
# ; 139   320   240   2     60hz
# ; 23    512   384   2     60hz
# ; 151   512   384   2     60hz
# ; 6     640   240   2     60hz
# ; 134   640   240   2     60hz
# ; 2     640   480   2     60hz
# ; 130   640   480   2     60hz
# ; 17    800   600   2     60hz
# ; 145   800   600   2     60hz
# ; 18    1024  768   2     60hz
# ; 146   1024  768   2     60hz
# ; 10    320   240   4     60hz
# ; 138   320   240   4     60hz
# ; 22    512   384   4     60hz
# ; 150   512   384   4     60hz
# ; 5     640   240   4     60hz
# ; 133   640   240   4     60hz
# ; 1     640   480   4     60hz
# ; 129   640   480   4     60hz
# ; 16    800   600   4     60hz
# ; 19    1024  768   4     60hz
# ; 9     320   240   16    60hz
# ; 137   320   240   16    60hz
# ; 21    512   384   16    60hz
# ; 149   512   384   16    60hz
# ; 4     640   240   16    60hz
# ; 132   640   240   16    60hz
# ; 0     640   480   16    60hz
# ; 8     320   240   64    60hz
# ; 136   320   240   64    60hz
# ; 20    512   384   64    60hz
# ; 3     640   240   64    60hz
# """

# # Initialize an empty dictionary
# modes_dict = {}

# # Split the data into lines and process each line
# for line in data.splitlines():
#     if not line.strip():
#         continue

#     line = line.lstrip(';').strip()
#     parts = line.split()

#     mode = int(parts[0])
#     horz = int(parts[1])
#     vert = int(parts[2])
#     cols = int(parts[3])
#     refresh = parts[4]

#     # Store only entries with mode <= 127
#     if mode <= 127:
#         modes_dict[mode] = {
#             'Mode': mode,
#             'Horz': horz,
#             'Vert': vert,
#             'Cols': cols,
#             'Refresh': refresh
#         }

# # Convert the dictionary to a list of records for sorting
# records = list(modes_dict.values())

# # Sort the records by 'Horz' (descending), 'Vert' (descending), 'Cols' (descending)
# sorted_records = sorted(records, key=lambda x: (-x['Horz'], -x['Vert'], -x['Cols']))

# # Print the sorted dataset
# for record in sorted_records:
#     print(record)

# # Convert records to a list of mode strings for the combobox
# mode_options = [f"{rec['Mode']}: {rec['Horz']}x{rec['Vert']}x{rec['Cols']}" 
#                 for rec in sorted_records]

# def on_select(event):
#     """Callback for when a mode is selected from the combobox."""
#     selected_mode = combobox.get()
#     print(f"Selected: {selected_mode}")

# # Create the main Tkinter window
# root = tk.Tk()
# root.title("Select Screen Mode")

# # Create a Combobox
# combobox = ttk.Combobox(root, values=mode_options, state="readonly")
# combobox.pack(padx=10, pady=10)

# # Set a default value
# combobox.set("Select a screen mode")

# # Bind the selection event
# combobox.bind("<<ComboboxSelected>>", on_select)

# # Start the Tkinter event loop
# root.mainloop()

import os

def compute_relative_path(from_path, to_path):
    """
    Compute the relative path from 'from_path' to 'to_path'.
    
    Parameters:
    - from_path (str): The starting file path.
    - to_path (str): The target file path.
    
    Returns:
    - str: The relative path from 'from_path' to 'to_path'.
    """
    # Get the directory names of the input paths
    from_dir = os.path.dirname(from_path)
    to_dir = os.path.dirname(to_path)

    # Compute the relative path
    relative_path = os.path.relpath(to_dir, start=from_dir)

    # Include the target file in the result
    relative_path = os.path.join(relative_path, os.path.basename(to_path))

    return relative_path

# Example usage
from_path = '/home/smith/Agon/emulator/sdcard/mystuff/agon-utils/examples/font_editor/src/fonts/mac/ttf/Arial Black.ttf'
to_path = '/home/smith/Agon/emulator/sdcard/mystuff/agon-utils/examples/font_editor/tgt/arial_black.rgba2'

relative_path = compute_relative_path(from_path, to_path)
print(f"Relative path from '{from_path}' to '{to_path}': {relative_path}")
