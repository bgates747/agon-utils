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
remain read-only. Prior checkpoints were pushed through c73d827; W06 is accepted for the next checkpoint.

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

Next after this checkpoint: MAIN-03 W07 aggregate qualification, fresh-image
repeat and delivery closeout. Hardware, alternate CPU state, power-loss guarantees
and arbitrary crash recovery remain unqualified. MOS-01 remains parked. This W06 acceptance checkpoint is local; prior checkpoints remain pushed at c73d827.
