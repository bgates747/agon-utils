import tkinter as tk
from PIL import Image, ImageTk

class ImageDisplayWidget(tk.Frame):
    """A widget to display and zoom an image on a canvas, handle mouse clicks, and extract characters."""
    def __init__(self, parent, app_reference, **kwargs):
        super().__init__(parent, **kwargs)
        self.app_reference = app_reference
        self.font_width = None
        self.font_height = None
        self.ascii_range = None
        self.current_ascii_code = None
        self.current_zoom_index = app_reference.config_manager.get_default_zoom_level()
        self.original_image = None

        self.grid_shown = False

        # Zoom levels: 1/8, 1/4, 1/2, 1, 2, 3, 4
        self.zoom_levels = [12.5, 25, 50, 100, 200, 300, 400]

        # Button controls at the top
        control_frame = tk.Frame(self)
        control_frame.pack(side=tk.TOP, pady=5)

        self.zoom_in_button = tk.Button(control_frame, text="Zoom In", command=self.zoom_in)
        self.zoom_in_button.pack(side=tk.LEFT, padx=5)

        self.zoom_out_button = tk.Button(control_frame, text="Zoom Out", command=self.zoom_out)
        self.zoom_out_button.pack(side=tk.LEFT, padx=5)

        self.toggle_grid_button = tk.Button(control_frame, text="Toggle Grid", command=self.toggle_grid)
        self.toggle_grid_button.pack(side=tk.LEFT, padx=5)

        # Canvas for displaying image
        self.canvas = tk.Canvas(self, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Bind resizing events
        self.canvas.bind("<Configure>", self.resize_canvas)
        self.canvas.bind("<Button-1>", self.on_click)

    def draw_selection_box(self, char_x, char_y):
        """Draw a green selection box around the selected character without obscuring edge pixels."""
        self.clear_selection_box()
        zoom_factor = self.zoom_levels[self.current_zoom_index] / 100
        box_width = int(self.font_width * zoom_factor)
        box_height = int(self.font_height * zoom_factor)
        x1 = char_x * box_width - 1
        y1 = char_y * box_height - 1
        x2 = x1 + box_width + 1
        y2 = y1 + box_height + 1
        self.canvas.create_rectangle(x1, y1, x2, y2, outline="green", width=2, tags="selection_box")

    def clear_selection_box(self):
        """Remove the existing selection box from the canvas."""
        self.canvas.delete("selection_box")

    def toggle_grid(self):
        """Toggle cyan gridlines on and off."""
        self.grid_shown = not self.grid_shown
        if self.grid_shown:
            self.draw_grid()
        else:
            self.clear_grid()

    def draw_grid(self):
        """Draw cyan gridlines based on the font dimensions and current zoom level."""
        self.clear_grid()
        zoom_factor = self.zoom_levels[self.current_zoom_index] / 100
        grid_width = int(self.font_width * zoom_factor)
        grid_height = int(self.font_height * zoom_factor)
        img_width = int(self.original_image.width * zoom_factor)
        img_height = int(self.original_image.height * zoom_factor)

        for x in range(0, img_width, grid_width):
            self.canvas.create_line(x, 0, x, img_height, fill="cyan", tags="gridline")
        for y in range(0, img_height, grid_height):
            self.canvas.create_line(0, y, img_width, y, fill="cyan", tags="gridline")

    def clear_grid(self):
        """Remove all gridlines from the canvas."""
        self.canvas.delete("gridline")

    def set_font_metadata(self, font_width, font_height, ascii_range):
        """Set the font metadata for width, height, and ASCII range."""
        print(f"Setting font metadata: width={font_width}, height={font_height}, ascii_range={ascii_range}")
        self.font_width = font_width
        self.font_height = font_height
        self.ascii_range = ascii_range
        if self.grid_shown:
            self.draw_grid()

    def load_image(self, original_image):
        """Load the image into the widget."""
        self.original_image = original_image
        img_width, img_height = self.original_image.size
        print(f"Loaded image with size: {img_width}x{img_height}")
        self.update_display_dimensions()
        self.display_image()

    def trigger_click_on_ascii_code(self, ascii_code):
        """Simulate a click on the given ASCII code and display the selection box."""
        if self.original_image:
            char_x, char_y = self.ascii_to_coordinates(ascii_code)
            self.extract_character(ascii_code, char_x, char_y)
            self.draw_selection_box(char_x, char_y)

    def display_image(self):
        """Display the image on the canvas based on the current zoom level."""
        if self.original_image is None:
            return
        zoom_factor = self.zoom_levels[self.current_zoom_index] / 100
        new_width = int(self.original_image.width * zoom_factor)
        new_height = int(self.original_image.height * zoom_factor)
        self.image = self.original_image.resize((new_width, new_height), Image.NEAREST)

        self.tk_image = ImageTk.PhotoImage(self.image)
        self.canvas.config(scrollregion=(0, 0, new_width, new_height))
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)

    def update_display_dimensions(self):
        """Update the entire widget's size based on the zoomed image dimensions."""
        zoom_factor = self.zoom_levels[self.current_zoom_index] / 100
        new_width = int(self.original_image.width * zoom_factor)
        new_height = int(self.original_image.height * zoom_factor)
        self.canvas.config(width=new_width, height=new_height)
        self.config(width=new_width, height=new_height)

    def resize_canvas(self, event):
        """Resize the canvas to fit the image."""
        if self.original_image:
            self.update_display_dimensions()
            self.display_image()

    def zoom_in(self):
        """Increase the zoom level and update the display."""
        if self.current_zoom_index < len(self.zoom_levels) - 1:
            self.current_zoom_index += 1
            self.update_display_dimensions()
            self.display_image()
            if self.grid_shown:
                self.draw_grid()
            if self.current_ascii_code is not None:
                char_x, char_y = self.ascii_to_coordinates(self.current_ascii_code)
                self.draw_selection_box(char_x, char_y)

    def zoom_out(self):
        """Decrease the zoom level and update the display."""
        if self.current_zoom_index > 0:
            self.current_zoom_index -= 1
            self.update_display_dimensions()
            self.display_image()
            if self.grid_shown:
                self.draw_grid()
            if self.current_ascii_code is not None:
                char_x, char_y = self.ascii_to_coordinates(self.current_ascii_code)
                self.draw_selection_box(char_x, char_y)

    def on_click(self, event):
        """Handle mouse click on the image and delegate to helper functions to get the character."""
        if not self.original_image:
            return
        click_x, click_y = self.get_click_coordinates(event)
        char_x, char_y = self.get_character_coordinates(click_x, click_y)
        ascii_code = self.coordinates_to_ascii(char_x, char_y)
        if self.ascii_range[0] <= ascii_code <= self.ascii_range[1]:
            self.current_ascii_code = ascii_code
            self.extract_character(ascii_code, char_x, char_y)
            self.draw_selection_box(char_x, char_y)
        else:
            self.clear_selection_box()
            print("Clicked outside the ASCII range.")

    # Additional methods to update pixels, extract characters, and handle image operations remain unchanged.


    def extract_character(self, ascii_code, char_x, char_y):
        """ Extract the character image from the original image using char_x, char_y, and display it in the editor """
        if not self.original_image:
            return  # Do nothing if no image is loaded

        # Calculate the bounding box for the character
        x1 = char_x * self.font_width
        y1 = char_y * self.font_height
        x2 = x1 + self.font_width
        y2 = y1 + self.font_height

        # Crop the character from the original image
        char_img = self.original_image.crop((x1, y1, x2, y2))

        # Pass the character image to the editor widget to populate the grid
        self.app_reference.editor_widget.populate_from_image(char_img)

    def update_pixel(self, x, y, new_value):
        """ Update the clicked pixel in the character image and paste it back to the original image """
        if self.current_ascii_code is None or self.original_image is None:
            print("No character selected or no image loaded.")
            return

        # Convert the ASCII code to character coordinates using helper function
        char_x, char_y = self.ascii_to_coordinates(self.current_ascii_code)

        # Calculate the absolute pixel position within the selected character
        pixel_color = new_value * 255

        # Update only the selected pixel in the original image
        self.original_image.putpixel((char_x * self.font_width + x, char_y * self.font_height + y), pixel_color)
        
        # Refresh the image on the canvas to reflect the change
        self.display_image()


    # Centralized conversion functions
    def ascii_to_coordinates(self, ascii_code):
        """ Convert an ASCII code to character coordinates (char_x, char_y) in the image picker """
        char_x = (ascii_code - self.ascii_range[0]) % 16
        char_y = (ascii_code - self.ascii_range[0]) // 16
        return char_x, char_y

    def coordinates_to_ascii(self, char_x, char_y):
        """ Convert character coordinates (char_x, char_y) to the corresponding ASCII code """
        return char_y * 16 + char_x + self.ascii_range[0]

    def get_click_coordinates(self, event):
        """ Convert the click event coordinates to be relative to the image, accounting for zoom """
        zoom_factor = self.zoom_levels[self.current_zoom_index] / 100

        # Adjust the click position based on the zoom factor and return the coordinates
        click_x = int(event.x / zoom_factor)
        click_y = int(event.y / zoom_factor)
        return click_x, click_y

    def get_character_coordinates(self, click_x, click_y):
        """ Calculate which character coordinates (char_x, char_y) were clicked based on click position """
        char_x = click_x // self.font_width
        char_y = click_y // self.font_height
        return char_x, char_y
    
    def crop_image(self, image, target_width, target_height):
        """Crop the image to match the target dimensions."""
        return image.crop((0, 0, target_width, target_height))  # Top-left crop

    def enlarge_image(self, image, target_width, target_height):
        """Enlarge the image by padding it to match the target dimensions."""
        new_image = Image.new("L", (target_width, target_height), color=255)  # White background
        new_image.paste(image, (0, 0))  # Paste original image at top-left
        return new_image
    