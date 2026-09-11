# AUDIT-001 — Audit application completeness, correctness, and maintainability

Status: **Accepted and closed — audit frozen.**
Created: 2026-09-10.
Completed: 2026-09-10.
Accepted: 2026-09-10. The author approved the audit as complete and directed
that it be frozen before discussing next steps. Preserve the report's findings
as the baseline; subsequent work belongs in separate linked records.
Report: [Application audit](../application-audit-2026-09-10.md).
History: [Development log](../development/2026-09-10.md).

Review the current Tkinter application, configuration schemas, native-library
integration, conversion paths, and assembly/deployment entry points. Identify
unfinished features, obvious defects, awkward product decisions, and structural
changes that would make future maintenance easier. Do not modify application
code, tests, or working configuration; do not commit anything.

1. [x] Inventory working, partial, disabled, and stubbed features and their paths.
   The report contains a feature matrix and distinguishes the live application
   from inventoried legacy scripts and unused prototypes.
2. [x] Audit file/data integrity, rendering/editing, UI/configuration events,
   font import/export, color tools, batch processing, and build/deployment.
   Findings F01–F26 cover these areas, including recent editing changes.
3. [x] Reproduce high-value defects in temporary copies where practical, clearly
   separating reproduced failures, source-proven defects, and suspected risks.
   Disposable fixtures confirmed edit loss, transformed save/reopen corruption,
   failed-open mutation, picker input-grab failure, native API mismatches, save
   dispatch failures, PNG/PSF issues, glyph spillover, batch event coupling,
   incorrect assembly lists, and destination deletion. No actual deployment ran.
4. [x] Produce a prioritized report with stable finding IDs, source references,
   impact, evidence, and incremental architectural recommendations.
   The linked report includes scope limits and future regression targets.
5. [x] Record the author's intent to embed glyph editing and restore color tools;
   leave implementation proposals deferred for later selection.
   UI-005 and UI-006 are linked from the root TODO. The grid/editor specification
   identifies the popup as interim behavior.

The audit covers recent changes as well as legacy code. Prior successful tests
are evidence for their narrow scenarios, not a claim that the whole app works.
