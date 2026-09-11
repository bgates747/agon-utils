# Source Recipes and Bitmap Export

Implemented under [BUG-001](tasks/BUG-001.md), the quantized-save repair
[BUG-002](tasks/BUG-002.md), and the original-source correction
[BUG-003](tasks/BUG-003.md), following the
[frozen application audit](application-audit-2026-09-10.md).

## Opening

Opening prepares the candidate configuration and rendered image before changing
the main document. Decode failures and invalid geometry/color values leave the
current paths, title, controls, pixels, selection, character editor and recent
preferences intact. The File Open action reports these failures in an error
dialog. A missing path passed directly to `open_file` returns False, retaining
the prior startup behavior when the last-used file has disappeared.

Opening does not write the input sidecar or shared default `font_config.xml`.
Successful opening installs the prepared pixels, updates derived cell dimensions,
refreshes an existing character editor and records the requested file in recent
preferences. `current_font_xml_file` refers to the selected XML/associated
sidecar, or None when defaults supplied the configuration.

## Batch forms

Rendering controls ask their owning `ConfigEditor` to redraw. Only the main
font form is configured with the main atlas renderer. Batch controls change
their own values; Set persists batch settings, and Cancel dismisses the form.
These operations do not rerender the main font or change its edited pixels.
This does not change the separate batch conversion/output implementation.

## Source recipes and saved pixels

The top-level XML settings describe the original font source and how to render
it. `original_font_path` retains that source's absolute path (PNG, TTF, OTF,
PSF or a directly opened bitmap font). Original dimensions, point size, offsets,
scale adjustments, raster type, colors and palette remain source settings.
They are not replaced by export dimensions or the exported filename.

The optional `position_units` field distinguishes legacy source offsets from
whole output-pixel positioning. Older XML defaults to `source`; explicit units
conversion and the per-character sampling trial are described in
[glyph-resampling.md](glyph-resampling.md). Search phases are not serialized.

PNG/FONT saves also include a nested `<bitmap>` element containing normalized
metadata for the exported pixels: exported cell dimensions, zero transforms
and the appropriate bitmap raster settings. This distinction preserves both
source provenance and the ability to inspect actual output. Existing XML
readers selecting direct `<setting>` children continue to read the recipe.

| Open action | Result |
| --- | --- |
| Open XML | Render its original source with the saved recipe. |
| Open a newly saved PNG/FONT directly | Load its saved pixels using bitmap metadata; that bitmap becomes the current source. |
| Restart after Save | Open the saved XML recipe and regenerate from the original source. |

Save retains the live source and rendering controls, records the saved XML as
`current_font_xml_file`, and stores that XML in recent-file preferences. XML-only
Save writes just the source recipe. File Save rejects overwriting the source
file itself, including an alias to it, because replacing source artwork with a
rendered output would invalidate the recipe. Choose a separate output filename.

Relative source paths in existing XML resolve against the XML's directory.
Missing sources and circular XML references fail through the regular open error
path; they do not silently fall back to exported pixels. Directly opening an
export remains possible without its original source. FONT rendering reads only
storage dimensions from its sidecar, allowing live raster and scale controls
to take effect without being reset by saved settings.

Legacy XML remains readable. A direct legacy FONT open uses its `*_mod` storage
dimensions with zero transforms; legacy XML still follows `original_font_path`.
Files whose source provenance was already replaced by BUG-001/BUG-002 cannot
automatically recover that original path. No user sidecars are migrated.

## `.font` export

Saving an Agon `.font` exports the current atlas as a monochrome bitmap using
the configured threshold. Its nested bitmap metadata uses white/black colors
and threshold rendering; the top-level source recipe retains the user's raster
choice. Opening the binary directly recovers exported pixels and re-export
preserves its binary bytes.

The guarantee applies to glyph pixels representable in the existing 256-position
monochrome format. It does not promise color/alpha preservation or storage of
unused atlas cells. The binary and sidecar still use separate writes; recovery
from a partially failed save remains unfinished. Absolute original-source paths
also retain the app's existing portability limitation when projects are moved.

## Quantized rendering and PNG saves

