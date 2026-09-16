# Register capture boundary

The maintained assembly probe records 32-byte snapshots at $B7E900 and $B7E920
using the [format v1 layout](result-format-v1.md). ADL/MB0 primary-register capture
has passed independent synthetic controls under the recorded Linux Fab runtime.
This is capture qualification, not a MOS function result or hardware claim.

## Call contract

First call capture_available from setup code: it checks RAM_ADDR_U=B7 and RAM_EN.
Do this before seeding test registers or writing the capture area. Invoke
_capture_before and _capture_after from a reviewed assembly call boundary, not
through a C++ call site whose ABI changes the registers under observation.

The probe stores HL before borrowing it to save AF, then records other primary
registers using direct stores. Three bytes are temporarily stored for AF; the
following BC store replaces the overlapping byte before the snapshot is usable.
It records SP normalized by +3 to exclude its own CALL return address. It restores
AF and HL before RET; other primary registers are unchanged. Snapshot PC identifies
the capture entry. MB is read directly; ADL=1 is a caller precondition, checked
against independent debugger state in qualification. IFF is unavailable (validity
bit clear), not inferred from later flags. No partial snapshot is valid evidence;
W04's record framing must commit only after the probe returns.

Require a valid writable stack with at least six bytes of headroom, mapping gate
success, exclusive user ownership of this reserved capture portion, and no nested
capture/callback writer. Both functions are non-reentrant. Normal ISR execution
is not globally disabled. Reserved capture-stack space remains available for a
later separately qualified alternate implementation; current calls use the caller
stack. No promise about preserving stack-memory contents below the restored SP.

## Qualification and use

```sh
./human/mos-tests capture-check --output .emulator/runs/capture-review
```

The command builds the C++/assembly synthetic application, creates a raw SD image,
uses headless debugger triggers at capture boundaries, checks 52 controls, dumps
SRAM, verifies guards and closes the emulator. Results include binary/map/runtime
identity, disassembly, debugger transcript, sram.bin and result.json. Existing
output directories are refused. Nonzero exit leaves incomplete evidence.

See [control rationale](../tests/capture/README.md). Check expected.json and the
assembly mutations independently when changing the probe; don't change the oracle
merely to silence a discrepancy. This observer also demonstrates that the tested
Fab debugger can retrieve this SRAM window. Recovery after arbitrary CPU/VDP
faults is not established by a successful controlled pause. Reset wipes SRAM.

MAIN-03 W04 now connects capture to shared lifecycle recording/checkpoint hooks
in a synthetic qualification app; see [binary recording](binary-recording.md).
Full catalogue/startup execution and report decoding remain subsequent work.
Capture alone does not guarantee durable or complete case results.
