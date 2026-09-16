# Emulator smoke workflow

On the Linux bench, start at `/home/smith/Agon/mystuff/agon-utils/examples/mos-tests`.
The installed AgonDev release, existing repository .venv and dedicated .emulator
profile must be present; see [build guide](../docs/build.md) for toolchain paths.
The profile reuses the installed Fab 1.2.4 runtime and pinned MOS 3.0.2.

```sh
./human/mos-tests build
./human/mos-tests smoke --output .emulator/runs/my-first-smoke
```

Choose a fresh output directory every time. Existing directories are refused.
Read summary.txt first, then cpp/ and assembly/ result.json, build logs, captured
output and debugger transcripts. Each variant retains its raw image and before/
after identity. The helper builds fixtures, prepares images, runs headlessly,
checks output/return/stack/IX and closes the emulator. Exit zero means both smoke
variants passed; nonzero requires reading retained evidence. A failure can be a
fixture, infrastructure or target problem; do not automatically blame MOS.

For a separate image of the root C++ smoke binary:

```sh
./human/mos-tests image --output .emulator/my-smoke.img
./human/mos-tests debug --image .emulator/my-smoke.img
```

Build first. debug opens a headless interactive debugger stopped at reset; it is
not an automatic test. Type `exit` to close it. See the [debugger reference](../docs/emulator-debugging.md)
for commands; automation should use smoke instead. All qualification uses
--sdcard-img and !boot.obey, not hostfs. The future editable autoexec selection
workflow is designed but not delivered by these current smoke tools.
