# W05 — BBC BASIC V ADL smoke test

Completed: Jeroen Venema's v1.0RC1 interpreter was rebuilt reproducibly, deployed
as bbc-basic-v-adl.bin, and executed a plain-text BASIC fixture from a raw SD
image. Exact output and return to MOS were verified headlessly, including a
repeat run using the saved preparation helper and a fresh image.

## Interpreter provenance

1. Source: `/home/smith/Agon/bbc-basic-v-adl`, origin
   `https://github.com/envenomator/agon-bbc-basic.git`, clean source commit
   `861085c472edbbb89080c3bd9cfd6a2a47360a62`, tag v1.0RC1.
2. Exported `git archive HEAD` into this task's ignored `source/` directory and
   built with `PATH=/home/smith/Agon/agondev/release/bin:$PATH make`.
   Upstream checkout was not modified. Build log is `build.txt`.
3. Rebuilt bytes match the pre-existing upstream build exactly: 25,499 bytes,
   SHA256 `ed6ff5a4707f941ff7b178111771a0bfade3ecdefccbb3bcb4015b9a6d5a87ab`.
   Retained as `bbc-basic-v-adl.bin` with `bbc-basic-v-adl.map`.
4. This is the pinned locally rebuilt v1.0RC1, not an assertion about the latest
   release. No other BASIC port is covered by this fixture.

## Fixture and invocation

`fixtures/smoke.bas` is CRLF plain text, not tokenized .BBC. It names its target
port, checks 6*7=42, prints a fixed pass marker, emits CR/LF with VDU, then QUITs.
The failure branch emits a distinct marker. This is a smoke check, not a broad
language or MOS conformance suite.

The raw-image `/!boot.obey` contains:

```text
SET KEYBOARD 1
cd /mystuff
load bbc-basic-v-adl.bin
run . smoke.bas
```

The dot in RUN selects the default execution address and passes smoke.bas to
BASIC. Its startup parser automatically CHAINs that filename. The first trial
omitted the dot and timed out; `trial-01-invalid-run-syntax.txt` preserves it.
The corrected form matches MOS's documented/default-address command behavior.

## Reproduce on Linux

From the subproject root, choose an image path that does not exist:

```bash
../../.venv/bin/python docs/tasks/SETUP-01/W05/prepare_basic.py --image "$PWD/.emulator/basic-new.img"
../../.venv/bin/python docs/tasks/SETUP-01/W05/run_basic.py --image "$PWD/.emulator/basic-new.img"
```

The preparer uses the shared image builder, installs the unambiguous interpreter
name and fixtures, removes the generic test.bin staging copy, reads every final
file back, and writes the final image/file hashes beside the image. The runner
uses the canonical wrapper with --sdcard-img through the headless entry point.
The preserved default W05 image is `.emulator/w05-basic.img`; the helper was
also validated with `.emulator/w05-reproduced.img`.

## Observation and evidence

1. `debugger.raw.txt` and `debugger.txt` retain the latest passing repeat run;
   `captured-output.bin` contains exactly `W05 BASIC PASS` followed by CR/LF.
2. `result.json` records the interpreter identity, raw-image backend, return
   PC 0x000D5F in MOS, HL=0, and emulator process exit zero.
3. The runner breaks at the pinned interpreter's final RET (0x0400D3), checks
   HL=0, single-steps RET, and confirms execution is back in MOS address space
   with HL still zero. It does not infer return from a printed marker alone.
4. The breakpoint derives from AGON_END=0x0400C3 and its verified epilogue.
   The runner pins the interpreter hash; update map/epilogue validation before
   testing a different build. This is a version-specific task harness.
5. `image-manifest.json` records the original executed image after final
   deployment verification; the reproduced image has its own adjacent manifest.
6. Consulted the selected interpreter README, docs/agonplatform.md,
   src/agon_init.s (AUTOLOAD/AGON_END), src/agon_os.s (BYE), and stock MOS
   src/mos.c (mos_cmdRUN default-address syntax).
7. No graphical confirmation or hardware test was performed. No process remains
   running and no commits/pushes were made. W07 will consolidate run metadata;
   these task-local scripts/fixtures can be promoted once the suite interface
   is established.
