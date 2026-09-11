# UI Scaling

Accepted on 2026-09-10 under [UI-001](tasks/UI-001.md).

Edit → Preferences → UI size offers Auto, 100%, 125%, 150%, 175%, 200%, and
250%. Save persists the selection as `ui_scale` in `src/python/app_config.xml`.
Close without saving leaves the stored preference unchanged. Restart the editor
to apply a saved change; the dialog does not restart it or discard the open font.
The accepted local setting is 200%.

Missing or invalid values default to Auto, which retains Tk's detected startup
scale. Manual percentages use 96 DPI as 100%, so 200% configures 192 DPI (Tk
scaling 192/72). These values specify the application's scale independently of
Tk's detected value. Enhanced desktop/per-monitor detection is deferred under
[UI-002](tasks/UI-002.md).

UI text, padding, and classic scrollbar width follow the application scale.
The +/− buttons use the normal UI font. Main and configuration-dialog forms
scroll vertically, including wheel scrolling and revealing focused controls;
their action buttons remain outside the scrolling form. Font-atlas zoom,
font dimensions, and export calculations retain their independent values.

Three integration checks in `tests/test_ui_scaling.py` verify growing controls,
scroll access, preference persistence and restart behavior, and unchanged atlas
pixels, glyph selection, and ordinary `.font` bytes. Run from the repository
root with `.venv/bin/python examples/font_editor/tests/test_ui_scaling.py` and
a display available, after the repository's prerequisite extension check.

Existing native API mismatches prevent RGBA2 export and color-picker visual
validation with the installed extension. These limitations and the test evidence
are recorded in the [development log](development/2026-09-10.md).
