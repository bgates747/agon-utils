# MOS-01 — Fix missing-OBEY cleanup and prepare an upstream PR

## Summary

Fix MOS's unconditional close of an unopened stack-local FIL when OBEY path
resolution fails. Preserve the documented startup fallback behavior and prepare
an upstream PR with a minimal reproducer and regression evidence.

## State

Planned separately from SETUP-01. The subproject-root TODO.md owns task status.
The Author authorized recording this follow-up; implementation is not started.

## Work

- W01 [ ] Confirm the missing-file cleanup defect using the existing W06 trace
  and a minimal missing-OBEY reproducer in an isolated user-owned MOS checkout.
- W02 [ ] Implement safe cleanup that closes only a successfully opened file;
  inspect adjacent error paths for the same lifecycle issue within agreed scope.
- W03 [ ] Verify missing !boot.obey, missing autoexec.obey, fallback autoexec.txt,
  successful OBEY execution, and relevant path/open failures with raw SD images.
- W04 [ ] Prepare an upstream PR with source rationale, reproduction and regression
  evidence. Resolve required validation/commit approval before publishing changes.

## Evidence

See `SETUP-01/W06/tom-trace/REPORT.md` and its trace/image bundle. The observed
chain is main → mos_cmdOBEY → f_close → f_sync → validate. Missing !boot.obey
produces FR_NO_FILE before f_open; unconditional f_close dereferences stale
obj.fs=0xA26300. A populated !boot.obey bypassed this path in the controlled run.

## Boundaries

Use an isolated user-owned checkout; upstream reference checkouts remain
read-only. Headless validation is preferred. Retain stable subtask IDs and
explicit dispositions under the subproject task conventions.
