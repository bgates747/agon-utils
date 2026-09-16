# Run MOS tests

Start here for human use. [Editable startup bundles](startup.md) now run the
synthetic foundation controls through autoexec.txt, on the Linux bench with
headless raw SD images. Real MOS function cases and physical hardware qualification
remain later work. The current controls do not establish broad MOS correctness.

- [Emulator instructions](emulator.md): working build, image and automated smoke tools.
- [Hardware instructions/status](hardware.md): prerequisites and current limits.

Run `./human/mos-tests help` from the project root, or invoke that file by its
absolute Linux path from anywhere. Python helpers use agon-utils/.venv. On-device
helper applications will use C++ targeting AgonDev.

[Selection planning](planning.md) is now available separately from smoke execution.
It saves plans only; use the startup workflow above to execute synthetic controls.

[Register capture qualification](../docs/register-capture.md) is available through
`human/mos-tests capture-check`. It checks synthetic controls, not MOS conformance.

[Binary recording/checkpoint qualification](../docs/binary-recording.md) uses
`human/mos-tests recording-check` with a fresh output directory.

[Result reports](reports.md) are available through `human/mos-tests report`;
`report-check` qualifies the host decoder without launching an emulator.

[Foundation qualification](qualification.md) gives the complete synthetic check procedure and evidence limits.

[Restart recovery](recovery.md) explains interrupted-run blocking, read-only
inspection and current recovery limits.
