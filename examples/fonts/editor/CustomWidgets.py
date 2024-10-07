
import tkinter as tk
from tkinter import font

class CustomWidgets:
    """Class to hold custom widgets for reusable UI components."""

    class ZoomControl(tk.Frame):
        """A compact widget to control zoom levels with buttons and a dropdown."""
        
        def __init__(self, parent, zoom_levels, current_zoom_index, on_zoom_change, **kwargs):
            super().__init__(parent, **kwargs)
            self.zoom_levels = zoom_levels  # List of zoom levels
            self.on_zoom_change = on_zoom_change  # Callback for zoom change events
            self.current_zoom_index = current_zoom_index  # Default zoom level index

            # Zoom out button
            self.zoom_out_button = tk.Button(self, text="–", command=self.zoom_out, width=2)
            self.zoom_out_button.pack(side=tk.LEFT, padx=2)

            # Dropdown for zoom levels
            self.zoom_var = tk.StringVar(value=f"{zoom_levels[current_zoom_index]}%")
            self.zoom_dropdown = tk.OptionMenu(self, self.zoom_var, *[f"{level}%" for level in zoom_levels], command=self._on_dropdown_change)
            self.zoom_dropdown.config(width=6)
            self.zoom_dropdown.pack(side=tk.LEFT, padx=2)

            # Zoom in button
            self.zoom_in_button = tk.Button(self, text="+", command=self.zoom_in, width=2)
            self.zoom_in_button.pack(side=tk.LEFT, padx=2)

        def _on_dropdown_change(self, selected_value):
            """Handle dropdown changes by updating the zoom level."""
            new_zoom_level = int(selected_value.strip('%'))
            self.current_zoom_index = self.zoom_levels.index(new_zoom_level)
            self.on_zoom_change(self.current_zoom_index)  # Call the zoom change callback

        def zoom_in(self):
            """Increase the zoom level if possible."""
            if self.current_zoom_index < len(self.zoom_levels) - 1:
                self.current_zoom_index += 1
                self.update_zoom()

        def zoom_out(self):
            """Decrease the zoom level if possible."""
            if self.current_zoom_index > 0:
                self.current_zoom_index -= 1
                self.update_zoom()

        def update_zoom(self):
            """Update zoom level display and invoke the callback."""
            new_zoom_level = self.zoom_levels[self.current_zoom_index]
            self.zoom_var.set(f"{new_zoom_level}%")  # Update dropdown text
            self.on_zoom_change(self.current_zoom_index)  # Trigger zoom level change callback

    class GridToggleButton(tk.Button):
        """A custom toggle button that switches between bold and regular hash (#) for grid control."""

        def __init__(self, parent, on_toggle, **kwargs):
            super().__init__(parent, text="#", command=self.toggle, **kwargs)
            self.on_toggle = on_toggle  # Callback to notify on toggle
            self.grid_on = False  # Initial grid state

            # Configure fonts for regular and bold states
            self.regular_font = font.nametofont("TkDefaultFont")
            self.bold_font = self.regular_font.copy()
            self.bold_font.configure(weight="bold")

            # Initialize with regular font
            self.config(font=self.regular_font)

        def toggle(self):
            """Toggle the grid state and update the button's appearance."""
            self.grid_on = not self.grid_on  # Switch the state
            self.config(font=self.bold_font if self.grid_on else self.regular_font)
            self.on_toggle(self.grid_on)  # Notify the parent widget of the new state