"""Global command applying independent glyph searches as one completed edit."""

import time
import tkinter as tk
from tkinter import ttk

from agon_font import read_font
from glyph_resampling import optimize_atlas
from ui_scaling import ui_px


class AtlasResampling(tk.Toplevel):
    def __init__(self, app):
        super().__init__(app.master)
        self.app = app
        self.title('Optimize All Characters')
        self.transient(app.master)
        self.pending = None
        self.completed = False
        self.protocol('WM_DELETE_WINDOW', self.close)
        self.bind('<Escape>', lambda event: self.close())
        self.font_config = app.font_config_editor.get_config().copy()
        self.path = app.current_font_file
        self.original = app.image_display.working_image.copy()
        self.document = self.original.tobytes()
        self.status = tk.Label(self, text='Preparing character searches…', justify='left',
                               wraplength=ui_px(self, 400))
        self.status.pack(padx=ui_px(self, 12), pady=ui_px(self, 10))
        self.progress = ttk.Progressbar(self, length=ui_px(self, 360), mode='determinate')
        self.progress.pack(padx=ui_px(self, 12), pady=ui_px(self, 6))
        self.cancel_button = tk.Button(self, text='Cancel', command=self.close)
        self.cancel_button.pack(pady=ui_px(self, 10))
        try:
            config, source = read_font(self.path, self.font_config, render=False)
            if (config['font_width'], config['font_height']) != (
                    self.font_config['font_width'], self.font_config['font_height']):
                raise ValueError('The source geometry changed. Reopen it before optimizing.')
            self.search = optimize_atlas(self.font_config, source, self.original)
            self.pending = self.after(1, self.advance)
        except (OSError, ValueError, TypeError, KeyError) as error:
            self.fail(str(error))

    def unchanged(self):
        display = self.app.image_display
        return (self.app.current_font_file == self.path
                and self.app.font_config_editor.get_config() == self.font_config
                and display.working_image.size == self.original.size
                and display.working_image.tobytes() == self.document)

    def fail(self, reason):
        self.status.configure(text=f'{reason}\nNo optimization was applied.')
        self.cancel_button.configure(text='Close')

    def advance(self):
        self.pending = None
        if not self.unchanged():
            self.fail('The document changed during the search. Run the command again.')
            return
        try:
            deadline = time.monotonic() + .008
            # Bound both the phase count and time spent before returning to Tk.
            for _ in range(64):
                done, total, code = next(self.search)
                if time.monotonic() >= deadline:
                    break
            self.progress.configure(maximum=total, value=done)
            self.status.configure(text=f'Optimizing character {code} — {done}/{total} sampling phases')
            self.pending = self.after(1, self.advance)
        except StopIteration as complete:
            self.app.image_display.working_image = complete.value
            self.app.image_display.redraw()
            self.app.refresh_character_editor()
            self.completed = True
            self.progress.configure(value=self.progress.cget('maximum'))
            count = self.font_config['ascii_end'] - self.font_config['ascii_start'] + 1
            self.status.configure(text=f'Optimized all {count} characters. Offsets unchanged.\n'
                                       'Save PNG to keep the pixels. Rescaling regenerates the source.')
            self.cancel_button.configure(text='Close')
        except (OSError, ValueError, TypeError, KeyError) as error:
            self.fail(str(error))

    def close(self):
        if self.pending is not None:
            self.after_cancel(self.pending)
        self.destroy()
