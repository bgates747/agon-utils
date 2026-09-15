# SETUP-01 — Configure a standard AgonDev project

## Summary

Establish a reproducible AgonDev C++ build and execution baseline for MOS tests,
with paths for BBC BASIC and assembly comparisons. W01 inspection and W02
build configuration are complete. W03 clean build and headless MOS-output/main-return checks passed.
W04 comparison also passed. W06 raw-image qualification now passes with !boot.obey. W05 BASIC qualification and W07 evidence consolidation also passed.

## State

Closed — Author accepted the results and explicitly approved committing on 2026-09-15. The authoritative unfinished-task index is the subproject-root
[TODO.md](../../TODO.md), at `agon-utils/examples/mos-tests/TODO.md`.
This task's subtask status lives here; the agon-utils repository-root TODO
is not authoritative for MOS tests.

Subtask identifiers are immutable and local to this task. Work/W is the
current category; additional categories may use distinct local prefixes as
needed, without a global subtask namespace. Never delete, renumber, or reuse
subtask IDs. Mark disposed items `[x]` with an explicit Completed, Deferred,
or Canceled disposition and rationale/evidence. See [task conventions](README.md).

All implementation subtasks are complete and accepted. Hardware remains untested;
acceptance covers the documented emulator evidence. No additional visual or hardware
validation is claimed.
Identifiers are unchanged.

## Work

- W01 [x] Inspect the installed AgonDev toolchain and its official local documentation;
   record its identity and supported C++/assembler/runtime conventions.
   **Completed** — installed-toolchain inspection and evidence recorded in
   [W01 findings](SETUP-01/W01/findings.md). No build or runtime qualification claimed.
- W02 [x] Configure the standard project layout and Makefile using AgonDev's supported
   build integration. Use the existing agon-utils Python environment for helpers.
   **Completed** — standard layout and Makefile configured; see
   [build guide](../build.md) and [configuration checks](SETUP-01/W02/validation.txt).
   Dry-run rule expansion passed; no test binary was compiled or executed.
- W03 [x] Build a minimal C++ MOS smoke test with explicit expected output and return
   behavior; document build, clean, deployment, and execution commands.
   **Completed** — clean build and headless debugger checks verified exact MOS
   output bytes and main returning zero. Hostfs bootstrap evidence only; no
   visible-prompt or hardware claim. See [headless result](SETUP-01/W03/headless-result.md).
- W04 [x] Provide an assembly comparison path and retain compiler assembly or linked
   disassembly so MOS ABI and machine-code discrepancies can be investigated.
   Check compiler output against documented behavior and independent hand assembly.
   **Completed** — independent C++/libagon and raw-MOS assembly paths matched
   expected output, 24-bit return, stack balance and IX preservation headlessly.
   See [W04 evidence](SETUP-01/W04/README.md); hostfs bootstrap only.
- W06 [x] Deploy only bounded test outputs/fixtures into the dedicated emulator SD
   image, using Fab `--sdcard-img` as the test baseline rather than hostfs.
   Prepare a project-owned raw SD image, verify deployed contents, and integrate
   it with the canonical profile launcher without mapping the parent project.
   **Scope clarified** — Author relayed Tom Morton's hostfs-fidelity advice;
   existing hostfs smoke results are bootstrap evidence, not filesystem validation.
   **Completed** — !boot.obey startup and image readback verified; both C++
   and independent assembly comparisons passed headlessly on raw SD images.
   Missing-OBEY cleanup defect tracked separately as MOS-01. See
   [W06 evidence](SETUP-01/W06/README.md).
- W05 [x] Establish a BBC BASIC fixture location and document interpreter selection,
   loading, invocation, and result capture. Decide which interpreter/mode the
   initial fixtures require from their semantics and available official docs.
   **Completed** — pinned v1.0RC1 rebuilt byte-identically, deployed as
   bbc-basic-v-adl.bin, and plain-text smoke verified twice headlessly on raw
   images, including return to MOS with HL=0. See [W05 evidence](SETUP-01/W05/README.md).
- W07 [x] Record exact toolchain, MOS, VDP, runtime, inputs, expected/actual results,
   and execution environment. Separate potential compiler/runtime faults from
   MOS and emulator faults; preserve minimal reproducers for discrepancies.
   **Completed** — [result summary](../test-results.md), consolidated run
   register and evidence verification under `SETUP-01/W07/`. Retrospective
   identity limits and outstanding hardware/acceptance gates are explicit.

- W08 [x] Inspect emulator debugging features and document a local reference
   with automation conventions and suitable test-suite integrations.
   **Completed** — inspected installed CLI/client/core and documented
   [emulator debugging](../emulator-debugging.md); source identities retained
   in `SETUP-01/W08/source-identity.txt`. Source-confirmed features are
   distinguished from W03-exercised behavior.

## Acceptance criteria

1. A clean documented AgonDev build produces and runs the C++ smoke binary.
2. An independent assembly comparison and a BBC BASIC smoke fixture have
   documented invocations and observed results, with relevant artifacts retained.
3. Build outputs and generated state are ignored appropriately; no duplicate
   Python environment or modified upstream checkout is needed.
4. The Author has validated resulting emulator behavior and explicitly approved
   committing emulator-related changes. Automated checks do not satisfy this gate.
5. Hardware results are recorded if performed; otherwise hardware confirmation
   remains explicitly outstanding and emulator success is not presented as hardware success.

## Task workspace

Use `docs/tasks/SETUP-01/` for bounded experiments and trials, with separate
subdirectories when needed. Promote mature code, scripts, and documents into
maintained subject-named locations in the subproject; retain provenance and
evidence links in this task record.

## Initial evidence

The dedicated profile and shared Python verification are described in
`../../HANDOFF.md` and the bootstrap development log. W02 configuration and W03 build evidence are linked above. The W03 binary
was qualified headlessly; subsequent raw-image comparisons and BASIC qualification
are consolidated in [test results](../test-results.md). Author acceptance and commit
approval were recorded on 2026-09-15.
