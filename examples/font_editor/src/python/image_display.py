import tkinter as tk
from PIL import Image, ImageTk
from custom_widgets import GridToggleButton, ZoomControl
from config_manager import get_app_config_value
from agon_font import create_blank_font_image

class ImageDisplay(tk.Frame):
    """A widget to display and zoom an image on a canvas, handle mouse clicks, and extract characters."""
    
    def __init__(self, parent, app_reference, **kwargs):
        super().__init__(parent, **kwargs)
        self.app_reference = app_reference

        self.current_ascii_code = ord('A')   # Default to ASCII code for 'A'
        self.zoom_levels = [25, 50, 100, 200, 300, 400]
        zoom_level = int(get_app_config_value('default_zoom_level'))
        self.current_zoom_index = self.zoom_levels.index(zoom_level)

        # Load the blank font image
        font_config = self.app_reference.font_config_editor.get_config()
        self.working_image = create_blank_font_image(font_config)        
        self.grid_shown = False

        # Control frame for toggle and zoom controls
        control_frame = tk.Frame(self)
        control_frame.pack(side=tk.TOP, anchor="nw", pady=5)

        # Create custom grid toggle button
        self.grid_toggle_button = GridToggleButton(control_frame, on_toggle=self.toggle_grid)
        self.grid_toggle_button.pack(side=tk.LEFT, padx=5)

        # Zoom control
        self.zoom_control = ZoomControl(
            control_frame, 
            zoom_levels=self.zoom_levels, 
            current_zoom_index=self.current_zoom_index, 
            on_zoom_change=self.change_zoom
        )
        self.zoom_control.pack(side=tk.LEFT, padx=5)

        # Canvas for displaying image
        self.canvas = tk.Canvas(self, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Configure>", self.resize_canvas)
        self.canvas.bind("<Button-1>", self.on_click)

        # Load the blank font image
        self.load_image(self.working_image)

    def redraw(self):
        """Redraw the canvas elements including the image, grid, and selection box."""
        self.display_image()  # Adjust image based on zoom level
        if self.grid_shown:
            self.draw_grid()  # Draw the grid if enabled
        if self.current_ascii_code is not None:
            char_x, char_y = self.ascii_to_coordinates(self.current_ascii_code)
            self.draw_selection_box(char_x, char_y)  # Update selection box

    def change_zoom(self, zoom_index):
        """Update zoom level and redraw widget."""
        self.current_zoom_index = zoom_index
        self.update_display_dimensions()
        self.redraw()

    def toggle_grid(self, grid_on):
        """Toggle the grid on the canvas based on the grid toggle button state."""
        self.grid_shown = grid_on
        if self.grid_shown:
            self.draw_grid()
        else:
            self.clear_grid()

    def display_image(self):
        """Display the image on the canvas based on the current zoom level."""
        if self.working_image is None:
            return
        
        zoom_factor = self.zoom_levels[self.current_zoom_index] / 100
        new_width = int(self.working_image.width * zoom_factor)
        new_height = int(self.working_image.height * zoom_factor)
        
        # Resize the image according to the new dimensions
        self.image = self.working_image.resize((new_width, new_height), Image.NEAREST)
        self.tk_image = ImageTk.PhotoImage(self.image)

        # Set scroll region and display image
        self.canvas.config(scrollregion=(0, 0, new_width, new_height))
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)

        # Adjust the canvas size if needed
        self.canvas.config(width=new_width, height=new_height)

    def draw_grid(self):
        """Draw cyan gridlines based on the font dimensions and current zoom level."""
        self.clear_grid()
        zoom_factor = self.zoom_levels[self.current_zoom_index] / 100
        font_config = self.app_reference.font_config_editor.get_config()
        grid_width = int(font_config['font_width_mod'] * zoom_factor)
        grid_height = int(font_config['font_height_mod'] * zoom_factor)
        img_width = int(self.working_image.width * zoom_factor)
        img_height = int(self.working_image.height * zoom_factor)

        for x in range(0, img_width, grid_width):
            self.canvas.create_line(x, 0, x, img_height, fill="cyan", tags="gridline")
        for y in range(0, img_height, grid_height):
            self.canvas.create_line(0, y, img_width, y, fill="cyan", tags="gridline")

    def draw_selection_box(self, char_x, char_y):
        """Draw a green selection box around the selected character without obscuring edge pixels."""
        self.clear_selection_box()
        zoom_factor = self.zoom_levels[self.current_zoom_index] / 100
        font_config = self.app_reference.font_config_editor.get_config()
        box_width = int(font_config['font_width_mod'] * zoom_factor)
        box_height = int(font_config['font_height_mod'] * zoom_factor)
        x1 = char_x * box_width - 1
        y1 = char_y * box_height - 1
        x2 = x1 + box_width + 1
        y2 = y1 + box_height + 1
        self.canvas.create_rectangle(x1, y1, x2, y2, outline="green", width=2, tags="selection_box")

    def resize_canvas(self, event):
        """Resize the canvas to fit the image and redraw."""
        if self.working_image:
            self.redraw()

    def clear_selection_box(self):
        """Remove the existing selection box from the canvas."""
        self.canvas.delete("selection_box")

    def clear_grid(self):
        """Remove all gridlines from the canvas."""
        self.canvas.delete("gridline")

    def load_image(self, image):
        """Load the image into the widget."""
        self.working_image = image
        self.redraw()

    def trigger_click_on_ascii_code(self, ascii_code):
        """Simulate a click on the given ASCII code and display the selection box."""
        if self.working_image:
            self.current_ascii_code = ascii_code
            char_x, char_y = self.ascii_to_coordinates(ascii_code)
            self.draw_selection_box(char_x, char_y)
            char_img = self.get_char_img_xy(char_x, char_y)
            self.app_reference.editor_widget.populate_from_image(char_img)

    def on_click(self, event):
        """Handle mouse click on the image and delegate to helper functions to get the character."""
        if not self.working_image:
            return
        click_x, click_y = self.get_click_coordinates(event)
        char_x, char_y = self.get_character_coordinates(click_x, click_y)
        ascii_code = self.coordinates_to_ascii(char_x, char_y)
        ascii_range = self.app_reference.font_config_editor.get_config()
        if ascii_range['ascii_start'] <= ascii_code <= ascii_range['ascii_end']:
            self.current_ascii_code = ascii_code
            self.draw_selection_box(char_x, char_y)
            char_img = self.get_char_img_xy(char_x, char_y)
            if self.app_reference.editor_widget:
                self.app_reference.editor_widget.populate_from_image(char_img)
        else:
            self.clear_selection_box()
            print("Clicked outside the ASCII range.")

    def get_char_img_xy(self, char_x, char_y):
        """ Extract the character image from the original image using char_x, char_y, and display it in the editor """
        if not self.working_image:
            return

        font_config = self.app_reference.font_config_editor.get_config()
        x1 = char_x * font_config['font_width_mod']
        y1 = char_y * font_config['font_height_mod']
        x2 = x1 + font_config['font_width_mod']
        y2 = y1 + font_config['font_height_mod']

        return self.working_image.crop((x1, y1, x2, y2))
    
    def get_char_img_ascii(self, ascii_code):
        """ Extract the character image from the original image using the ASCII code and display it in the editor """
        char_x, char_y = self.ascii_to_coordinates(ascii_code)
        return self.get_char_img_xy(char_x, char_y)

    def update_pixel(self, x, y, color):
        """Update the clicked pixel in the character image with the provided RGBA color and refresh the working image."""
        if self.current_ascii_code is None or self.working_image is None:
            print("No character selected or no image loaded.")
            return

        # Retrieve font dimensions from the config editor
        font_config = self.app_reference.font_config_editor.get_config()
        font_width = font_config['font_width_mod']
        font_height = font_config['font_height_mod']

        # Calculate position in working image based on character coordinates
        char_x, char_y = self.ascii_to_coordinates(self.current_ascii_code)
        pixel_x = char_x * font_width + x
        pixel_y = char_y * font_height + y

        # Update the pixel color in the working image and refresh display
        self.working_image.putpixel((pixel_x, pixel_y), color)
        self.redraw()

    # Helper functions
    def ascii_to_coordinates(self, ascii_code):
        font_config = self.app_reference.font_config_editor.get_config()
        char_x = (ascii_code - font_config['ascii_start']) % 16
        char_y = (ascii_code - font_config['ascii_start']) // 16
        return char_x, char_y

    def coordinates_to_ascii(self, char_x, char_y):
        font_config = self.app_reference.font_config_editor.get_config()
        return char_y * 16 + char_x + font_config['ascii_start']

    def get_click_coordinates(self, event):
        zoom_factor = self.zoom_levels[self.current_zoom_index] / 100
        click_x = int(event.x / zoom_factor)
        click_y = int(event.y / zoom_factor)
        return click_x, click_y

    def get_character_coordinates(self, click_x, click_y):
        font_config = self.app_reference.font_config_editor.get_config()
        char_x = click_x // font_config['font_width_mod']
        char_y = click_y // font_config['font_height_mod']
        return char_x, char_y

    def crop_image(self, image, target_width, target_height):
        return image.crop((0, 0, target_width, target_height)) 

    def enlarge_image(self, image, target_width, target_height):
        new_image = Image.new("RGBA", (target_width, target_height), color=255)
        new_image.paste(image, (0, 0))
        return new_image
    
    def update_display_dimensions(self):
        zoom_factor = self.zoom_levels[self.current_zoom_index] / 100
        new_width = int(self.working_image.width * zoom_factor)
        new_height = int(self.working_image.height * zoom_factor)
        self.canvas.config(width=new_width, height=new_height)
        self.config(width=new_width, height=new_height)
