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
remain read-only. Pushes have not been requested.

## Current human and agent entry points

Humans start at human/README.md and use human/mos-tests. Agents start at
agents/README.md and reuse the same tool. The promoted smoke comparison passes
for C++ and assembly through raw images; results are saved per fresh run directory.
Hardware, full-suite autoexec selection and the first MOS case batch are not
implemented. See docs/test-strategy.md for accepted design.
MAIN-02 validation evidence is under docs/tasks/MAIN-02/. The Author authorized retrospective checkpoint commits on 2026-09-16;
no upstream publication or physical hardware work was performed.

MAIN-03 W01–W05 and TEST-01 W01–W05 are complete. Binary recording/capture
and the host decoder/report are qualified component by component. Use
human/mos-tests report and report-check; see human/reports.md. W05 passed 58
scenarios and 1,380 malformed-record controls, including all 14 report oracles.
Evidence: docs/tasks/MAIN-03/W05/. No emulator was launched for host decoder work.

Next is MAIN-03 W06 with TEST-01 W06: authenticated editable autoexec startup
bundle, persistent selection/run identity and shared human/agent front ends.
W04's target fixture uses illustrative hashes; do not relabel it an authenticated
full-suite result. IFF, alternate state, arbitrary crash/power-loss behavior and
hardware remain unqualified. Supplied recovery errors override file completion;
a file-only report does not establish successful close or absence of lost errors.
Completed work through MAIN-03 W05 is accepted for the retrospective checkpoint
series authorized on 2026-09-16. W06 is frozen but unstarted. MOS-01 remains parked.
