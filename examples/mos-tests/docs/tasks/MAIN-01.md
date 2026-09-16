# MAIN-01 — MOS API inventory and test strategy

## Summary

Define how the suite will exercise every function in a pinned MOS API, with
explicit expected behavior, independent observations, and a practical sequence
of implementation batches. Deliver an API inventory, coverage matrix, and test
architecture before expanding the smoke checks into a general suite.

SETUP-01 supplies the working Linux/headless baseline. Keep the populated
`!boot.obey` workaround; the Author has parked MOS-01. Fixing firmware is not a
prerequisite for this work. This task plans coverage; it does not claim that the
listed functions have been tested or implement the full suite.

## State and ownership

Reconstructed contract checkpoint. Completed items: none.
Remaining work is frozen and unstarted at this checkpoint. The subproject TODO
owns unfinished task indexing. This is a retrospective grouping, not an exact
previous edit version or a backdated acceptance record.

## Work

- W01 [ ] Inventory the pinned MOS API and its contracts.
  Start from the SETUP-01 MOS 3.0.2 Arthur baseline and record the exact source,
  binary, symbol-map and official documentation identities used. Enumerate
  public calls, selectors/subfunctions, version availability and related entry
  conventions. Record inputs, outputs, register/flag effects, pointer/buffer
  requirements, errors and state changes. Cross-reference documentation and
  implementation; identify disagreement and unspecified behavior explicitly.
  Distinguish MOS calls from VDP protocols, shell commands and library helpers;
  record dependencies without silently expanding the API scope.
- W02 [ ] Define the function-by-function coverage matrix.
  Give each inventory entry normal, boundary and documented failure cases,
  prerequisites, fixtures, expected results, observation method, implementation
  route, isolation requirements and execution capability (headless emulator,
  hardware, or both). Every function must have proposed coverage or an explicit
  reason for exclusion/deferment. Distinguish an unimplemented case, unsupported
  environment, blocked case and a verified pass. Invalid-pointer and other
  undefined-input probes must be identified as isolated robustness experiments,
  not automatically scored as API conformance failures.
  Make advertised-versus-observed register preservation a first-class dimension:
  link each preservation claim to pinned documentation, distinguish preserved
  registers/flags from outputs and unspecified effects, and cover success,
  documented errors and boundary paths. Record full 24-bit register effects,
  including upper bytes and IX/IY, promised flags and stack balance where
  applicable. Also identify advertised defaults and omitted default behavior;
  distinguish an explicit default, observed default and unspecified behavior.
- W03 [ ] Specify fixtures, assertions, isolation and evidence.
  Define C++/AgonDev calls and direct assembly comparators against independently
  stated expectations; use BBC BASIC V ADL where it adds meaningful coverage.
  Record shared dependencies so agreement is not mistaken for independence.
  Specify return/register/stack checks only where contracts require them;
  distinguish MOS-entry output bytes from actual display or device effects.
  Use fresh raw SD images with known contents and !boot.obey for stateful tests,
  inspect resulting bytes/metadata where applicable, and define reset/cleanup
  boundaries. Specify bounded execution, crash/hang capture, debugger use,
  launch-time identities, expected/actual results and reproducible artifacts.
  Define how harness failures differ from target failures, and what later
  TEST-* work should use to detect false passes and broken observations.
  Specify an assembly preservation harness that seeds unconstrained registers
  with distinguishable values, supplies valid arguments, and captures entry and
  return state before reporting or comparison code can alter it. Use more than
  one seed pattern; compare argument registers against their actual entry values.
  Preserve flags during capture and distinguish expected outputs from clobbers.
  Specify independent TEST-* checks with known-preserving and known-clobbering
  routines so the harness cannot silently create or hide discrepancies.
  Reports must show the advertised claim/default and source reference, exact
  inputs and path, before/after register values and changed bytes/bits, target
  identities and a minimal reproducer. Label observations without an advertised
  promise as documentation omissions, not automatically conformance failures.
- W04 [ ] Select and sequence the first implementation batch.
  Choose a small batch of deterministic calls that exercises the proposed
  harness and has useful independently checkable results. Treat register
  preservation auditing as a strong candidate for this first batch. Explain dependencies
  and sequence subsequent groups, including filesystem, input, timing and
  peripheral work as supported by the inventory. Identify which cases need
  hardware or stronger emulator support. Consolidate the strategy and matrix
  into maintained project documents, retain research provenance in the task
  silo, and propose bounded MAIN-* follow-ups for Author review. Do not create
  an implementation task per API call or start firmware repairs under this task.
## Human and agent use

Hardware is the final authority for real-machine behavior. Emulator results are
valuable both as preparation for hardware and as independent emulator-validation
results. Always identify the backend; an emulator pass does not imply a hardware
pass, and disagreement must remain visible.

The root README must prominently direct humans to `human/README.md`. The human
entry point owns usable instructions and runnable front ends for both emulator
and hardware. `agents/README.md` owns agent workflow, evidence rules and any
agent-specific automation. Agent instructions link to human operations they
reuse, rather than copying those instructions or reimplementing their tools.
Shared fixtures, build/deployment primitives, result formats and comparison
logic have one maintained implementation. Agent-only helpers add capabilities
such as debugger orchestration or unattended evidence collection.

