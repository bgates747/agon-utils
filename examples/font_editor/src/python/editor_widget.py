import tkinter as tk

from agon_font import parse_rgba_color, rgba_to_hex
from ui_scaling import ui_px


class EditorWidget(tk.Frame):
    """Edit the selected glyph's pixels without changing its bitmap dimensions."""

    def __init__(self, parent, app_reference, **kwargs):
        super().__init__(parent, **kwargs)
        self.app_reference = app_reference
        self.pixel_size = max(4, ui_px(self, 16))
        self.pixel_border = max(1, ui_px(self, 1))
        self.char_image = None
        self.pixel_items = {}
        self.canvas = tk.Canvas(self, bg="cyan", highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.vscroll = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.vscroll.grid(row=0, column=1, sticky="ns")
        self.hscroll = tk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)
        self.hscroll.grid(row=1, column=0, sticky="ew")
        self.canvas.configure(yscrollcommand=self.vscroll.set, xscrollcommand=self.hscroll.set)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.canvas.bind("<Button-1>", self.on_click)

    def populate_from_image(self, image):
        """Use the actual selected glyph as both visible and editable state."""
        config = self.app_reference.font_config_editor.get_config()
        self.fg_color = parse_rgba_color(config["fg_color"])
        self.bg_color = parse_rgba_color(config["bg_color"])
        self.char_image = image.convert("RGBA").copy()
        width, height = self.char_image.size
        canvas_width = width * self.pixel_size
        canvas_height = height * self.pixel_size
        self.canvas.configure(
            width=min(canvas_width, ui_px(self, 512)),
            height=min(canvas_height, ui_px(self, 420)),
            scrollregion=(0, 0, canvas_width, canvas_height),
        )
        self.canvas.delete("all")
        self.pixel_items.clear()
        for y in range(height):
            for x in range(width):
                self.pixel_items[x, y] = self.canvas.create_rectangle(
                    x * self.pixel_size + self.pixel_border,
                    y * self.pixel_size + self.pixel_border,
                    (x + 1) * self.pixel_size,
                    (y + 1) * self.pixel_size,
                    fill=rgba_to_hex(self.char_image.getpixel((x, y))), outline="",
                )

    def on_click(self, event):
        if self.char_image is None:
            return
        x = int(self.canvas.canvasx(event.x) // self.pixel_size)
        y = int(self.canvas.canvasy(event.y) // self.pixel_size)
        if not (0 <= x < self.char_image.width and 0 <= y < self.char_image.height):
            return
        current_color = self.char_image.getpixel((x, y))
        color = self.bg_color if current_color[:3] == self.fg_color[:3] else self.fg_color
        self.char_image.putpixel((x, y), color)
        self.canvas.itemconfigure(self.pixel_items[x, y], fill=rgba_to_hex(color))
        self.app_reference.image_display.update_pixel(x, y, color)
