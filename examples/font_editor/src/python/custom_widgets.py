
import tkinter as tk
from tkinter import ttk
from tkinter import font
from tkinter import ttk, colorchooser
from ui_scaling import ui_px


class ScrollableFrame(tk.Frame):
    """Keep configuration rows reachable when large fonts exceed the window."""

    def __init__(self, parent):
        super().__init__(parent)
        self.canvas = tk.Canvas(self, highlightthickness=0, height=ui_px(self, 440))
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.content = tk.Frame(self.canvas)
        self.window = self.canvas.create_window(0, 0, window=self.content, anchor="nw")
        self.content.bind("<Configure>", self._content_changed)
        self.canvas.bind("<Configure>", self._canvas_changed)
        self.toplevel = self.winfo_toplevel()
        self.bindings = {
            sequence: self.toplevel.bind(sequence, callback, add="+")
            for sequence, callback in (
                ("<MouseWheel>", self._scroll),
                ("<Button-4>", self._scroll),
                ("<Button-5>", self._scroll),
                ("<FocusIn>", self._show_focus),
            )
        }
        self.bind("<Destroy>", self._cleanup, add="+")

    def _content_changed(self, event):
        self.canvas.configure(
            scrollregion=self.canvas.bbox("all"), width=self.content.winfo_reqwidth()
        )

    def _canvas_changed(self, event):
        self.canvas.itemconfigure(self.window, width=max(event.width, self.content.winfo_reqwidth()))

    def _contains(self, widget):
        while widget is not None:
            if widget is self:
                return True
            widget = getattr(widget, "master", None)
        return False

    def _scroll(self, event):
        if not self._contains(event.widget) or isinstance(event.widget, ttk.Combobox):
            return
        if self.content.winfo_height() <= self.canvas.winfo_height():
            return
        if event.num in (4, 5):
            units = -3 if event.num == 4 else 3
        elif event.delta:
            units = -max(1, abs(event.delta) // 120) if event.delta > 0 else max(1, abs(event.delta) // 120)
        else:
            return
        self.canvas.yview_scroll(units, "units")
        return "break"

    def _show_focus(self, event):
        if not self._contains(event.widget) or event.widget in (self.canvas, self.scrollbar):
            return
        top = event.widget.winfo_rooty() - self.content.winfo_rooty()
        bottom = top + event.widget.winfo_height()
        visible_top = self.canvas.canvasy(0)
        visible_bottom = visible_top + self.canvas.winfo_height()
        if top < visible_top:
            self.canvas.yview_moveto(top / max(1, self.content.winfo_height()))
        elif bottom > visible_bottom:
            self.canvas.yview_moveto((bottom - self.canvas.winfo_height()) / max(1, self.content.winfo_height()))

    def _cleanup(self, event):
        if event.widget is self:
            for sequence, binding in self.bindings.items():
                self.toplevel.unbind(sequence, binding)

class ZoomControl(tk.Frame):
    """A compact widget to control zoom levels with buttons and a dropdown."""
    
    def __init__(self, parent, zoom_levels, current_zoom_index, on_zoom_change, **kwargs):
        super().__init__(parent, **kwargs)
        self.zoom_levels = zoom_levels  # List of available zoom levels
        self.on_zoom_change = on_zoom_change  # Callback for zoom change events
        self.current_zoom_index = current_zoom_index  # Default zoom level index

        # Zoom out button
        self.zoom_out_button = tk.Button(self, text="-", command=self.zoom_out, width=2)
        self.zoom_out_button.pack(side=tk.LEFT, padx=ui_px(self, 2))

        # Dropdown for selecting zoom levels
        self.zoom_var = tk.StringVar(value=f"{zoom_levels[current_zoom_index]}%")
        self.zoom_dropdown = tk.OptionMenu(
            self, self.zoom_var, *[f"{level}%" for level in zoom_levels], command=self._on_dropdown_change
        )
        self.zoom_dropdown.config(width=6)
        self.zoom_dropdown.pack(side=tk.LEFT, padx=ui_px(self, 2))

        # Zoom in button
        self.zoom_in_button = tk.Button(self, text="+", command=self.zoom_in, width=2)
        self.zoom_in_button.pack(side=tk.LEFT, padx=ui_px(self, 2))

    def _on_dropdown_change(self, selected_value):
        """Handle dropdown changes by updating the zoom level."""
        new_zoom_level = int(selected_value.strip('%'))
        self.current_zoom_index = self.zoom_levels.index(new_zoom_level)
        self.on_zoom_change(self.current_zoom_index)  # Trigger zoom change callback

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
        """Update the zoom level display and invoke the callback."""
        new_zoom_level = self.zoom_levels[self.current_zoom_index]
        self.zoom_var.set(f"{new_zoom_level}%")  # Update dropdown display
        self.on_zoom_change(self.current_zoom_index)  # Trigger zoom level change callback

class GridToggleButton(tk.Button):
    """A custom toggle button to control grid display, toggling between bold and regular text."""
    
    def __init__(self, parent, on_toggle, **kwargs):
        super().__init__(parent, text="#", command=self.toggle, **kwargs)
        self.on_toggle = on_toggle  # Callback to notify parent of toggle state
        self.grid_on = False  # Initial state of the grid display

        # Configure fonts for the regular and bold states
        self.regular_font = font.nametofont("TkDefaultFont")
        self.bold_font = self.regular_font.copy()
        self.bold_font.configure(weight="bold")

        # Initialize with regular font
        self.config(font=self.regular_font)

    def toggle(self):
        """Toggle the grid state and update the button's appearance."""
        self.grid_on = not self.grid_on  # Toggle the state
        self.config(font=self.bold_font if self.grid_on else self.regular_font)
        self.on_toggle(self.grid_on)  # Notify the parent widget of the new state

class ConsoleDisplay(tk.Frame):
    """A console-like text display widget with a method to append messages."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        # Create a frame to hold the text display and scrollbar
        text_frame = tk.Frame(self)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=ui_px(self, 5), pady=ui_px(self, 5))
        
        # Initialize text widget for console output
        self.text_display = tk.Text(text_frame, wrap='word', height=5, width=70, state='disabled', bg='black', fg='white')
        self.text_display.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Add scrollbar within the text_frame, aligned to the right
        self.scrollbar = tk.Scrollbar(text_frame, command=self.text_display.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_display.config(yscrollcommand=self.scrollbar.set)

    def append_message(self, message):
        """Append a new message to the console display."""
        self.text_display.config(state='normal')  # Enable editing
        self.text_display.insert(tk.END, message + "\n")  # Add the message
        self.text_display.config(state='disabled')  # Disable editing
        self.text_display.see(tk.END)  # Scroll to the end
