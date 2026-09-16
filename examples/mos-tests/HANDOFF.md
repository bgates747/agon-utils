# MOS tests handoff

SETUP-01 is complete and accepted; the Author approved committing on 2026-09-15.
C++, independent assembly, and BBC BASIC checks passed headlessly on raw SD
images. MOS-01 remains open for the missing-OBEY cleanup defect and upstream PR.
MAIN-01 is accepted; MAIN-02 scaffold is complete and accepted for checkpointing; MOS-01 is parked with the
!boot.obey workaround retained.
Hardware has not been exercised; acceptance does not establish hardware correctness.

## Environment

1. Root: `/home/smith/Agon/mystuff/agon-utils/examples/mos-tests`.
2. Python: `/home/smith/Agon/mystuff/agon-utils/.venv/bin/python` (3.14.6).
3. Toolchain: `/home/smith/Agon/agondev/release`; Makefile resolves it explicitly.
4. Dedicated ignored profile: `.emulator/`, using official Fab 1.2.4 runtime at
   `/home/smith/Agon/mystuff/AgonJukebox/.emulator/runtime/fab-1.2.4`.
5. MOS: hash-pinned v3.0.2 Arthur, with matching map and native platform VDP.
6. BASIC: Jeroen Venema BBC BASIC V ADL v1.0RC1, deployed as `bbc-basic-v-adl.bin`.

## Build and execution

Run on Linux from the subproject root:

```bash
make
make sd-image
make headless
```

Image preparation refuses existing outputs; preserve an existing image or select
another output using the documented script options. Use raw `--sdcard-img` and
`/!boot.obey`; absent boot files expose MOS-01. Hostfs trials are historical
bootstrap evidence only. Headless execution is the default; launch graphics only
when visual confirmation is necessary. The runner changes to the profile and
executes its canonical wrapper with SDL dummy drivers and software rendering.

Read [build guide](docs/build.md), [debugger reference](docs/emulator-debugging.md),
and [results](docs/test-results.md) before further test work. Reproduction scripts,
fixtures, provenance, failed trials and qualified results remain under
`docs/tasks/SETUP-01/`. The W07 register records retrospective runtime fingerprints
with their limits. No emulator was launched for closeout.

## Task state

The subproject-root [TODO.md](TODO.md) owns unfinished work. SETUP-01 and all its
immutable subtask records are retained under `docs/tasks/`; MOS-01 is separate.
Keep unrelated agon-utils changes out of MOS tests commits. Upstream checkouts
remain read-only. Prior checkpoints were pushed through c73d827; W06 is committed locally as 6bc13e9.

## Current human and agent entry points

Humans start at human/README.md and use human/mos-tests. Agents start at
agents/README.md and reuse the same tool. The promoted smoke comparison passes
for C++ and assembly through raw images; results are saved per fresh run directory.
Editable autoexec selection now runs synthetic controls; physical hardware and
the first real MOS case batch remain unqualified/unimplemented. See docs/test-strategy.md for accepted design.
MAIN-02 validation evidence is under docs/tasks/MAIN-02/. The Author authorized retrospective checkpoint commits on 2026-09-16;
no upstream publication or physical hardware work was performed.

MAIN-03 W01–W06 and TEST-01 W01–W06 are implemented and qualified. W06 is
accepted by the Author on 2026-09-16; this checkpoint commits its results with
the already frozen W07 contract before beginning W07. Do not accumulate another uncommitted work item.
See human/startup.md for bundle, startup and startup-check commands. W06 retains
!boot.obey -> EXEC /autoexec.txt as the MOS-01 workaround; firmware is unchanged.

Ten raw-image scenarios passed, with native parser/hash/continuation controls.
Selection is derived on target from actual script bytes; run identities allocate
from an installation namespace/counter, and repeated boots preserve earlier runs.
Ordinary discrepancies continue; infrastructure/script-integrity errors stop.
Evidence: docs/tasks/MAIN-03/W06/, with a compressed qualification archive.
The current bundle implements only three synthetic controls; default coverage
is two passes and one unsupported UART fixture, not an all-pass suite claim.

At the W06 checkpoint, the next work was W07; it has now passed as recorded below. Hardware, alternate CPU state, power-loss guarantees
and arbitrary crash recovery remain unqualified. MOS-01 remains parked. This W06 acceptance checkpoint is local; prior checkpoints remain pushed at c73d827.

## MAIN-03 W07 delivery qualification

All aggregate synthetic checks and an independent fresh-image repeat passed.
See docs/tasks/MAIN-03/W07/validation.md and human/qualification.md. W07 results
await acceptance and commit; MAIN-03 and TEST-01 remain in TODO until then.
Twelve command stages took about 119 seconds on this Linux host. Ten prior W06
result files were unchanged; repeated boots preserved previous runs; no Fab
processes remained. Controlled pre-reset SRAM retrieval is supported. Hardware,
arbitrary crash recovery and power-loss guarantees remain unqualified.
Next is MAIN-05 restart recovery, before the proposed MAIN-04 real MOS cases.
Freeze its W01 contract after the pending W07 acceptance checkpoint. The design
now requires SD-backed startup inspection and explicit interruption disposition,
preventing automatic reboot loops. No recovery implementation or real cases
started; no push.

## Accepted foundation; MAIN-05 W01 authorized

On 2026-09-16 the Author approved the W07 result checkpoint and proceeding with
MAIN-05 W01. MAIN-03 and TEST-01 are accepted/closed and removed from TODO.
Freeze W01 scope in this checkpoint, then design the recovery contract and
independent transition expectations. No W02 implementation or push authorized
by this checkpoint. Earlier pending-acceptance paragraphs describe prior state.

## MAIN-05 W01 design ready

Checkpoint ecec9b9 accepted W07 and froze W01 scope. W01 now supplies
docs/restart-recovery.md plus 30 transition expectations and an independent
IDLE-slot binary fixture under docs/tasks/MAIN-05/W01. It awaits acceptance and
commit before W02 implementation. Key decisions: invalid slot blocks despite an
older clean slot; reconcile bounded retained history; publish intent before
allocation/case entry; park remains stopped; retry/continue is explicit and
one-use with new parent-linked identity. No emulator launched for this design.

## W01 accepted; W02 authorized

The Author requested “push, then do your next work.” This accepts W01 for its
result checkpoint, freezes W02 implementation/validation scope, and authorizes
pushing these commits before implementing the gate. W03 dispositions remain
separate. No hardware execution or firmware repair is authorized.
