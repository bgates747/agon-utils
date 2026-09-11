"""A cancellable, selected-character preview for the experimental brightness search."""

import tkinter as tk

from PIL import Image, ImageTk

from agon_font import read_font
from glyph_resampling import source_glyph, search_candidates, brightness
from ui_scaling import ui_px


class ResamplingPreview(tk.Toplevel):
    def __init__(self, app):
        super().__init__(app.master)
        self.app = app
        self.title('Optimize selected character')
        self.transient(app.master)
        self.pending = None
        self.protocol('WM_DELETE_WINDOW', self.close)
        self.bind('<Escape>', lambda event: self.close())
        self.font_config = app.font_config_editor.get_config().copy()
        self.path = app.current_font_file
        self.code = app.image_display.current_ascii_code
        self.document = app.image_display.working_image.tobytes()
        self.document_size = app.image_display.working_image.size
        self.result = None
        self.current = app.image_display.get_char_img_ascii(self.code).convert('RGBA')
        tk.Label(self, text=f'Character {self.code} — brightest of 81 sampling phases',
                 font='TkDefaultFont').grid(row=0, column=0, columnspan=2, padx=ui_px(self, 8))
        tk.Label(self, text='Current').grid(row=1, column=0)
        tk.Label(self, text='Candidate').grid(row=1, column=1)
        self.current_view = tk.Label(self)
        self.current_view.grid(row=2, column=0, padx=ui_px(self, 8))
        self.candidate_view = tk.Label(self)
        self.candidate_view.grid(row=2, column=1, padx=ui_px(self, 8))
        self.show_image(self.current_view, self.current)
        self.status = tk.Label(self, text='Searching…', justify='left', wraplength=ui_px(self, 440))
        self.status.grid(row=3, column=0, columnspan=2, padx=ui_px(self, 8), pady=ui_px(self, 6))
        self.apply_button = tk.Button(self, text='Apply to character', state='disabled', command=self.apply)
        self.apply_button.grid(row=4, column=0, pady=ui_px(self, 8))
        tk.Button(self, text='Cancel', command=self.close).grid(row=4, column=1)
        try:
            # Decode the source, not the already downsampled working image.
            decoded, source = read_font(self.path, self.font_config, render=False)
            if (decoded['font_width'], decoded['font_height']) != (
                    self.font_config['font_width'], self.font_config['font_height']):
                raise ValueError('The source geometry changed. Reopen it before optimizing.')
            self.search = search_candidates(self.font_config, source_glyph(self.font_config, source, self.code))
            self.pending = self.after(1, self.advance)
        except (OSError, ValueError, TypeError, KeyError) as error:
            self.status.configure(text=str(error))

    def show_image(self, label, glyph):
        scale = max(1, min(ui_px(self, 20), ui_px(self, 280) // max(glyph.size)))
        image = glyph.resize((glyph.width * scale, glyph.height * scale), Image.Resampling.NEAREST)
        photo = ImageTk.PhotoImage(image, master=self)
        label.configure(image=photo)
        label.photo = photo

    def unchanged(self):
        display = self.app.image_display
        return (self.app.current_font_file == self.path
                and display.current_ascii_code == self.code
                and self.app.font_config_editor.get_config() == self.font_config
                and display.working_image.size == self.document_size
                and display.working_image.tobytes() == self.document)

    def advance(self):
        self.pending = None
        if not self.unchanged():
            self.status.configure(text='The document or selection changed. Start a new preview.')
            return
        try:
            for _ in range(8):
                done, total, self.result, score, phase = next(self.search)
                self.status.configure(text=f'Searching {done}/{total}…')
            self.pending = self.after(1, self.advance)
        except StopIteration:
            self.show_image(self.candidate_view, self.result)
            gain = brightness(self.result) - brightness(self.current)
            self.status.configure(text=(f'Brightness change: {gain:+d}. Offsets unchanged: '
                                        f"{self.font_config['offset_left']}, {self.font_config['offset_top']} output pixels.\n"
                                        'Brightness may favour heavier strokes. Apply only if it looks better. '
                                        'Save PNG to preserve edits; changing render settings or reopening XML regenerates the source.'))
            self.apply_button.configure(state='normal')
        except (OSError, ValueError, TypeError, KeyError) as error:
            self.status.configure(text=str(error))

    def apply(self):
        if self.result is None or not self.unchanged():
            self.apply_button.configure(state='disabled')
            self.status.configure(text='The document or selection changed. Start a new preview.')
            return
        display = self.app.image_display
        x, y = display.ascii_to_coordinates(self.code)
        width, height = self.result.size
        display.working_image.paste(self.result.convert('RGB'), (x * width, y * height))
        display.redraw()
        self.app.refresh_character_editor()
        self.close()

    def close(self):
        if self.pending is not None:
            self.after_cancel(self.pending)
        self.destroy()
