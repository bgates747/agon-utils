# Run MOS tests

Start here for human use. Current tools run the accepted C++/assembly smoke
comparison on the Linux bench, headlessly using raw SD images. The general MOS
case runner, editable full-suite autoexec.txt bundle and on-device decoder are
not implemented yet. These smoke checks do not establish broad MOS correctness.

- [Emulator instructions](emulator.md): working build, image and automated smoke tools.
- [Hardware instructions/status](hardware.md): prerequisites and current limits.

Run `./human/mos-tests help` from the project root, or invoke that file by its
absolute Linux path from anywhere. Python helpers use agon-utils/.venv. On-device
helper applications will use C++ targeting AgonDev.

[Selection planning](planning.md) is now available separately from smoke execution.
It saves plans only; the general runner does not execute tests yet.

[Register capture qualification](../docs/register-capture.md) is available through
`human/mos-tests capture-check`. It checks synthetic controls, not MOS conformance.

[Binary recording/checkpoint qualification](../docs/binary-recording.md) uses
`human/mos-tests recording-check` with a fresh output directory.

[Result reports](reports.md) are available through `human/mos-tests report`;
`report-check` qualifies the host decoder without launching an emulator.
