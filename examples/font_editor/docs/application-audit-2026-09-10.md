# Font Editor Application Audit — 2026-09-10

Status: **Accepted as complete and frozen by the author on 2026-09-10.**
Preserve this report and finding IDs F01–F26 as the audit baseline. Record later
discoveries, corrections, and implementation decisions in separate dated
documents or linked tasks rather than rewriting this snapshot. Acceptance of
the audit does not authorize implementation of its recommendations.

Completed under [AUDIT-001](tasks/AUDIT-001.md). This is a findings report,
not authorization to change implementation or a second task backlog. The
[root TODO](../TODO.md) remains the sole index of promoted unfinished work.
No application code, tests, or working configuration was changed for this audit.

## Assessment and intended product

The app has a useful conversion core and a working basic bitmap-editing path,
but it does not yet have a reliable editable-document lifecycle. Source files,
render settings, displayed pixels, saved pixels, and recent-file preferences
can disagree. That is the main source of both bugs and structural complexity.
The most urgent issues are silent loss of edits, inconsistent save/reopen
behavior, and destructive destination copying. Restoring color tools requires
more than re-enabling their UI: several native calls and dialog contracts are
broken.

1. The author confirmed that character editing works again. The separate glyph
   window is an **interim implementation**. The intended editor is a pane inside
   the main application, recorded in [UI-005](tasks/UI-005.md).
2. Palette selection, hue/color selection, selection feedback, and
   foreground/background picking are intended features. Their disabled or broken
   state reflects unresolved debugging, not a decision to remove color support.
   Eventual restoration is recorded in [UI-006](tasks/UI-006.md).
3. The accepted application-size preference and atlas zoom through 800% remain
   current behavior. Desktop/per-monitor detection remains deferred in UI-002.
   The audit does not propose replacing Tkinter merely to solve the structural
   problems below.

## Scope and evidence

Reviewed the application entry point, views, menu, generated configuration
controls and XML schemas, configuration persistence, font codecs and transforms,
color picker and palette helpers, batch conversion, and assembly/deployment
entry points. The Python directory contains 18 modules, including unused
prototypes. Inspected the relevant current `agonutils` exports and image API
implementation. Inventoried the separate legacy `scripts/` conversion/build
utilities; those scripts and the assembly runtime were not exhaustively executed
or independently qualified by this desktop-application audit.

**R — reproduced:** exercised the actual functions in temporary fixtures or
temporary copies of the application. **S — source-proven:** a concrete defect
or incomplete implementation is visible in the current code; its complete UI
path was not exercised. **Risk:** plausible impact needs a targeted follow-up.

**P1** means data integrity, destructive side effects, or a blocked core
workflow. **P2** means incorrect behavior, incomplete features, or material
maintenance costs. **P3** means lower-priority cleanup. These are proposed
triage priorities, not implementation commitments.

The repository extension prerequisite,
`.venv/bin/python tests/test_agonutils.py`, passed during the audit. Temporary
probes used the existing test fixture copier, a withdrawn Tk root, disposable
images/fonts/configuration, and mocked file-dialog responses. SD-copy testing
used two disposable directories; no actual SD destination, assembler, or
emulator was used. No new application instance was launched against the user's
working document. Existing six integration tests provide earlier evidence for
UI scaling and simple 8×8 editing/export; they do not cover the failures below.

## Feature inventory

| Area | Current state | Relevant findings |
| --- | --- | --- |
| Application UI scaling | Accepted manual preference, restart required; scrollable forms | UI-001 complete; UI-002 deferred |
| Atlas navigation | Working tested zoom 25–800%, scrolling, selection, grid, partial rows | F18: large-workload limits remain |
| Glyph editing | Working basic foreground/background pixel toggle; separate window | UI-005; F01, F13 |
| TTF/OTF import | Implemented; raster dimensions and bearings are fragile | F09, F10 |
| PSF import | Implemented bitmap path; format and character mapping incomplete | F11, F12 |
| PNG atlas import | Implemented; partial-row geometry broken | F08 |
| Agon `.font` import/export | Simple fixture round trip works; transformed/document cases unsafe | F02–F04, F12 |
| RGBA2 | Advertised open path unsupported; save path blocked by native API mismatch | F05, F06 |
| PNG save | Advertised, no save dispatcher implementation | F05 |
| XML load/save | Settings recipe, not a complete edited-font document | F02–F04, F17 |
| Color tools | Substantial dormant/partial implementation; currently fails at construction | F06, F07, F13–F15; UI-006 |
| Import/Export menu actions | Stubs distinct from File Open/Save conversion paths | F16 |
| Undo/Redo/Revert | Visible stubs; no edit history or recovery | F01, F16 |
| About/Help | Visible stubs; no contextual guidance | F16 |
| Batch conversion | Loop and output writers exist; state, geometry and reporting defects | F19, F20 |
| Assembly/deployment | Generator and SD copy active; assembly/emulator copy disabled; launch active | F21–F23 |
| Configuration-driven UI | Widget construction works; behavior rules only partially connected | F17, F24 |
| Legacy utilities/prototypes | Separate overlapping pipelines and experiments | F26 |

