# Documentation

Current project operation lives in `../HANDOFF.md`; project intent lives in
`../README.md`. `../TODO.md` owns unfinished work. Task records live in
`tasks/`, and chronological evidence and decisions live in `development/`.
Promote recurring task outputs into subject-named documentation or tools when
accepted; keep task records as provenance.

See [emulator debugging](emulator-debugging.md) for headless launch, commands,
triggers, diagnostic hooks, automation, and test-integration patterns.

The [MOS API inventory](mos-api-inventory.md) is a compact map to pinned upstream
contracts plus project findings. Upstream owns API descriptions. Check target
identities before using it; task archives are historical evidence only.

[Provisional runner design](provisional-runner-design.md) records startup-script,
selection, menu and reporting ideas; it is not a runnable procedure.

[Provisional result design](provisional-result-design.md) records binary evidence,
frequent checkpoints, text decoding and the verified baseline SRAM mapping.

The [coverage matrix](mos-coverage-matrix.md) defines proposed case families and
backend requirements; it contains no executed-case results.

[Test strategy](test-strategy.md) is the current W03 implementation design and
supersedes the provisional runner/result notes. Component guides below describe
implemented capabilities and qualification limits.

[Result format v1](result-format-v1.md) owns exact runner data contracts;
fixtures/format-v1 holds independent known-answer bytes and report/capture oracles.

[Register capture qualification](register-capture.md) is available through
`human/mos-tests capture-check`. It checks synthetic controls, not MOS conformance.

[Binary recording/checkpoint qualification](binary-recording.md) uses
`human/mos-tests recording-check` with a fresh output directory.

[Result reports](../human/reports.md) are available through `human/mos-tests report`;
`report-check` qualifies the host decoder without launching an emulator.

[Editable startup bundles](../human/startup.md) use the shared bundle/startup/
startup-check front ends. W06 is accepted; its checkpoint precedes W07.
