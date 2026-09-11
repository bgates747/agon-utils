"""Application chrome scaling; font artwork always keeps its own pixel scale."""

import tkinter as tk
from tkinter import font, messagebox, ttk

from config_manager import get_app_config_value, set_app_config_value


UI_SCALES = ("Auto", "100%", "125%", "150%", "175%", "200%", "250%")


def normalize_ui_scale(value):
    """Old configurations and invalid preferences use Tk's startup default."""
    return value if value in UI_SCALES else "Auto"


def initialize_ui_scaling(root):
    """Call before creating widgets. Explicit percentages use 96 DPI as 100%."""
    if hasattr(root, "ui_scale"):
        return
    root.ui_scale = normalize_ui_scale(get_app_config_value("ui_scale"))
    initial_scaling = float(root.tk.call("tk", "scaling"))
    if root.ui_scale != "Auto":
        scaling = (96 / 72) * int(root.ui_scale.rstrip("%")) / 100
        root.tk.call("tk", "scaling", scaling)
        # Point fonts follow Tk scaling. Pixel-sized named fonts need an
        # explicit adjustment; refresh point fonts for older Tk versions too.
        ratio = float(root.tk.call("tk", "scaling")) / initial_scaling
        for name in font.names(root):
            named_font = font.nametofont(name, root=root)
            size = named_font.cget("size")
            named_font.configure(size=-max(1, round(-size * ratio)) if size < 0 else size)
    root.ui_scale_factor = float(root.tk.call("tk", "scaling")) / (96 / 72)
    # Classic Tk scrollbars have a pixel width. Text-sized controls and ttk
    # theme elements already follow their fonts / Tk's scale.
    root.option_add("*Scrollbar.width", ui_px(root, 14))


def ui_px(widget, pixels):
    """Convert a UI dimension at 96 DPI; never use for font atlas coordinates."""
    root = widget._root()
    factor = getattr(root, "ui_scale_factor", 1.0)
    return round(pixels * factor)


class PreferencesDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Preferences")
        self.transient(parent)
        self.resizable(False, False)
        body = ttk.Frame(self, padding=ui_px(self, 12))
        body.pack(fill="both", expand=True)
        ttk.Label(body, text="UI size").grid(row=0, column=0, sticky="w")
        self.scale = tk.StringVar(self, normalize_ui_scale(get_app_config_value("ui_scale")))
        self.selector = ttk.Combobox(
            body, textvariable=self.scale, values=UI_SCALES, state="readonly", width=10
        )
        self.selector.grid(row=0, column=1, padx=ui_px(self, 12), sticky="e")
        ttk.Label(
            body,
            text="Auto uses the detected display scale.\nChanges apply after restarting the editor.\nFont-image zoom and saved fonts are unaffected.",
            justify="left",
        ).grid(row=1, column=0, columnspan=2, pady=ui_px(self, 12), sticky="w")
        self.status = ttk.Label(body, text="")
        self.status.grid(row=2, column=0, columnspan=2, sticky="w")
        buttons = ttk.Frame(body)
        buttons.grid(row=3, column=0, columnspan=2, pady=(ui_px(self, 8), 0), sticky="e")
        ttk.Button(buttons, text="Save", command=self.save).pack(side="left", padx=ui_px(self, 5))
        ttk.Button(buttons, text="Close", command=self.destroy).pack(side="left")
        self.bind("<Escape>", lambda event: self.destroy())
        self.grab_set()
        self.selector.focus_set()

    def save(self):
        try:
            if not set_app_config_value("ui_scale", normalize_ui_scale(self.scale.get())):
                raise OSError("Could not update app_config.xml.")
        except OSError as error:
            messagebox.showerror("Preferences", str(error), parent=self)
            return
        self.status.configure(text="Saved. Restart the editor to apply.")
