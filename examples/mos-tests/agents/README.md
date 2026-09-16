# Agent entry point

Read ../AGENTS.md, HANDOFF.md and the authoritative subproject TODO first.
Use [human tools](../human/README.md), especially the [automated smoke procedure](../human/emulator.md),
without duplicating commands or implementation. The hardware route is explicitly
pending; do not infer deployment/flash authorization from an emulator request.

Verify Linux SSH access, the existing .venv, toolchain/profile prerequisites and
fresh output path. Run the shared human front end unattended with explicit
arguments; retain evidence on Linux. Inspect summary.txt and both result.json
files, not merely stdout. Nonzero exits require investigation. Report backend,
selection, firmware identity and evidence limits; do not label smoke as API-wide
coverage. Failed/incomplete evidence is never a pass.

For new automation read docs/test-strategy.md and docs/emulator-debugging.md.
Resolve paths relative to this project; debugger commands require PTY prompt
synchronization. Use the canonical profile wrapper and raw images. Close launched
processes on success/failure. Add unique agent helpers only when needed; this
scaffold reuses shared run_smoke.py and supplies no duplicate agent runner.

Use [selection planning](../human/planning.md) for saved synthetic plans. Never
report the planner's success or the target build as execution of selected tests.

[Register capture qualification](../docs/register-capture.md) is available through
`human/mos-tests capture-check`. It checks synthetic controls, not MOS conformance.

[Binary recording/checkpoint qualification](../docs/binary-recording.md) uses
`human/mos-tests recording-check` with a fresh output directory.

[Result reports](../human/reports.md) are available through `human/mos-tests report`;
`report-check` qualifies the host decoder without launching an emulator.

[Editable startup bundles](../human/startup.md) use the shared bundle/startup/
startup-check front ends. W06 is accepted; its checkpoint precedes W07.

For complete qualification, follow [the human procedure](../human/qualification.md). Run shared-profile emulator checks sequentially and retain all expected negative-case evidence.

Use [human recovery guidance](../human/recovery.md). Preserve stopped images;
never clear a journal or allocation counter to bypass the gate. Use the shared recover command for explicit dispositions, with a named actor,
reason, expected subject/generation, selected cases and confirmed prerequisites.
Never infer retry authorization from an incomplete report. Reuse recovery-check
and disposition-check; child reports do not replace parent findings.
