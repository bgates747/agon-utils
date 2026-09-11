# Font Resampling Optimization

The search was accepted under [RENDER-001](tasks/RENDER-001.md). Its global
command was accepted under [RENDER-002](tasks/RENDER-002.md). Brightness remains
an experimental heuristic, not a claim of optimal typography.

## Positioning

`Position Units = output` isolates each source glyph, scales it using bicubic
resampling, rasterizes it, then translates it by exactly `offset_left` and
`offset_top` whole output pixels inside its own cell. Positive offsets move
right/down. Neither position offset changes sampling phase. Cell dimensions
remain base + scale + width/height offset. Pixels outside that cell are clipped;
they cannot spill into adjacent glyphs or rows. Atlas zoom remains independent.

New files without metadata use output units. Existing XML without
`position_units` retains `source` units and the historical rendering path,
including its known sheet-offset artifacts, so opening a recipe does not
silently reinterpret its coordinates. Selecting a different Position Units
value explicitly converts each position offset using the scaled/base dimension
ratio and rounds to the nearest integer (ties to even), then rerenders. The
converted offsets are visible in the controls. This conversion can round away
fractional placement and is not guaranteed reversible. Saving records units in
the recipe; bitmap metadata uses output units with zero transforms.

## Optimize all characters

1. Select output Position Units and the desired cell size/position. Use white
   foreground on opaque black, with quantized, grayscale or threshold rendering.
2. Choose **Optimize All Characters** beside the atlas zoom controls. The
   command searches every character in the configured range independently.
3. A progress window offers **Cancel**. After successful completion, all winning
   glyphs replace the working pixels together; the atlas and open glyph editor
   refresh. Cancel, errors or changed document/settings/pixels discard pending
   results. Selection and rendering settings are not changed by this operation.

The individual-character preview and its Apply/Cancel implementation remain in
code with regression coverage, but have no UI command. This is intentional at
the author's request. There is no per-character confirmation in the global run.

The command decodes the original source once, isolates each glyph, and tests
81 sampling phases: horizontal and vertical shifts from −1 to +1 source pixel
in quarter-pixel steps. Sampling uses background padding and a fractional resize
box in a single bicubic resampling pass. No neighbouring source pixels enter
the filter. The zero phase is included and matches ordinary output-mode rendering.

Each candidate is rasterized, positioned at the unchanged integer offsets and
clipped to the unchanged output cell. The score is summed visible grayscale
brightness. A candidate is rejected if its rasterized ink loss outside the
output cell exceeds the zero-phase loss. Among equal scores the smallest phase
distance wins, then a fixed coordinate order. Blank glyphs retain zero phase.
No centering, offset adjustment or cell resizing occurs. The global operation
assembles independent per-glyph winners; it does not search for one phase shared
by the whole sheet. Unused cells in a partial final row retain their pixels.

Search runs in small Tk event-loop batches bounded by time and phase count.
Changed source path, render settings, image dimensions or working pixels
invalidate the global run. Merely selecting a different character is allowed.
Duplicate command invocations raise the existing progress window. Errors are
shown there without applying partial results.

## Persistence and limits

Search parameters and chosen phases are not written into metadata. Completion is a
pixel edit. Save PNG preserves it; directly opening that exported PNG restores
the saved pixels. Changing rendering settings or reopening the XML recipe
regenerates from source and discards edits, including these optimizations. The
project-bundle/dirty-document design remains separate work. Search always uses
the original source; it does not optimize an already hand-edited working glyph.

The author explicitly accepts that rescaling discards optimized working pixels.
Higher brightness can favour heavier strokes or closed counters. The clipping
check limits ink lost at output-cell boundaries; it does not establish glyph
legibility, topology preservation or correct visual weight. The global command
applies the heuristic automatically; the author judges the resulting atlas.

## Verification

`tests/test_glyph_resampling.py` checks exact translations across three raster
modes, clipping at cell/row boundaries, source immutability, offset conversion,
bounded deterministic search, blank ties, clipping limits and unsupported modes.
Its Tk probe checks Cancel during search, Apply, unchanged metadata/settings,
unmodified neighbours, editor refresh, stale-selection rejection, PNG pixels
and the units-conversion handler. Pure rendering probes remove display variables.
The individual preview test invokes its retained method directly and verifies
its button is absent. `tests/test_atlas_resampling.py` additionally checks global
results against individual winners, progress counts, nonzero character ranges,
partial rows, cancellation after a private winner exists, injected mid-run errors,
stale edits, duplicate invocation, automatic application, selection/editor state,
PNG persistence and regeneration. The full suite command is in
[document-io.md](document-io.md).
