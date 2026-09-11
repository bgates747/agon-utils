# Font Editor Entry Point

Read the repository-root [`AGENTS.md`](../../AGENTS.md) and
[`codex-workflow-notebook.md`](../../codex-workflow-notebook.md), including
their canonical environment guidance, before working here.

This subproject is the desktop Tkinter font editor for Agon font assets.
Its entry point is `src/python/font_editor.py`; configuration is XML-based.
Use the agon-utils repository's `.venv` as directed by the repository handoff.
Current UI behavior is specified in [`docs/ui-scaling.md`](docs/ui-scaling.md).
Atlas and character editing behavior is specified in
[`docs/font-grid-editor.md`](docs/font-grid-editor.md).
Opening, bitmap export and batch-form isolation are specified in
[`docs/document-io.md`](docs/document-io.md).
Output positioning and the per-character resampling trial are specified in
[`docs/glyph-resampling.md`](docs/glyph-resampling.md).
The [2026-09-10 application audit](docs/application-audit-2026-09-10.md)
records known defects, incomplete features, and proposed maintenance boundaries.
It is findings evidence, not authorization to implement its recommendations.

[`TODO.md`](TODO.md) is this subproject's single authoritative unfinished-work
index. Task details and lifecycle conventions live in
[`docs/tasks/README.md`](docs/tasks/README.md). Read the relevant task before
implementation. Keep reusable environment guidance in the canonical repository.
