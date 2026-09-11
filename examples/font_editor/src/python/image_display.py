import math
import tkinter as tk
from PIL import Image, ImageTk

from custom_widgets import GridToggleButton, ZoomControl
from config_manager import get_app_config_value
from agon_font import create_blank_font_image, read_font
from ui_scaling import ui_px


class ImageDisplay(tk.Frame):
    """A scrollable font atlas with zoom and character selection."""

    def __init__(self, parent, app_reference, **kwargs):
        super().__init__(parent, **kwargs)
        self.app_reference = app_reference
        self.current_ascii_code = ord('A')
        self.zoom_levels = [25, 50, 100, 200, 300, 400, 500, 600, 700, 800]
        try:
            zoom_level = int(get_app_config_value('default_zoom_level'))
            self.current_zoom_index = self.zoom_levels.index(zoom_level)
        except (TypeError, ValueError):
            self.current_zoom_index = self.zoom_levels.index(100)
        self.grid_shown = False

        control_frame = tk.Frame(self)
        control_frame.pack(side=tk.TOP, anchor="nw", pady=ui_px(self, 5))
        self.grid_toggle_button = GridToggleButton(control_frame, on_toggle=self.toggle_grid)
        self.grid_toggle_button.pack(side=tk.LEFT, padx=ui_px(self, 5))
        self.zoom_control = ZoomControl(
            control_frame, zoom_levels=self.zoom_levels,
            current_zoom_index=self.current_zoom_index, on_zoom_change=self.change_zoom,
        )
        self.zoom_control.pack(side=tk.LEFT, padx=ui_px(self, 5))
        self.optimize_all_button = tk.Button(
            control_frame, text="Optimize All Characters",
            command=app_reference.optimize_all_characters,
        )
        self.optimize_all_button.pack(side=tk.LEFT, padx=ui_px(self, 5))

        viewport = tk.Frame(self)
        viewport.pack(fill="both", expand=True)
        viewport.rowconfigure(0, weight=1)
        viewport.columnconfigure(0, weight=1)
        self.canvas = tk.Canvas(
            viewport, bg="white", highlightthickness=0,
            width=ui_px(self, 640), height=ui_px(self, 440),
        )
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.vscroll = tk.Scrollbar(viewport, orient="vertical", command=self.canvas.yview)
        self.vscroll.grid(row=0, column=1, sticky="ns")
        self.hscroll = tk.Scrollbar(viewport, orient="horizontal", command=self.canvas.xview)
        self.hscroll.grid(row=1, column=0, sticky="ew")
        self.canvas.configure(xscrollcommand=self.hscroll.set, yscrollcommand=self.vscroll.set)
        self.canvas.bind("<Button-1>", self.on_click)
        for sequence in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
            self.canvas.bind(sequence, self._scroll)
        # Reuse a single image item. Window resizes only change the viewport;
        # they must not rasterize the atlas or request another window resize.
        self.image_item = self.canvas.create_image(0, 0, anchor=tk.NW, tags="atlas")
        config = self.app_reference.font_config_editor.get_config()
        self.load_image(create_blank_font_image(config))

    def redraw(self):
        self.display_image()
        if self.grid_shown:
            self.draw_grid()
        else:
            self.clear_grid()
        self.clear_selection_box()
        if self.current_ascii_code is not None:
            self.draw_selection_box(*self.ascii_to_coordinates(self.current_ascii_code))

    def change_zoom(self, zoom_index):
        if not 0 <= zoom_index < len(self.zoom_levels):
            return
        self.current_zoom_index = zoom_index
        self.zoom_control.current_zoom_index = zoom_index
        self.zoom_control.zoom_var.set(f"{self.zoom_levels[zoom_index]}%")
        self.redraw()

    def toggle_grid(self, grid_on):
        self.grid_shown = grid_on
        if grid_on:
            self.draw_grid()
        else:
            self.clear_grid()

    def display_image(self):
        zoom = self.zoom_levels[self.current_zoom_index] / 100
        size = (max(1, int(self.working_image.width * zoom)),
                max(1, int(self.working_image.height * zoom)))
        self.image = self.working_image.resize(size, Image.Resampling.NEAREST)
        self.tk_image = ImageTk.PhotoImage(self.image, master=self.canvas)
        self.canvas.itemconfigure(self.image_item, image=self.tk_image)
        self.canvas.tag_lower(self.image_item)
        self.update_display_dimensions()

    def _display_scale(self):
        # Use the actual raster size, including rounding at fractional zooms.
        return (self.image.width / self.working_image.width,
                self.image.height / self.working_image.height)

    def draw_grid(self):
        self.clear_grid()
        config = self.app_reference.font_config_editor.get_config()
        scale_x, scale_y = self._display_scale()
        width, height = config['font_width_mod'], config['font_height_mod']
        # Iterate source cells, never an integer-truncated zoomed pixel step.
        for x in range(0, self.working_image.width + 1, width):
            self.canvas.create_line(x * scale_x, 0, x * scale_x, self.image.height,
                                    fill="cyan", tags="gridline")
        for y in range(0, self.working_image.height + 1, height):
            self.canvas.create_line(0, y * scale_y, self.image.width, y * scale_y,
                                    fill="cyan", tags="gridline")
        self.canvas.tag_raise("selection_box")

    def draw_selection_box(self, char_x, char_y):
        self.clear_selection_box()
        config = self.app_reference.font_config_editor.get_config()
        scale_x, scale_y = self._display_scale()
        cell_width = config['font_width_mod'] * scale_x
        cell_height = config['font_height_mod'] * scale_y
        self.canvas.create_rectangle(
            char_x * cell_width, char_y * cell_height,
            (char_x + 1) * cell_width, (char_y + 1) * cell_height,
            outline="green", width=2, tags="selection_box",
        )

    def clear_selection_box(self):
        self.canvas.delete("selection_box")

    def clear_grid(self):
        self.canvas.delete("gridline")

    def load_image(self, image):
        self.working_image = image
        config = self.app_reference.font_config_editor.get_config()
        if self.current_ascii_code is None or not config['ascii_start'] <= self.current_ascii_code <= config['ascii_end']:
            self.current_ascii_code = config['ascii_start']
        self.redraw()
        # A source/configuration change refreshes an already open editor but
        # never opens one just because a font was loaded.
        self.app_reference.refresh_character_editor()

    def trigger_click_on_ascii_code(self, ascii_code):
        config = self.app_reference.font_config_editor.get_config()
        if not config['ascii_start'] <= ascii_code <= config['ascii_end']:
            return
        self.current_ascii_code = ascii_code
        self.draw_selection_box(*self.ascii_to_coordinates(ascii_code))
        self.app_reference.open_character_editor()

    def on_click(self, event):
        x, y = self.get_click_coordinates(event)
        if not (0 <= x < self.working_image.width and 0 <= y < self.working_image.height):
            return
        char_x, char_y = self.get_character_coordinates(x, y)
        self.trigger_click_on_ascii_code(self.coordinates_to_ascii(char_x, char_y))

    def get_char_img_xy(self, char_x, char_y):
        config = self.app_reference.font_config_editor.get_config()
        width, height = config['font_width_mod'], config['font_height_mod']
        x, y = char_x * width, char_y * height
        return self.working_image.crop((x, y, x + width, y + height))

    def get_char_img_ascii(self, ascii_code):
        return self.get_char_img_xy(*self.ascii_to_coordinates(ascii_code))

    def update_pixel(self, x, y, color):
        if self.current_ascii_code is None:
            return
        config = self.app_reference.font_config_editor.get_config()
        width, height = config['font_width_mod'], config['font_height_mod']
        if not (0 <= x < width and 0 <= y < height):
            return
        char_x, char_y = self.ascii_to_coordinates(self.current_ascii_code)
        # Rendering uses RGB; the editor maintains RGBA state for its colors.
        if self.working_image.mode == "RGB":
            color = color[:3]
        self.working_image.putpixel((char_x * width + x, char_y * height + y), color)
        self.redraw()

    def ascii_to_coordinates(self, ascii_code):
        config = self.app_reference.font_config_editor.get_config()
        index = ascii_code - config['ascii_start']
        return index % config['chars_per_row'], index // config['chars_per_row']

    def coordinates_to_ascii(self, char_x, char_y):
        config = self.app_reference.font_config_editor.get_config()
        return char_y * config['chars_per_row'] + char_x + config['ascii_start']

    def get_click_coordinates(self, event):
        scale_x, scale_y = self._display_scale()
        return (math.floor(self.canvas.canvasx(event.x) / scale_x),
                math.floor(self.canvas.canvasy(event.y) / scale_y))

    def get_character_coordinates(self, click_x, click_y):
        config = self.app_reference.font_config_editor.get_config()
        return click_x // config['font_width_mod'], click_y // config['font_height_mod']

    def update_display_dimensions(self):
        self.canvas.configure(scrollregion=(0, 0, self.image.width, self.image.height))

    def _scroll(self, event):
        if event.num in (4, 5):
            units = -3 if event.num == 4 else 3
        elif event.delta:
            units = -1 if event.delta > 0 else 1
        else:
            return
        view = self.canvas.xview_scroll if event.state & 1 else self.canvas.yview_scroll
        view(units, "units")
        return "break"

    def render_font(self):
        file_path = self.app_reference.current_font_file
        print(f"Rendering font image from {file_path}")
        config = self.app_reference.font_config_editor.get_config()
        config, font_image = read_font(file_path, config)
        config['font_width_mod'] = config['font_width'] + config['offset_width'] + config['scale_width']
        config['font_height_mod'] = config['font_height'] + config['offset_height'] + config['scale_height']
        self.app_reference.font_config_editor.set_controls_from_config(config)
        self.load_image(font_image.convert("RGB"))
