# RENDER-001 — Faithful positioning and per-character resampling search

Status: **Accepted — author reports improvement for most tested characters.**
Created and accepted: 2026-09-10. Global-command follow-up: [RENDER-002](RENDER-002.md).
Classification: **Ad-hoc task — completed and accepted.**
The author authorized committing this implementation at the end-of-session closeout.
Behavior: [Per-character Resampling Trial](../glyph-resampling.md).

The author approved a commanded per-character bounded sampling-phase search,
initially maximizing brightness. Positioning must remain faithful to the
specified offsets. First checkpoint existing progress (done: `c5f700d`); leave
this new experiment uncommitted for the author's trial.

1. [x] Separate output-pixel positioning from sampling. Isolate and scale each
   glyph, rasterize it, then position and clip it inside its own output cell.
   Old XML recipes retain legacy behavior until an explicit units conversion;
   switching units converts and displays the nearest equivalent integer offsets.
2. [x] Add a selected-character command searching ±1 source pixel in quarter-pixel
   steps (81 candidates). Include the unjittered render, break brightness ties
   by smallest jitter, and reject increased ink loss at the output boundary.
   The search never changes offsets, scale, cell size or other glyphs.
3. [x] Preview current/candidate glyphs, with Apply/Cancel. Apply writes edited
   pixels only. Invalidate a preview if its document, settings or pixels change.
   Keep search responsive and do not store its jitter parameters in metadata.
4. [x] Regress integer translations, clipping/isolation, deterministic search,
   bounds/ties, legacy compatibility and preview/save/cancel behavior. Document
   the persistence boundary and launch the app for the author's trial.
   All 21 checks pass under Xvfb. Trial launched with the current Concept 02 PNG,
   output units and converted offsets −3/−2 in memory; character A preview open.
5. [x] Author judged the trial helpful for most tested characters and requested
   a global command. Accepted and included in the authorized closeout commit.

Brightness is an experimental heuristic for white-on-black grayscale/quantized
or threshold glyphs; it can favour heavier strokes. This is not a general glyph
quality metric. PNG saves preserve applied pixels; XML regeneration still drops
hand edits. Project bundles, full undo and color tools remain separate work.