Raster Type **quantized** uses the nearest of four fixed grayscale values:
0, 85, 170 and 255, without dithering. Raster Type **grayscale** converts the
rendered image to grayscale without reducing it to four levels. Previously
these two choices did not have rendering branches.

Save defaults to **PNG Font Atlas (preserve shades and colors)** for quantized,
grayscale and palette rendering. Threshold rendering defaults to **Agon Font
Files (monochrome)**. An explicitly selected `.font` remains a thresholded,
one-bit export; the binary format cannot retain intermediate gray levels.

PNG saving writes the current atlas pixels plus `<filename>.png.xml`. The
top-level sidecar retains the source recipe; its nested bitmap metadata records
the saved cell dimensions and zero transforms. Keep the PNG and sidecar together
to reopen the saved bitmap with its configured grid and raster choice. Opening
the PNG directly preserves exact pixels without applying raster conversion again.
Opening XML regenerates from the original source instead. PNG row calculations
include partially filled final rows and ranges shorter than one full row;
incompatible image/grid dimensions produce an error. XML source references
apply rendering transforms once, not again after the referenced source returns.

PNG export does not alter the live rendering settings or rerender before saving.
As with `.font`, the image/metadata are separate writes. The PNG preserves the
current visible atlas, including hand edits, but cannot recover alpha data
already discarded by the display. The XML recipe contains no hand-edit history.

For extensionless filenames, Save uses the selected format. Supported explicit
extensions take precedence, including uppercase variants. Tk derives its default
extension from the current filter so changing file type does not retain the
previous type's extension. Cancel writes nothing.

Gray levels already lost in a thresholded `.font` cannot be recovered from that
binary. Reopen the original image/vector font to regenerate them. RGBA2 export
and the color-picker restoration remain separate unfinished work under UI-006.

## Remaining lifecycle boundary

Successful opening replaces the current atlas. Main-form rendering changes still
regenerate from the source and can discard hand edits; a dirty-document/history
policy remains future work. The frozen audit's F01/F04 and other findings remain
historical evidence, with BUG-001 recording only the specific fixes above.

PNG loading assumes a uniformly tiled sheet: cell width is image width divided
by `chars_per_row`, and cell height is image height divided by the ceiling row
count for the configured character range. It does not detect glyph boundaries,
gutters or margins. The Import menu is a stub; a pitch-aware import setup as
part of opening a PNG remains a proposed workflow.

The author proposed a portable project bundle containing original artwork,
rendering settings and edited glyphs, with a separate explicit Agon export.
That document design remains for later discussion. It would address the current
split between source regeneration and hand-edited output, as well as portability.

## Regression checks

`tests/test_document_integrity.py` adds five checks covering failed opens,
successful read-only opens, batch isolation, transformed bitmap round trips and
preservation of live settings during export. Its bitmap probe removes DISPLAY
and WAYLAND_DISPLAY. GUI probes use actual Tk controls in disposable application
copies; file dialogs/error dialogs are mocked, and the broken color picker is
substituted only to exercise the existing color-change event.

`tests/test_quantized_save.py` adds four checks for fixed-level rendering,
PNG pixel/metadata round trips, format selection, and Tk's actual Linux save
dialog after changing its file-type filter. Rendering and PNG data checks also
run with display environment variables removed.

`tests/test_source_recipes.py` adds three checks covering PNG/TTF recipes with
transforms, XML-only saves, actual startup after export, missing sources, source
overwrite rejection, relative/cyclic references and live FONT controls with
new and legacy sidecars. Its source-rendering probes run without a display.
Earlier tests now distinguish direct bitmap round trips from XML regeneration.

Three additional checks in `tests/test_glyph_resampling.py` cover output-pixel
positioning, bounded sampling search and selected-character preview/application.

Two checks in `tests/test_atlas_resampling.py` additionally cover the global
command, per-glyph equivalence, complete application, cancellation and errors.

After the repository extension prerequisite, run the full 23-test suite from
the repository root with Xvfb/xvfb-run available:

```bash
xvfb-run -a -s '-screen 0 1920x1080x24 -dpi 96' \
  .venv/bin/python -m unittest discover -s examples/font_editor/tests -v
```

The tests do not operate on the author's current font, desktop windows or real
deployment destinations. Visual layout approval is separate from these checks.