W03 must specify these entry points and ownership boundaries, with explicit
arguments, useful exit codes, saved results and deliberate interactive behavior
so agents can call human tools. W04 must sequence promotion of mature task-local
helpers into this structure. [MAIN-02](MAIN-02.md) owns initial scaffolding; it
must not pre-empt the unfinished coverage matrix or harness design.

## Provisional runner direction

See [provisional runner design](../provisional-runner-design.md). W03 must first
work out the human-editable autoexec.txt selection workflow and verified boot
chain, retaining !boot.obey where required. W04 must prioritize that interface
before a menu application. Function-level selection and report semantics are
shared by human and agent entry points. On-device helper applications use C++
with AgonDev; assembly ABI tests and BASIC fixtures remain appropriate.
Incremental reporting, completion markers and recovery are design ideas to
resolve, not implemented guarantees.

W03 must also resolve [provisional result design](../provisional-result-design.md):
binary capture before reporting, early/frequent SD checkpoints, post-run readable
reports and bounded crash recovery. Verify the target SRAM mapping and coordinate user allocations; onboard SRAM
is guaranteed user-owned by platform contract. The pinned baseline maps 8 KiB
at $B7E000–$B7FFFF. MOS reset wiping, including soft resets, prevents assuming
reset persistence.
Specify format validation, capture integrity, checkpoint failures and buffer-full
handling; do not present RAM recovery as reset or power-loss persistence.

## Compatibility and discrepancy policy

Finding a discrepancy is not authorization to patch firmware or change behavior.
The Author reports a community compatibility policy of retaining established
behavior so legacy applications do not break on fixes. This project follows that
policy: prioritize clear documentation of discrepancies and omissions, especially
advertised or implicit defaults, with version and path qualifications and evidence.
Do not silently change expectations to hide a discrepancy, either. Keep the
advertised contract and observed behavior separately visible.

Prepare documentation clarification proposals rather than firmware fixes. Any
exception to this behavior-preservation policy requires a separate explicit
Author decision; this task supplies no such authorization. Publishing upstream
documentation or contacting maintainers also requires separate authorization.
MOS-01 remains parked; its existence is not authorization to resume repairs.

Exception: stock MOS/VDP writes to onboard user SRAM, excluding the allowed MOS
reset wipe, are ownership-contract violations to flag for immediate rectification.
They must not be normalized as legacy behavior or resolved only by documenting
an exception. Preserve writer/address/target evidence. This directs finding
classification and priority; implementing or publishing a patch still requires
separate explicit Author direction.

## Deliverables

1. `docs/mos-api-inventory.md`: pinned API scope, contracts, source references,
   discrepancies and explicit exclusions.
2. `docs/mos-coverage-matrix.md`: cases and observation requirements for every
   inventory entry; planning status clearly separated from execution results.
3. `docs/test-strategy.md`: suite architecture, fixtures, isolation, result
   semantics, reproducibility and staged implementation priorities.
4. `docs/tasks/MAIN-01/`: bounded research, draft matrices and any small trials
   needed to resolve strategy questions. Mature guidance is promoted into the
   maintained documents above; task IDs and evidence links remain durable.

These are planned outputs, not files already delivered. Keep detailed actionable
subtasks here and task-level unfinished status only in the authoritative TODO.

## Acceptance criteria

1. Every function/subfunction in the agreed pinned API scope is accounted for;
   omissions, undocumented behavior and version-dependent contracts are visible.
2. Each proposed case states a concrete expectation and a way to observe it;
   C++/assembly agreement alone cannot establish correctness.
3. Stateful isolation and failure reporting are sufficient to distinguish a
   MOS defect from compiler, binding, runtime, fixture or emulator faults.
4. The first implementation batch is bounded and justified, with later groups
   sequenced by dependencies and available observation capabilities.
5. Hardware-only and currently unobservable behavior remains explicit. Emulator
   success never becomes a hardware claim; hostfs is not the qualification basis.
6. The Author reviews the strategy before it becomes the implementation plan.
   All W identifiers remain intact and receive explicit dispositions on closure.

7. The matrix and harness design explicitly address advertised preservation,
   default behavior and omissions, including independent capture validation and
   reproducible discrepancy reports. Documentation clarification is the default
   disposition; finding a mismatch does not authorize changing firmware behavior.

## Report presentation direction

W04 should keep first implementation reporting to a prominent verdict, invariant
counts, failed-test summary and failure details in stable order, as specified in
[test strategy](../test-strategy.md). All-pass requires complete selected coverage;
incomplete or skipped cases cannot disappear behind a green headline. Summary-only,
verbose and optional detail grouping/sorting are later enhancements after the
harness is qualified, not prerequisites for the initial batch.

## Starting references

1. [SETUP-01](SETUP-01.md) and [setup results](../test-results.md).
2. [Build guide](../build.md) and [emulator debugging](../emulator-debugging.md).
3. [MOS-01](MOS-01.md), parked with the !boot.obey workaround retained.
4. [Task conventions](README.md).

All project work, source inspection and experiments remain on Linux under the
user-owned project. Upstream checkouts are read-only references. BASIC fixtures
name their interpreter explicitly: `bbc-basic-v-adl.bin`, with pinned provenance.
