# RENDER-002 — Optimize all characters from one global command

Status: **Completed and accepted.** Created and accepted: 2026-09-10.
Classification: **Ad-hoc task.** Removed from the unfinished-work index.
The author confirmed the global workflow worked well and authorized committing
the completed work. Behavior: [Font Resampling Optimization](../glyph-resampling.md).

The author accepted RENDER-001's results for most tested characters and requests
only a global operation in the UI. Retain individual preview code, but hide its
command. The author explicitly accepts regeneration discarding optimized edits.

1. [x] Add a global Optimize All Characters command, running the same independent
   bounded search for every character in the configured range. Read the source
   once; keep all offsets, settings, cell dimensions and selection unchanged.
2. [x] Keep Tk responsive with progress and Cancel. Prepare results separately;
   apply together only after successful completion to an unchanged document.
   Cancel, errors or document edits must not leave a partially optimized sheet.
3. [x] Remove the individual command from the UI while retaining its code and
   regression coverage. Save optimized pixels through the existing PNG path;
   rescaling continues to regenerate from source.
4. [x] Verify every result matches the individual search, partial rows/ranges,
   no metadata changes, cancellation/errors/stale document behavior and saving.
   Update specs/log and launch the app. Commit subsequently authorized at closeout.
   All 23 tests pass. A read-only 256-character run completed in 1.899 seconds.
   The updated desktop trial was launched with only the global command exposed.
5. [x] Author confirmed the global workflow worked well and requested task
   closeout and a commit. Individual functionality remains in code only.
