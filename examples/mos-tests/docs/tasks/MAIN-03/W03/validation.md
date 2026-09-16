# MAIN-03 W03 — capture qualification

PASSED: all 52 synthetic controls matched independent Fab CPU state and their
explicit expected mutations. SRAM guards remained intact. Emulator-only evidence;
no MOS conformance or hardware result is claimed.

## Reproduction

From /home/smith/Agon/mystuff/agon-utils/examples/mos-tests on Linux:

```sh
./human/mos-tests capture-check --output .emulator/runs/capture-review
./human/mos-tests runner-build
```

Use a fresh output directory. Qualified run: capture-02; prior capture-01 also
passed before adding the SRAM mapping preflight. The final run includes that gate.
The raw image remains in ignored .emulator/runs/capture-02/sd.img; its receipt,
build, identity, disassembly, transcripts, results and SRAM dump are retained here.
Both applications build with AgonDev. The emulator exited normally after checks.

## Scope and limits

Two seeds exercise preservation, each byte of BC/DE/HL/IX/IY, A, each F bit,
and an isolated simulated post-return SP+3 deviation. Subsequent deliberate
register clobbering does not change snapshots. The debugger independently observes
capture entry and exit state; SP is normalized by the three-byte capture CALL.
All bytes outside the two 32-byte snapshots retain C7 across the controlled run.

Qualified mapping B7E000–B7FFFF, ADL=1, MB=0. Interrupt-state capture is unavailable;
alternate registers, other modes, arbitrary crash recovery and hardware remain
unqualified. SRAM retrieval at a controlled debugger pause succeeded. Reset is
not a recovery mechanism. Binary record commit/checkpoint integration is W04.

Maintained implementation: apps/runner/src/capture.asm and docs/register-capture.md.
Reusable controls: apps/capture-controls, tests/capture, agents/check_capture.py;
humans and agents invoke the shared human/mos-tests capture-check command.