## Findings

### F01 — P1 — R/S: Rerendering silently discards hand edits

[`image_display.py`](../src/python/image_display.py), `update_pixel` and
`render_font`; [`font_config_widget.py`](../src/python/font_config_widget.py),
`default_redraw_font_handler`; [`menu_bar.py`](../src/python/menu_bar.py).

Pixel edits live only in `ImageDisplay.working_image`. Rendering reads
`current_font_file` again and replaces that image. In the fixture, editing A
changed the pixels; calling `render_font()` restored the original bytes exactly.
Controls wired to rerender therefore erase edits as a side effect. There is no
dirty flag, edit history, or save/discard guard for open/exit. Batch controls can
also invoke this path (F19). A document model must own edits, with explicit
semantics for applying new rendering settings and regenerating from a source.

### F02 — P1 — R/S: Opening a file changes state and writes metadata before validation

[`file_manager.py`](../src/python/file_manager.py), `open_file`, lines 39–78.

Open changes recent-file preferences, `current_font_file`, the title and controls,
and writes the existing sidecar or shared `font_config.xml` before rendering
succeeds. Opening a deliberately broken TTF raised `OSError` after its path had
replaced both current/recent state and been written into default metadata. A
read operation can rewrite user metadata even on failure. Loading should first
produce a validated candidate document, then replace current state; preference
updates should follow success and opening should not implicitly save metadata.

### F03 — P1 — R: Saved transformed fonts do not preserve their pixels on reopen

[`file_manager.py`](../src/python/file_manager.py), `save_agon_font`, lines
106–132; [`agon_font.py`](../src/python/agon_font.py), `read_agon_font`,
`read_font`, `resample_and_scale_image`.

Export writes the transformed raster while retaining original cell dimensions
and transformation settings in its sidecar; normalization code is commented
out. The reader builds cells using `font_width_mod` but returns the original
configuration, after which the transform slices using `font_width`. A fixture
widened from 8 to 9 pixels saved and reopened at the same 144-pixel atlas width,
but its pixels differed. Correct dimensions alone do not prove a correct round
trip. Exported bitmap metadata must describe the bitmap actually written;
source-render recipes should be stored separately.

### F04 — P1 — R/S: Configuration and file identity have competing authorities

[`agon_font.py`](../src/python/agon_font.py), `read_font`, lines 28–38;
[`file_manager.py`](../src/python/file_manager.py), `open_file`, `save_file`,
`save_agon_font`.

For a `.font` with a sidecar, every render reloads that sidecar over the supplied
control values: requesting `offset_width=2` returned `0` in the fixture. XML
opening follows `original_font_path`; exported sidecars retain the original
source path, so opening the XML can regenerate the source instead of loading
the edited export. XML save itself stores configuration only, not edited pixels.
Save updates `most_recent_file` but leaves `current_font_file` and the title
pointing at the old document. `current_font_xml_file` is assigned only in one
open branch and can also become stale. Define source, document, and export
identities explicitly instead of treating any one of these paths as all three.

### F05 — P1 — R/S: Save and Open advertise unsupported format paths

[`file_manager.py`](../src/python/file_manager.py), `get_open_filename`,
`save_file`, `get_save_filename`; [`agon_font.py`](../src/python/agon_font.py),
`read_font`.

Saving `out.png` raises `NotImplementedError`. Saving an extensionless name
appends `.xml`, but returns the original whole path as the supposed file type
and raises another `NotImplementedError`. The selected dialog filter is never
captured. RGBA2 appears in Open but has no reader dispatch branch. Use one
format-capability registry for dialogs and codecs; distinguish unavailable
formats visibly until implemented, and derive filename/type consistently.

### F06 — P1 — R: Python/native API drift blocks color picking and RGBA2 export

