# Font Grid and Character Editor

Implemented under [UI-003](tasks/UI-003.md) and [UI-004](tasks/UI-004.md).

The author confirmed the restored interaction works, but clarified that the
editor must ultimately be embedded in the main application. The separate window
described below is the current interim behavior; [UI-005](tasks/UI-005.md) records
the intended replacement. No implementation change is made during the audit.

Clicking a valid character in the atlas opens one character editor window.
Further selections reuse that window and load the selected glyph's actual pixel
data. It holds no modal input grab, so the atlas and main controls stay usable.
Close the editor with its window close button or Escape; another glyph click
reopens it. Clicking the atlas margin or an unused final-row cell does nothing.

Clicking an editor cell toggles that pixel between the configured foreground and
background colors and immediately updates the corresponding atlas glyph. Edits
survive switching characters and are included by the existing ordinary `.font`
save path. Closing the character window does not discard atlas edits. Opening or
rerendering a source font successfully replaces the atlas; the open editor refreshes
to reflect the new image. There is no new undo or automatic font-saving behavior.
Failed opens preserve the current document. Batch controls do not rerender it,
and new `.font` exports reopen with their saved bitmap geometry, as specified in
[Document Opening and Bitmap Export](document-io.md).

Atlas zoom offers 25%, 50%, 100%, 200%, 300%, 400%, 500%, 600%, 700%, and 800%.
The dropdown and +/− buttons share the selection and respect the endpoints.
The configured `default_zoom_level` is read at startup; an invalid or unavailable
value falls back to 100%. Changing zoom does not change the saved startup value.

Horizontal and vertical scrollbars expose enlarged artwork. The mouse wheel
scrolls vertically over the atlas; Shift+wheel scrolls horizontally. Glyph clicks
and overlays use scrolled canvas coordinates, the actual rendered scale, the
configured characters per row, and the active character range. Zoom is independent
of [application UI size](ui-scaling.md) and never changes source font dimensions
or pixels.

The atlas reuses a single canvas image item. Window resizing changes the viewport
without rerasterizing the atlas; zoom and pixel changes redraw it. Editor pixel
items are replaced on glyph selection and updated in place on pixel changes.
Both the atlas and large character grids scroll within their windows.

Regression checks in `tests/test_character_editor.py` cover click bindings,
editing/export bytes, window lifecycle, scrolled selection, and repeated redraws.
Run the full font-editor suite from the repository root with
`.venv/bin/python -m unittest discover -s examples/font_editor/tests -v`, after
the repository's prerequisite extension check. Tk tests require a display, which
can be virtual; the [document I/O specification](document-io.md) gives the full
headless suite command. Tests use temporary app copies and generated Tk events
rather than global input.

The atlas toolbar offers **Optimize All Characters**, which runs an independent
brightness search per glyph and applies the complete result together. The
individual preview code remains but has no UI command. Output-pixel positioning,
legacy conversion and persistence limits are described in
[Font Resampling Optimization](glyph-resampling.md).
