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

import tkinter as tk
from config_manager import get_typed_data

# Create the main window
root = tk.Tk()
root.title("Tkinter Checkbox Example")

# Create a BooleanVar to store the state of the checkbox
checkbox_var = tk.BooleanVar()

# Function to update the checkbox state based on a given boolean
def set_checkbox(value: bool):
    """Sets the checkbox state to the given boolean value."""
    checkbox_var.set(value)

# Function to get the current state of the checkbox as a boolean
def get_checkbox() -> bool:
    """Returns the current state of the checkbox as a boolean."""
    return checkbox_var.get()

# Callback function to print the checkbox state when toggled
def on_checkbox_toggle():
    print(f"Checkbox state: {get_checkbox()}")

# Link the callback to the variable change
checkbox_var.trace_add('write', lambda *args: on_checkbox_toggle())

# Create the Checkbutton widget
checkbox = tk.Checkbutton(root, text="Check Me!", variable=checkbox_var)
checkbox.pack(pady=10)

value = get_typed_data("bool","False")
print(value)

# Set initial checkbox state
set_checkbox(value)  # Set the checkbox to checked initially

# Start the Tkinter event loop
root.mainloop()