[`agon_color_picker.py`](../src/python/agon_color_picker.py),
[`make_palette.py`](../src/python/make_palette.py),
[`agon_font.py`](../src/python/agon_font.py), `write_rgba2_font`;
[`agonutils.c`](../../../src/agonutils.c), method table;
[`images.c`](../../../src/images.c), `_parse_palette_conversion_args`.

The installed extension lacks `rgb_to_hsv`, `rgb_to_cmyk`, `hsv_to_rgb`,
`cmyk_to_rgb`, `process_image_with_palette`, and `find_nearest_color_rgb`, which
the palette/picker code calls. Picker construction fails on the first of these.
RGBA2 export calls `img_to_rgba2` with two arguments; the current implementation
requires source, destination, palette file, and conversion method. It raises
`TypeError` at the missing third argument. Establish a small tested adapter to
the supported extension API; some scalar color conversion belongs naturally in
Python rather than requiring restoration of every historical native symbol.

### F07 — P1 — R: A failed color-picker constructor leaves a modal input grab

[`agon_color_picker.py`](../src/python/agon_color_picker.py), `__init__`,
lines 18–37.

`grab_set()` happens before palette loading and other fallible initialization.
After the missing-native-function exception, `root.grab_current()` still
returned the orphaned picker. This is a demonstrated mechanism for an apparent
application freeze in the color workflow; it does not establish the cause of
the earlier glyph-click report. Initialize successfully before acquiring input
and guarantee destruction/release on failure.

### F08 — P2 — R: PNG import miscalculates partial rows

[`agon_font.py`](../src/python/agon_font.py), `read_png_font`, lines 469–481.

Height calculation uses floor division for the number of rows. One glyph with
16 columns divides by zero. A 128×16 atlas containing 17 8×8 cells reports a
16-pixel glyph height instead of 8. Use the same ceiling row calculation as
atlas layout, and reject incompatible image dimensions with a useful error.

### F09 — P2 — R: Glyph offsets can move ink into neighboring glyphs

[`agon_font.py`](../src/python/agon_font.py), `resample_and_scale_image`,
lines 71–97.

Position offsets apply to the entire source atlas before individual cells are
cropped. In a two-cell fixture with 2×1 cells, shifting right by one moved the
first glyph's rightmost white pixel into the second glyph. Transform each glyph
inside its own bounded cell. Also review final paste clipping when offsets make
the target cell smaller than the pasted image.

### F10 — P2 — R/S: TTF rasterization clips large glyphs and ignores bearings

[`agon_font.py`](../src/python/agon_font.py), `render_ttf_chars`, lines 241–283.

Every glyph is first drawn on a fixed 64×64 scratch image at `(0, 0)`. At the
permitted point size 128, bundled Arial's A has bounding box `(-1, 24, 86, 116)`;
the renderer returns a clipped 64×64 extent. Negative bearings can also be cut
off. Derive scratch bounds from font metrics and define baseline/alignment for
the common bitmap cell. Empty/all-blank ranges also need explicit dimensions
instead of allowing measured zero-sized cells.

### F11 — P2 — R/S: PSF2 parsing mishandles extended headers and Unicode maps

[`agon_font.py`](../src/python/agon_font.py), `read_psf2`,
`extract_unicode_table`, lines 416–462.

