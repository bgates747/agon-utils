# MOS tests agent entry point

Read the repository-root `AGENTS.md` and `codex-workflow-notebook.md`, then
this project's `HANDOFF.md`, `README.md`, `TODO.md`, and latest dated log
under `docs/development/`. Apply canonical Agon guidance with the Author's subproject-specific scope
clarifications below.

## Project rules

1. Keep all project work on Linux under `agon-utils/examples/mos-tests`.
2. Use the existing repository-root `.venv/bin/python` explicitly; from here
   this is `../../.venv/bin/python`. Do not create a subproject environment.
3. `agon-utils/examples/mos-tests/TODO.md`, at this subproject root, is the
   sole authoritative unfinished-work index for MOS tests. Canonical references
   to the project's TODO mean this file for MOS tests, not a TODO at the
   agon-utils repository root. Do not duplicate MOS tests tasks there.
   Task details belong in
   `docs/tasks/<ID>.md`; bounded supporting work belongs in `docs/tasks/<ID>/`.
   Follow `docs/tasks/README.md`: subtasks use immutable task-local identifiers
   followed by checkboxes. Work/W01 is a default; tasks may define several
   category prefixes. No global subtask namespace or registry is maintained.
   Never delete or renumber subtasks; mark disposed items
   `[x]` with explicit Completed, Deferred, or Canceled status and rationale.
   Use task directories to silo trials; promote mature outputs into maintained
   subproject locations with provenance retained in the task record.
   Record decisions and validation in dated development logs as work proceeds.
4. Tests will primarily use C++. Support BBC BASIC and assembly where useful.
   Hand assembly can provide an independent comparator for AgonDev-generated
   code, particularly MOS calling conventions and emitted machine code.
5. Distinguish MOS faults from compiler, runtime, ABI, fixture, and emulator
   faults. Agreement between two implementations alone is not proof of correctness.
6. Keep the dedicated emulator in ignored `.emulator/`. Never map this whole
   project into its nested SD tree. Launch by changing to `.emulator` and
   executing `./fab-agon-emulator`.
7. Leave emulator-related changes uncommitted and unpushed until the Author
   tests the behavior and explicitly approves committing. Preserve unrelated
   repository work; never stage it with this subproject.

## SD-card fidelity

Use Fab `--sdcard-img` with a project-owned raw SD-card image as the MOS test
baseline. The Author relayed maintainer Tom Morton's advice that hostfs can
teach a test suite to depend on its incorrect behavior. Existing hostfs smoke
results are bootstrap evidence only and do not establish filesystem correctness.
SETUP-01 W06 owns image preparation, deployment, and launcher integration.

## Emulator execution preference

Headless emulator execution is the default for testing and development.
Use debugger traces, captured output, and automated checks where sufficient.
Launch a graphical emulator only when the Author's visual confirmation is
absolutely necessary; explain the specific visual behavior requiring review.
Do not launch graphical instances merely as attention alerts. This explicit
Author preference supersedes canonical graphical-launch/attention guidance
for this subproject. Continue using the canonical profile-local wrapper and
record the execution backend and evidence limits. This preference does not
by itself authorize commits or waive other explicit approval requirements.

Read `docs/emulator-debugging.md` before designing emulator observations or
automation; use its command, fidelity, and evidence conventions.

Jeroen Venema's BBC BASIC V ADL is deployed as `bbc-basic-v-adl.bin` to
avoid ambiguity with other BASIC ports. Preserve its upstream source filename
and version/hash in provenance; do not rename files in the upstream checkout.
