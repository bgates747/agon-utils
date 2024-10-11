import subprocess
import time
import tkinter as tk
from Xlib import display
from Xlib.ext import randr

# Step 1: Launch the emulator process
emulator_path = "/usr/local/bin/fab-agon-emulator"  # Adjust path as necessary
process = subprocess.Popen([emulator_path])
time.sleep(2)  # Allow some time for the window to initialize

# Step 2: Get screen and window dimensions
# Initialize Tkinter to get screen dimensions
root = tk.Tk()
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.destroy()

# Assuming the emulator starts in 4x scale
original_width = 640  # Replace with actual emulator window content width
original_height = 480  # Replace with actual emulator window content height
scaled_width = original_width * 4
scaled_height = original_height * 4

# Step 3: Calculate the new dimensions to resize to 1:1 pixel ratio
# Adjust for title bar height and borders if necessary
title_bar_height = 30  # This may vary by environment; adjust as needed
border_width = 0  # This may vary as well

# Calculate the new window dimensions to fit the screen
new_width = original_width + (2 * border_width)
new_height = original_height + title_bar_height + (2 * border_width)

# Step 4: Use wmctrl to resize the window (or Xlib)
# Note: Requires `wmctrl` package to be installed on the system
subprocess.call(['wmctrl', '-r', 'fab-agon-emulator', '-e', f'0,0,0,{new_width},{new_height}'])

print("Emulator resized to 1:1 pixel scale.")