The reader ignores `header_size` and reads bitmaps immediately after byte 32.
A valid 36-byte header followed by bitmap `80` produced glyph byte `41` from
the extra header instead. Unicode parsing treats the first byte as a glyph
index and following pairs as native-endian integers. The minimal table
`41 FF 42 FF` produced `{65: [17151]}` rather than mapping positions 0 and 1
to A and B. PSF2 uses a bitmap offset, little-endian header integers, and
UTF-8 mappings terminated per glyph. Those requirements are specified by the
[kbd project format documentation](https://kbd-project.org/docs/font-formats/font-formats-1.html).
The current native-endian signed header format is also unsuitable as a portable
format definition. Validate headers and bitmap lengths before allocation/read.

### F12 — P2 — R/S: Truncated fonts and incompatible character ranges are accepted

[`agon_font.py`](../src/python/agon_font.py), `read_agon_font`,
`read_psf1`, `render_psf_glyphs`, `write_agon_font`, `write_rgba2_font`;
[`font_config_editor.xml`](../src/python/font_config_editor.xml).

An empty `.font` file loaded as a blank 128×128 atlas instead of reporting
missing data. Raw and PSF readers lack complete expected-length validation.
The controls allow character codes through 65536, while the binary writers
emit 256 positions; glyphs outside that range cannot be represented by these
writers. PSF rendering uses positional glyph indexes, while TTF uses `chr()`;
the parsed PSF Unicode mapping is not used. Define font glyph identity and
target encoding separately, and validate representability when exporting.

### F13 — P1 for color restoration — S: Alpha and foreground/background semantics are inconsistent

[`image_display.py`](../src/python/image_display.py), `render_font`;
[`editor_widget.py`](../src/python/editor_widget.py), pixel toggle;
[`agon_font.py`](../src/python/agon_font.py), raster conversion and export;
[`font_config_widget.py`](../src/python/font_config_widget.py), `choose_color`;
[`images.c`](../../../src/images.c), `_parse_transparent_color`.

The main preview converts to RGB, discarding alpha. Palette conversion also
saves an RGB intermediate. The pixel editor toggles between two configured
colors and compares RGB components; that is not yet a general multicolor brush
model. The picker caller preserves the old alpha regardless of selected alpha.
The native transparency parser actually expects RGBA and enables color-key
transparency for alpha 255, although the exported docstring describes RGB;
the picker passes opaque black with a comment claiming no transparency.
Specify RGBA storage, brush behavior, threshold output, palette output and
color-key transparency once, and verify the complete preview-to-export path.

### F14 — P2 — S: Color-dialog initialization and dismissal do not honor their API

[`agon_color_picker.py`](../src/python/agon_color_picker.py), `__init__`,
`update_selected_color`, `on_ok`, `on_cancel`, `askcolor`.

The supplied initial `color` is ignored. `selected_hex` is initialized to None
and never assigned a selected value; `selected_rgb` actually contains RGBA.
Window-manager close is not routed through Cancel, so it can return the last
selection as if accepted. These bugs remain after native compatibility is
fixed. Define one return contract and make Cancel/Escape/window-close preserve
the caller's original color.

### F15 — P2 — S: Picker image state, canvas use, and palette validation are fragile

[`agon_color_picker.py`](../src/python/agon_color_picker.py),
`on_hue_selected`, `set_color_from_pixel`, `update_selected_color`,
palette-grid methods; [`make_palette.py`](../src/python/make_palette.py),
`read_gimp_palette` and palette column parsing.

Hue changes replace `image_data`, but `set_color_from_pixel` reads the older
`color_picker_image_pillow`, so initialization can choose a stale color.
Repeated interactions create additional canvas image items instead of reusing
them. Palette selection reparses disk data and click paths lack complete edge
checks. Blank palette lines can index missing fields; missing column counts or
empty palettes can fail grid calculations. Keep one image/state per view,
validate a palette once, and handle blank margins and malformed palettes.

### F16 — P2 — S: Visible commands promise features that do nothing

[`menu_bar.py`](../src/python/menu_bar.py), lines 78–139;
[`file_manager.py`](../src/python/file_manager.py), duplicate action stubs;
[`font_editor.py`](../src/python/font_editor.py), component construction;
[`config_editor.py`](../src/python/config_editor.py), `create_buttons`.

Import, Export, Revert, Undo, Redo, About and Help are `pass` implementations.
There is no New-document workflow. The console is disabled behind `if False`,
yet errors and progress go primarily to `print`; the normal form exposes
“Print Current Values.” Separate real user commands from developer diagnostics,
and make unavailable commands visibly unavailable until their behavior exists.
Actual File Open/Save implementations should not be confused with the separate
stubbed Import/Export commands.

### F17 — P2 — S: Configuration parsing lacks one validated schema and recovery policy

[`config_manager.py`](../src/python/config_manager.py), `load_xml`,
`xml_to_dict`, `xml_values_to_dict`, `generate_blank_font_config`;
[`font_config_widget.py`](../src/python/font_config_widget.py), numeric controls.

There are overlapping XML serialization/loading approaches. `load_xml` prints
errors and returns None, which downstream parsing does not consistently handle.
`xml_values_to_dict` uses defaults for type lookup but does not merge absent
values; the blank configuration starts with None values. Per-field limits do
not validate relationships such as start ≤ end or positive final cell sizes.
Use a typed settings object with defaults, schema version/migration, validation
at the boundary, and actionable errors while retaining the last valid document.

### F18 — P2 — Risk: Rendering work can still overwhelm Tk's event loop

[`image_display.py`](../src/python/image_display.py), `redraw`, `update_pixel`,
`render_font`; [`agon_font.py`](../src/python/agon_font.py), transforms;
[`font_config_editor.xml`](../src/python/font_config_editor.xml).

The recent canvas fixes bound item growth in the tested grid path, but large
font rendering and whole-atlas zoom resampling still run synchronously. One
pixel edit redisplays the enlarged atlas. Large character ranges, cell sizes
and 800% zoom can produce expensive allocations and event-loop stalls. No
worst-case stress/OOM test was attempted. Bound work and allocation sizes,
debounce repeated controls, cache display images, and use cancellable background
jobs for expensive data processing with Tk updates on its owning thread.

### F19 — P1 — R: Editing batch settings rerenders the main document

[`batch_convert_dialog.py`](../src/python/batch_convert_dialog.py),
[`batch_convert_dialog.xml`](../src/python/batch_convert_dialog.xml),
[`font_config_widget.py`](../src/python/font_config_widget.py),
`default_redraw_font_handler`.

Generic controls reach through `parent.app_reference.image_display`. In a
temporary batch dialog, incrementing its point size from 16 to 17 called the
main display's `render_font()` once, while the main point size remained 16.
This is an unrelated-document mutation path and combines with F01 to lose edits.
Each form needs an explicit change callback scoped to the model it edits.

### F20 — P2 — S: Batch output geometry and completion reporting are unreliable

[`batch_convert_dialog.py`](../src/python/batch_convert_dialog.py),
`on_go`, `generate_file_list`.

After rendering with offsets/scales, batch conversion sets modified dimensions
back to the base dimensions. PNG can therefore contain transformed cells while
the binary writer slices with different geometry. Recursive conversion flattens
names, so equally named fonts can overwrite one another. Extension matching is
case-sensitive. Per-file exceptions are printed, then the dialog closes without
a success/failure summary; there is no progress, cancellation, or empty-input
feedback. Share the validated single-font conversion/export path, preserve
identity, and return structured results.

### F21 — P2 — R: Assembly font-list generation selects the wrong files and paths

[`asm_config_editor.py`](../src/python/asm_config_editor.py),
`build_fonts_asm`, lines 49–127.

The file-processing loop is outside `os.walk`, so it sees only the last visited
directory's `files`/`root`. With a top-level font and a nested font and
`recursive=False`, the fixture omitted the top-level font and included the
nested one. Filename construction concatenates directory and basename without
a separator, producing `"fontschild.font"`. Nested basename-derived labels can
also collide. Build from an explicit validated file list and normalize target
paths and unique labels before generating assembly.

### F22 — P1 — R: SD copying deletes unrelated destination contents

[`asm_config_editor.py`](../src/python/asm_config_editor.py),
`build_and_deploy_fonts.copy_to_directory`, lines 250–279, and SD dispatch.

Before its filtered `.bin`/`.font` copy, the routine deletes the entire existing
destination tree using `shutil.rmtree`. In disposable source/destination
directories, an unrelated destination text file was removed and the new binary
was copied. There is no source/destination overlap guard. A targeted artifact
deployment operation should preserve unrelated files and reject invalid or
overlapping paths; failure should leave the prior deployment recoverable.
No real SD card was involved in this audit.

### F23 — P1 — S: Build/deploy controls can launch without assembling or copying

[`asm_config_editor.py`](../src/python/asm_config_editor.py),
`DoAssemblyDialog`, `build_and_deploy_fonts`, lines 172–323;
[`asm_config_editor.xml`](../src/python/asm_config_editor.xml).

Assembly and emulator copying are commented out but their UI flags remain.
Emulator launch remains active, so GO can launch stale output after merely
printing that assembly/copying is disabled. The helper rewrites autoexec,
changes process-wide working directories, and can call `sys.exit` on errors.
Assembly dialog values are not persisted through a dedicated Set implementation.
Launch configuration is legacy and needs reconciliation with current canonical
profile tooling before restoration. Separate build, deployment and launch
results, require each prerequisite to succeed, and surface errors in the app.
This source review did not execute or validate emulator behavior.

### F24 — P2 — S: XML-driven behavior is silently only partly implemented

[`config_editor.py`](../src/python/config_editor.py), `create_widgets`,
`set_visible`; [`font_config_widget.py`](../src/python/font_config_widget.py),
`trigger_event_handlers`, `raster_type_on_change_handler`; the form XML schemas.

Visibility rules are collected but not connected to initialization or control
changes. Handler names are resolved by `getattr` and missing handlers are
silently ignored. XML hover handlers/descriptions do not create functioning
help. Derived metadata is presented with ordinary editable controls without a
consistent ownership rule. Data-driven forms are useful, but arbitrary string
method names and widget-parent traversal obscure their behavior. Validate
schema/action references at startup and make each form's controller explicit.

### F25 — P2 — S/Risk: Persistent and temporary files share the source tree

[`agon_font.py`](../src/python/agon_font.py), palette and RGBA2 intermediates;
[`agon_color_picker.py`](../src/python/agon_color_picker.py), image paths;
[`config_manager.py`](../src/python/config_manager.py), XML persistence;
[`font_editor.py`](../src/python/font_editor.py), startup paths.

Preview and conversion use shared fixed `temp.png`/`temp.rgba2` names; color
tools write fixed PNGs and `temp_palette.gpl` beside code. Separate windows or
instances can overwrite or delete one another's intermediates. Some resource
paths use `__file__`, others require launching from the subproject directory.
Configuration writes replace files directly rather than atomically. Separate
read-only bundled resources, user preferences, document metadata and per-job
temporary files; use in-memory images where possible. Concurrent-instance and
interrupted-write failures were identified as risks, not reproduced.

### F26 — P3 — S: Prototypes, repeated mechanisms and mixed responsibilities obscure ownership

[`temp.py`](../src/python/temp.py), [`spreadsheet.py`](../src/python/spreadsheet.py),
[`make_palette.py`](../src/python/make_palette.py), [`scripts/`](../scripts/),
plus the active modules above.

Experimental spreadsheet/evaluation code, commented implementations and legacy
asset scripts sit near runtime code without a clear maintained/archived boundary.
There are multiple overlapping font conversion, palette conversion and XML
mechanisms. `agon_font.py` combines decoding, transforms, rasterization, binary
encoding, diagnostics and disk-backed native conversion; assembly GUI code
contains deployment orchestration. These are concrete extraction boundaries.
Inventory callers before removing anything; unused prototypes are not evidence
of a reachable GUI vulnerability. Move or retire them deliberately rather than
letting experiments appear to be supported features.

## Maintainability direction

These are architectural recommendations, not additional work checklists.

| Responsibility | Proposed owner/boundary | Why it helps |
| --- | --- | --- |
| Editable document | Source identity, glyph images, encoding, settings, dirty state and history | Views stop serving as the database; save/open becomes transactional |
| Import/export | Format registry and pure validated codecs, with explicit metadata rules | Dialog promises match capabilities; batch and interactive output agree |
| Rendering | Per-glyph transforms and cached derived previews | Prevents cross-glyph contamination and makes edit/rerender semantics testable |
| Configuration | One typed schema with defaults, migration and cross-field validation | Removes duplicated parsing and invalid intermediate state |
| UI composition | Main controller plus atlas, embedded editor and configuration/palette panes | Implements UI-005 and removes nested parent/app-reference dependencies |
| Color support | Palette service and a small native adapter with an explicit RGBA contract | Makes UI-006 testable without entangling file generation and dialog lifecycle |
| Long-running work | Data-only jobs with progress/cancel; Tk-owned UI updates | Prevents expensive conversions from monopolizing interaction |
| Build/deploy | Independently callable services with explicit inputs, outputs and failure results | Eliminates global CWD changes, hidden disabled stages and broad deletion |

A sensible sequence is to establish document/save integrity and contain
destructive deployment first; then embed the editor on that model and restore
color through a tested adapter; then consolidate codecs/transforms, batch jobs
and configuration machinery. Each step can retain the working UI while replacing
one responsibility. There is no evidence here that a framework rewrite would
be a better first step.

## Follow-up verification targets

Before implementing fixes, promote selected findings into tasks in the root
TODO. The most valuable future regression coverage exercises user-visible
boundaries: dirty edit → settings change/open/close; transformed save → reopen
with exact pixels and bytes; failed open/save retaining the previous document;
color initialization/OK/Cancel/window-close/exception with no residual grab;
RGBA and palette preview/export agreement; partial-row and malformed fonts;
batch settings isolated from the main document; and deployment preserving
unrelated files and refusing overlapping paths. The existing basic editor and
scaling tests should remain useful during those extractions.

The audit probes and JSON output were kept under `/tmp` and are disposable.
The concrete fixture inputs, observed outcomes and source locations above are
the durable evidence. Findings labeled S or Risk still need targeted execution
when their implementation work is selected.
