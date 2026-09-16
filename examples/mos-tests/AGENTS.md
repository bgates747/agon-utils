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

## MOS API contract authority

`docs/mos-api-inventory.md` owns scope accounting and project findings, not a
copy of upstream contracts. Before designing assertions, verify the target MOS
binary/map and source revision and read the referenced upstream documentation
and implementation. Documentation is independently versioned; record conflicts
rather than treating either prose or source behavior as automatically correct.
Review the inventory and discrepancy notes whenever the target or documentation
baseline changes. W01 archives are historical evidence only, not current agent
guidance; do not extract them into maintained source/documentation directories.

## Compatibility and discrepancy handling

Finding an API discrepancy does not authorize a firmware patch or behavior
change. The Author's stated community policy is to preserve established behavior
so legacy applications do not break on fixes. Prioritize documentation updates
that prominently distinguish advertised behavior from observed behavior and
highlight omissions, especially defaults. Include pinned versions, execution
paths and evidence. Do not silently rewrite expectations to conceal mismatches.
Any behavior-changing exception requires separate explicit Author direction.
MOS-01 is parked and must not be resumed on the strength of a new finding.
Upstream publication or maintainer contact requires separate authorization.

Register-preservation auditing is a core suite requirement: compare documented
promises with immediately captured state across relevant paths. Distinguish
outputs and unspecified effects, include full register widths and promised flags,
and independently validate that the observation harness detects known clobbers.

## Human and agent tooling ownership

Follow MAIN-02's audience structure for new tooling and MAIN-01's strategy.
The root README's prominent usage direction must lead humans to human/README.md,
which owns human-facing emulator and hardware instructions and runnable tools.
Agents use agents/README.md for their workflow, linking to human procedures and
calling their tools where useful. Until MAIN-02 scaffolds these paths, use the
existing maintained guides; do not imply those entry points already exist.
Keep common fixtures, build/deployment primitives and result logic in one shared
implementation. Agent-only tooling adds automation rather than duplicating human
tools. Promote mature task experiments with provenance before routine use.
Hardware is authoritative for real-machine behavior; emulator results also have
independent value. Identify the backend and never imply one validates the other.

## Runner direction and helper language

Prioritize the human-editable autoexec.txt workflow before a menu convenience
application. See docs/provisional-runner-design.md for provisional details;
verify boot chaining and script syntax before presenting runnable instructions.
On-device helper applications must use C++ targeting AgonDev, including any
future menu. This does not constrain assembly ABI tests, BASIC fixtures or
existing host-side Python orchestration. Reuse common function selection and
result logic across human and agent interfaces.

## Onboard SRAM ownership

The Author confirms a hard platform contract: the eZ80's 8 KiB onboard SRAM is
always user-allocated space. System code never uses it for runtime storage;
MOS reset wiping, including soft resets, is the exception. Do not require an
audit to establish system non-use. For this pinned target it maps to
$B7E000–$B7FFFF. Verify mappings for other targets and coordinate allocations
among user code. Capture recovery must precede reset; do not assume persistence.

### SRAM contract violation exception

Any stock MOS or VDP routine writing onboard user SRAM, apart from the allowed
MOS reset wipe, violates the platform ownership contract. Flag such a finding
prominently for immediate rectification, with writer attribution, address range,
target identity and reproducible evidence. This is an explicit exception to the
usual policy of retaining legacy discrepancies and clarifying documentation:
system writes to this user-owned space are not acceptable legacy behavior.
Flagging and prioritizing rectification does not itself authorize implementing
or publishing a firmware patch; obtain separate explicit direction for that work.

MAIN-01 W03 consolidated the runner/result ideas into docs/test-strategy.md.
Use that maintained design for implementation; provisional design notes are
superseded brainstorming provenance. Do not present designed interfaces as built.

Before implementing or investigating tests, follow the Test design patterns and
Agent implementation rules in docs/test-strategy.md. In particular, establish
independent expectations, qualify the tester and preserve failure reproducers.

MAIN-02 entry points now exist: read agents/README.md and reuse human/mos-tests.
Hardware/full-suite startup capability remains pending as labelled there.

## Acceptance checkpoints and frozen work contracts

1. Before implementation, freeze the next work item's scope, stable IDs,
   acceptance criteria and validation plan in a commit. A proposed change to that
   contract must be recorded and committed before implementing the changed scope.
2. Work only against that committed contract. Retain implementation, experiments,
   validation and limitations with the same task/work-item identifiers.
3. On Author acceptance, commit the completed item's implementation, evidence and
   disposition together with the frozen contract for the next item. Do not begin
   the next item until this checkpoint exists. This keeps rollback points aligned
   with known-good results and preserves the original instructions for later work.
4. If the next contract is not ready, commit the accepted results, then commit the
   next contract separately before implementation. Do not let accepted work collect
   across multiple uncommitted items. Acceptance/commit authorization may already
   be explicit in the conversation; do not request it a second time.
5. Preserve task identifiers and disposition history. Scope changes never erase
   the contract that motivated work. Keep unrelated repository changes out of
   these commits, and do not push without authorization. A commit does not imply
   unperformed hardware or visual validation.
6. For the 2026-09-16 backlog only, the Author explicitly authorized reconstructing
   logical contract/result commits. Identify that reconstruction, use real current
   commit dates, and preserve the original evidence and its limitations. This is
   not permission to invent historical approvals, test runs or exact edit versions.
