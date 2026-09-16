# MOS suite execution and evidence design

## Summary

Use one shared case catalogue and runner, exposed through human-editable startup
scripts and reusable human/agent front ends. Capture raw evidence in user SRAM,
checkpoint to SD before and after each case, and decode the same binary records
into text. Start with deterministic, returning cases; peripheral and destructive
cases retain explicit capability requirements. This is the W03 implementation
specification, not a claim that the tools or binary format already exist.

## Scope and authority

[Coverage matrix](mos-coverage-matrix.md) defines proposed case families;
[API inventory](mos-api-inventory.md) links pinned contracts and discrepancies.
W03 defines their execution and evidence interfaces. MAIN-02 scaffolds the
entry points; MAIN-01 W04 selects the first implementation batch. No new case
execution or firmware change was needed to produce this design.

Hardware is authoritative for hardware behavior. Emulator results are separately
useful; record the backend and capability profile on every run. Defaults and
preservation disagreements remain visible and normally lead to documentation
clarification. They do not authorize a firmware patch. Stock MOS/VDP writes to
user SRAM, except the allowed reset wipe, are violations for immediate
rectification under the explicit ownership exception.

## Test design patterns

Choose the pattern from the claim being investigated, not from a desire to grow
case counts. These firmware-interface tests often cross multiple components;
calling everything a unit test does not make MOS, VDP and filesystem dependencies
isolated. Small synthetic harness controls can be true unit-level checks; target
API calls are contract/integration checks with explicitly recorded dependencies.

| Pattern | Purpose and application |
| --- | --- |
| Contract | Compare advertised preservation, results, defaults and side effects with captured behavior; pin the claim's source |
| Characterization | Record ambiguous or undocumented behavior without inventing a pass/fail contract |
| Regression | Preserve a reproducer and detect changes across target/compiler/emulator versions; a change is not automatically a defect |
| Differential | Compare C++ and assembly routes or emulator and hardware against independent expectations; agreement alone is insufficient |
| Boundary | Choose empty, one-element, exact-capacity, just-too-small, last-element and exhaustion cases where valid |
| State transition | Exercise meaningful sequences such as open/read/EOF/seek/read/close, including failures and cleanup between states |

Start with contract tests, selected boundary paths and deliberate harness
controls. Expand to longer state sequences and generated inputs only after the
observation mechanism is qualified. Randomized testing must retain its seed and
exact input sequence; random input is not a substitute for a known expectation.

### Independent expectations and observations

Define expected outcomes before running the target. Do not derive a preservation
mask from the implementation and then claim it validates advertised preservation.
Do not validate a filesystem write solely by reading through the same library;
inspect the resulting card/image independently. Shared implementations can share
a defect, so document which parts of a differential comparison are independent.
Expected-error cases pass when the promised error and side effects are observed.

### Test the tester

Use known-preserving and deliberately clobbering assembly controls to qualify
capture. For example, changing only IX's upper byte must produce exactly that
reported discrepancy; a preserving control must pass. Verify flag/stack capture
and that later reporting clobbers cannot change saved observations. Exercise
decoders/reporters with truncation, corrupt records, failed checkpoints, absent
case completion and inconsistent totals. TEST-* is reserved for this work.
These controls are implementation dependencies, not claims already validated.

### Minimize and preserve failures

Save the original run and evidence before investigating. Reduce input sizes,
case sequences and preceding state changes while preserving the failure. Keep
each trial separate and record its relationship to the original. A reduced
reproducer should identify the target, setup, input, advertised expectation and
actual observation. Do not discard a necessary sequence merely because a
single-call reproducer would look cleaner. Avoid repeated blind reruns; change
one relevant condition and record what it tests.

### Agent implementation rules

1. State the claim, pinned authority, inputs and observable expectation before
   coding. Separate unspecified behavior from advertised promises and distinguish
   source suspicions from runtime-confirmed discrepancies.
2. Separate setup, action, immediate capture, comparison, checkpoint and reporting.
   A test's own logging must not disturb the state being measured.
3. Select distinct execution paths and boundaries rather than many redundant
   inputs. Identify prerequisite fixtures, backend capabilities and isolation.
4. Record source/toolchain/firmware identities, fixtures, seeds, ordering and
   backend. Restore or isolate state so results can be reproduced.
5. Never weaken an assertion simply to make a failure disappear. A justified
   contract correction needs explicit rationale and versioned expectations;
   retain the original advertised claim and evidence of disagreement.
6. Never count a timeout, skip, unsupported path or missing/corrupt evidence as
   success. Keep harness/reporting failures separate from target failures.
7. Preserve original discrepancies before minimization or investigation. Do not
   overwrite the initial result with a later successful trial.
8. Follow the compatibility policy: prioritize documentation clarification for
   legacy discrepancies; finding a defect does not authorize a patch. Flag SRAM
   ownership violations under the explicit immediate-rectification exception.
9. Run proportionate checks for changes and required harness qualification;
   broaden testing when a failure or changed dependency justifies it, not merely
   to accumulate passing runs. Report what the evidence does and does not prove.

## One implementation, two audiences

| Location | Responsibility |
| --- | --- |
| human/README.md | Root README's prominent destination; emulator and hardware procedures |
| human/ | Runnable human front ends, reusable unattended by agents |
| agents/README.md | Prerequisites, capability selection, orchestration and evidence rules; links to human operations |
| agents/ | Unique debugger/recovery automation, calling shared tools |
| scripts/ | Existing Python build/image/launch primitives and future shared host utilities |
| src/runner/, src/cases/, include/ | AgonDev C++ runner/case descriptors and narrow assembly ABI probes |
| fixtures/ | Known-answer inputs, image manifests and decoder fixtures shared by routes |
| docs/ | Maintained contracts for suite behavior, format and user procedures |

These are intended ownership locations, not all existing directories. Promote
mature task helpers with provenance; routine operation must not depend on an
old task silo. Keep the current top-level Python environment. Target helper
applications, including decoder/menu helpers, use C++/AgonDev. Assembly is used
where observing exact registers requires it; BBC BASIC fixtures explicitly name
bbc-basic-v-adl.bin and its pinned interpreter identity. A future menu uses the
same catalogue and selection; it is not part of the initial implementation.

## Catalogue and selection

Each case descriptor has an immutable suite-local string ID, function/route,
contract reference, expectation revision, input fixture identity, required
capabilities, isolation class and timeout policy. Assign sequential IDs within
function/route (for example mos_fgetc.rst08.001); do not derive identity from row
position. Never reuse removed case IDs. Aliases may help selection, not identity.
The build emits a catalogue with a hash and a uint32 case-key mapping. Numeric
keys are meaningful only with that exact catalogue identity; retain its manifest
with every bundle and report. This is case identity, not global task namespaces.

Select by canonical function name, route, group or exact case ID. Unknown names
are configuration errors, never an empty passing selection. Selecting a function
includes its applicable case families; report exclusions individually. Resolve
selection once and store the ordered plan before execution. Default order is
catalogue order for reproducibility. Random order is opt-in with a recorded seed.

The runner requires a declared backend/capability profile. It must not infer
hardware versus emulator solely from CPU behavior. Bundle identity, user-selected
profile and host verification are distinguished in the manifest. Profile mismatch
or unavailable capability yields an explicit diagnostic/skip, not a false pass.

## Human startup workflow

Package /!boot.obey, editable /autoexec.txt, target executables, fixtures and
manifests together. For this MOS baseline, !boot.obey explicitly executes
`EXEC /autoexec.txt` after minimal boot setup. The script name does not cause
an automatic second-stage execution once !boot.obey succeeds.

Provide commented function groups. The intended structure is LOAD the shared
runner, RUN . with a function selection, repeat for the next group, then invoke
the report/finalize operation. CLI option spelling is assigned during scaffolding;
do not publish placeholder commands as working instructions. Humans disable a
whole LOAD/RUN group using # on each line or by deleting it. Use explicit paths
so cwd changes do not redirect the next load. Keep script lines below the pinned
MOS 256-byte line-buffer limit and generate CRLF files.

Source checks: pinned MOS mos.c recognizes # comments at line 445; mos_EXEC
runs lines and stops on a nonzero command status (around line 2748); !boot.obey
precedence is in main.c around line 228. SETUP-01 proved RUN . arguments for
BASIC, not this future runner. Verify the complete generated boot chain and
selection behavior on a disposable raw image before calling it ready for humans.

A completed test group returns MOS status zero even if it found discrepancies;
those are persisted evidence, not a script-control error. Configuration, missing
fixture, capture-integrity or checkpoint failure returns nonzero after best-effort
recording and stops further ordinary execution. Host decoding exposes aggregate
status separately: 0 complete/no discrepancies, 1 complete with discrepancies,
2 incomplete/infrastructure failure, 3 invalid configuration/evidence. These are
suite host-tool exit codes, not invented MOS API result codes.

Store the selected plan and script identity before the first case. A run-end
record alone is insufficient: completion requires reconciling every selected
case to a terminal disposition. Final reporting must detect deleted finalization
commands, skipped groups and mismatched manifests as incomplete execution.

## Case lifecycle and isolation

1. Validate bundle, target, capabilities and run destination; never overwrite an
   existing result. Allocate a fresh run directory/counter or accept a supplied
   unique run ID. Store the same 128-bit run ID in file and SRAM. No clock/random
   entropy assumption; reject collisions and persist allocation before tests.
2. Build fixtures and restore a known state. Preserve original vectors, cwd,
   owned handles and variables needed for cleanup. Checkpoint case-start, then
   establish any state that checkpoint I/O changes. Capture actual entry state.
3. Enter the measured call with no printing/filesystem operation inside the
   observation window. Capture exit state immediately; only then compute checks
   or report. Record raw values as well as classifications.
4. Append observation and case-end, write them promptly and sync. Cleanup uses
   the captured result, not volatile return registers. Record cleanup failure
   separately. Reinitialize contaminated state rather than carrying it forward.
5. Before the next case, ensure no unsaved evidence and all required cleanup
   succeeded. Buffer-full or write/sync failure halts the normal batch; never
   silently overwrite unsaved records. Finalize and decode the reconciled plan.

Isolation classes: PURE uses guarded memory; STATEFUL restores state; MEDIA
uses a fresh image/card state; EXCLUSIVE runs alone outside EXEC/OBEY with no
open script/report handle; CONTROL deliberately resets/crashes and is separate.
Raw SD writes/remount and tests invalidating file state must be EXCLUSIVE.
The ordinary boot-script batch reports those as needing a separate profile,
not silently attempting them while MOS is reading the script. Full coverage may
require multiple boots/profiles; one script cannot honestly promise survival of
arbitrary crashes or destructive media tests.

Filesystem checks inspect expected data independently after handles are released.
Checkpoints also use MOS/FatFS: keep reporting outside the mutated namespace and
capture first. Namespace separation alone does not isolate remount/raw writes.
For those, SRAM capture and externally retrieved image evidence precede any
attempt to reopen reporting. Physical-card results require a safe extraction
procedure; do not assume emulator host recovery exists on hardware.

## Preservation probe and trustworthy observations

Use a small assembly boundary with a declared capture contract. Load all test
arguments, seed unconstrained register bytes with at least two distinguishable
patterns, and compare preserved argument registers to their real entry values.
Record AF, BC, DE, HL, IX, IY with full architectural width and entry/exit SP;
record MB, caller mode and applicable interrupt state. Treat alternate registers
as a separate explicit probe capability, never implicitly covered by primary
register capture. Flags are captured before any flag-changing comparison.

The capture routine must store state without corrupting unrecorded registers.
Use a reviewed sequence of direct stores and a dedicated capture stack if needed;
restore the exact test stack before entering MOS. Correct for probe-owned return
addresses in the documented SP comparison, not by an unexplained magic offset.
The precise instruction sequence is an implementation artifact to disassemble
and independently validate. A C++ function prologue cannot serve as the first
capture point. Preserve pre-interrupt state when callbacks are part of the case;
do not disable interrupts globally to make tests pass or break blocking services.

Advertised preservation becomes an explicit per-register/per-bit mask. Outputs
are separate; unspecified flags/clobbers are observations or documentation gaps.
Capture before applying masks. Repeat success, documented error and boundary
paths, not only the happy path. C-function routes use the Zilog ABI and matching
prototypes; do not apply RST masks to them. BASIC results are complementary and
do not substitute for direct register evidence.

Mandatory harness qualification before trusting discrepancies: synthetic leaf
routines that preserve everything, intentionally change each register/upper byte
and selected flag bits, return known values, and produce known stack deviations.
The oracle is the intentional assembly mutation, independently reviewed against
captured bytes/disassembly. Include reporting code that clobbers registers to
prove capture precedes reporting. Later TEST-* tasks own durable harness and
decoder checks; qualification is a dependency, not optional extra MOS coverage.

## SRAM allocation

All 8 KiB onboard SRAM is guaranteed user-owned. Pinned mapping is
$B7E000–$B7FFFF. Use these provisional v1 allocations, checked by linker/runtime
bounds in implementation; coordinate all other user allocations with the runner.

| Offset from $B7E000 | Size | Purpose |
| --- | --- | --- |
| 0000–00FF | 256 | Discoverable control header and two generation/checksum slots |
| 0100–08FF | 2048 | Append-only unsaved record staging |
| 0900–0CFF | 1024 | Entry/exit register captures and case emergency data |
| 0D00–0DFF | 256 | Emergency reporting-failure slot |
| 0E00–0FFF | 512 | Dedicated capture stack, guarded at both ends |
| 1000–1FFF | 4096 | Guarded unused region for ownership-violation detection |

Do not execute test payload code or place ordinary buffers in this allocation.
Compare guarded unused bytes around cases; writer attribution requires tracing,
not merely finding a changed guard. Distinguish probe/user writes from stock MOS
or VDP violations. Initialization writes are deliberate user actions. Reset
wiping is allowed and destroys recovery data, including soft reset scenarios.

Control slots include magic, format version, run ID, generation, buffer extent,
next sequence and last confirmed SD sequence, capture-state code and checksum.
Update the inactive slot then publish it; select the highest valid generation
on recovery. Header fields are explicitly serialized, not a compiler struct.
Generation exhaustion ends the run. Validate bounds and checksum independently
of the active-slot hint. No multi-byte update is assumed atomic.

## Binary evidence v1 design

The [format v1 contract](result-format-v1.md) now freezes exact payload/snapshot/
control-slot layouts and manifest semantics. It supersedes provisional layout
language below; in particular, valid typed payloads require at least two bytes.


Use little-endian explicit fixed-width fields. Each independently checkable
record has the following 40-byte header, payload of 0–1024 bytes, then CRC32
and one commit byte. There is no implicit alignment padding.

| Offset | Bytes | Field |
| --- | --- | --- |
| 0 | 4 | ASCII MSTR |
| 4 | 1 | Major version = 1 |
| 5 | 1 | Record type |
| 6 | 2 | Header length = 40 |
| 8 | 16 | Run ID |
| 24 | 4 | Sequence, increasing without wrap |
| 28 | 4 | Catalogue-local case key, zero for run-level records |
| 32 | 4 | Payload length, maximum 1024 |
| 36 | 4 | Reserved flags, zero in v1 |
| 40+length | 4 | CRC-32/ISO-HDLC over header and payload |
| 44+length | 1 | Commit marker A5, written last |

Specify CRC polynomial 0x04C11DB7 (reflected 0xEDB88320), init/final xor FFFFFFFF;
known-answer ASCII 123456789 gives CBF43926. Commit plus CRC detects incomplete
records; neither guarantees atomic storage or power-loss durability. Decoders
reject unsupported major versions, excessive lengths, unknown mandatory types,
nonzero reserved bits and inconsistent IDs. Unknown types are not silently passes.

Types: 1 RUN_START, 2 CASE_START, 3 OBSERVATION, 4 CASE_END, 5 CHECKPOINT_ERROR,
6 RUN_END. Payload begins with a uint16 payload-schema version. Typed payload layouts and golden fixtures are frozen in the linked contract;
production encoder/decoder interoperability still requires qualification. Do not
dump C++ structs.
Large evidence is chunked using explicitly typed observation chunk indices and
counts, or stored in a hashed sidecar; never truncate without a recorded error.

RUN_START references bundle/catalogue/configuration/target manifest hashes and
backend. CASE_START identifies fixture/seed/path and expected contract revision.
OBSERVATION contains unmasked raw state/bytes and capture provenance. CASE_END
records disposition and expected/actual comparison references; skips carry reasons.
RUN_END summarizes outcomes and selected-plan identity. Store manifests with
results so hashes do not point at unavailable metadata. Binary evidence is primary;
classification can be regenerated with an explicitly versioned expectation set.

## Checkpoint and recovery semantics

Flush every complete record promptly; sync case-start before entering the test
and observation/case-end before advancing. Close when releasing filesystem state
or ending a group. A reported sync success means the tested software accepted it,
not proven power-loss persistence. Do not recursively report a reporting failure
through the failing reporter. Preserve its error in the emergency RAM slot and
stop. Record confirmed progress only after successful write and sync.

After a partial write/sync failure, do not append speculative retries to the
same tail. Recover and validate the prefix; resume only into a fresh artifact
with parent-run identity and explicit case selection. Re-run an interrupted case
from fresh prerequisites, never mid-instruction or with half-completed mutations.
Merge file and SRAM records by run/sequence: identical duplicates are harmless;
conflicting duplicates are corruption. Normal decoding stops at an invalid tail.
Optional forensic scanning beyond corruption labels recovered fragments uncertain
and must not infer a complete or passing run.

Emulator automation pauses on faults/timeouts, captures CPU state and the SRAM
region before reset, retrieves image state and closes the process. Verify Fab
can expose internal SRAM before implementing this recovery promise. No binary
dump command is assumed; use only documented/proven source capabilities.
Hardware has no assumed automatic watchdog or debugger. Unexpected hangs may
require manual intervention and lose uncheckpointed RAM. Persisted case-start
identifies the interrupted case; report it incomplete. Backend-specific timeout
limits and elapsed measurements are recorded, not treated as hardware equivalence.

### Restart recovery gate — planned, MAIN-05

The [restart recovery contract](restart-recovery.md) defines MAIN-05 W01 journal
bytes, transition ordering, bounded reconciliation and explicit dispositions.
W02 implements its restricted startup gate; W03 dispositions are not yet
implemented. Result-format v1 remains unchanged.

Run recovery inspection from the normal startup helper, before allocating a new
run or executing any test group. This applies to both emulator and hardware
autoexec workflows; it must not depend on an agent being present. Newly prepared startup bundles now implement the restricted W02 gate; older
bundles do not acquire it merely by updating host tooling.

Before entering a case, persist and sync its run/case identity and CASE_START.
Use a small versioned, checksummed alternating-slot SD journal to locate the
active run and distinguish execution from finalization/close phases. Freeze exact
fields and publication ordering before implementation. The journal is a locator
and conservative stop signal, not independent proof of a test verdict. Validate
the run's manifests, identities, record prefix and selected-plan completion.

On restart, an unresolved run stops automatic execution. Preserve its artifacts,
identify the last valid started case without a matching completion, and report
INCOMPLETE with any already confirmed failures. If evidence cannot locate a case,
say so. A complete record stream with an unresolved close/journal transition is
not silently promoted to a clean completion. Missing, corrupt or conflicting
journal state requires bounded reconciliation against retained run directories;
unreadable or ambiguous evidence blocks testing rather than becoming a fresh
installation. Define how a genuinely empty installation is recognized.

Call the event an interruption, not a proven test-caused reset. Manual reset,
power loss and storage errors can leave the same evidence. Attach a reset reason
only when its source is trustworthy and explicitly identified. Do not depend on
reset-persistent SRAM: MOS may wipe it. Pre-reset debugger SRAM/register/trace
capture and post-restart SD inspection are complementary recovery paths.

Recovery inspection is repeatable and performs no automatic retry. Require an
explicit human or agent disposition to retry, continue a selected remainder, or
acknowledge/park the interrupted run. Persist that decision without rewriting the
original evidence. Retry/continuation starts a new linked run with fresh
prerequisites and an explicit selection; it cannot resume an uncertain file tail,
reuse half-completed fixture state, or count unexecuted cases as passes. Another
reset during recovery or acknowledgement must still stop safely, preventing
reboot loops. Storage write failure must not clear the unresolved state.

On-device recovery helpers use C++/AgonDev. Human tools own recovery instructions
and actions; agents reuse them. Emulator checks use raw images and synthetic
interruptions, including interrupted recovery itself. Journal CRCs, alternating
slots and accepted sync calls do not establish physical power-loss durability.
Implement and qualify this gate before the first real MOS case batch.

## Human output and validation boundaries

Reports begin with the verdict, before metadata or detailed evidence:

- **ALL TESTS PASSED — N passed.** Only when every selected test ran and passed,
  with a reconciled complete run and no skips, unsupported/blocked cases,
  capture/report errors or uncertain evidence. This means the selected plan,
  not every possible suite case; state selection and backend immediately below.
- **FAILURES — N failed tests.** Count unique failing case IDs, not individual
  assertions or repeated seed observations. Immediately summarize each failing
  test by ID/function and short reason, then give detailed breakdowns.
- **INCOMPLETE** is prominent when selected tests lack trustworthy terminal
  results or infrastructure/evidence failed. If failures are also known, lead
  with **INCOMPLETE — N confirmed failed tests**; do not hide them or imply
  the failure count is exhaustive.
- **NO FAILURES OBSERVED — coverage limited.** Use for an otherwise completed
  plan containing skipped/unsupported/blocked selections. List those counts and
  reasons. An empty selection is not a passing run.

A failure here means an assertion/contract discrepancy established by valid test
evidence; documentation-only omissions and informational observations remain
separately counted findings. Harness/capture/reporting errors are infrastructure
errors, not silently attributed to MOS. Show both failed-test and failed-assertion
counts when useful, clearly labelled. Multiple observations within a test do not
inflate the headline test count. Expected-status error-path tests can pass.

After the verdict, give selection, target/backend, completion, passed/failed/
skipped/unsupported/blocked/incomplete counts and infrastructure/finding counts.
List failed tests and incomplete/blocked cases concisely before detailed sections.
Identify decoder/expectation versions and file versus recovered evidence; uncertain
fragments cannot establish a clean verdict. Keep summary counts invariant under
any detail filtering/grouping option.

### Human-readable case messages

Use **outcome + operation + verified effect + return value**, in plain language.
Name the MOS function and describe what was checked rather than emitting a
cryptic fixture marker or merely saying execution reached a location.

Examples of the pattern (not claims of tests already executed):

- **PASSED: mos_getleafname located "file.txt" and returned the expected pointer.**
- **PASSED: mos_fwrite wrote all 16 expected bytes and returned a count of 16.**
- **FAILED: mos_fwrite wrote 12 of the expected 16 bytes and returned a count of 12.**

Claim only independently verified effects. If only the returned count was
checked, say so; do not claim that file contents were verified. Where the API
has no return value, omit that clause. Preservation-only cases should name the
registers actually checked. Characterization without a contract uses OBSERVED,
not PASSED. Infrastructure faults and unfinished cases use ERROR or INCOMPLETE,
not a false target verdict. Include case ID and relevant input/path context so
similar cases remain distinguishable; detailed expected/actual values follow.

Default test-result labels are **PASSED** and **FAILED**. On colour-capable
human displays, render PASSED as white text on a green background and FAILED as
white text on a red background. Apply the badge to the status label; keep the
explanation legible in normal text. Use a sufficiently dark green/red palette
for readable white lettering and restore the normal colours after each badge.

Always retain the written labels: colour supplements meaning and is never its
only carrier. Plain-text files and unsupported terminals use uncoloured labels;
do not insert terminal/VDU control bytes into saved plain-text reports or binary
evidence. Renderer-specific colour belongs to presentation, with a plain-output
option. OBSERVED, ERROR and INCOMPLETE remain distinct from test pass/fail and
must not receive a misleading passed badge. Validate actual Agon palette/display
behaviour when implementing the on-device renderer; this specification does not
claim that coloured output is already implemented.

This per-case wording does not replace the prominent run verdict and failure
summary. Default failure-only reports need not print a success sentence for
every passed case; verbose reports can. Live progress must distinguish a case
that has started from a verified outcome.

### Initial implementation

Always emit the verdict and summary. Default detail mode is **failures only**:
show every failed test's expected/observed result and relevant evidence, plus
necessary infrastructure/incomplete-run diagnostics. Successful tests contribute
to summary counts without a detailed dump. Use stable catalogue order in the
failure list and detail section. No grouping/sorting UI is required initially.
Keep the data model rich enough that details can later be regenerated from the
binary evidence without rerunning tests.

### Later presentation options

After the harness and reports are qualified, offer only three detail modes:
**summary only**, **failures only** (default), and **verbose** (all available
passed and failed evidence, including skips/diagnostics). These are mutually
exclusive modes; verbose never removes or postpones the preliminary summary.
Summary-only retains failed-test names/reasons and the execution limitations.
Do not add a combinatorial collection of independent toggles.

Optional detail grouping can be **none**, **function name**, or **function code**.
Codes must include the route namespace (RST selector versus C-function B selector)
to avoid merging unrelated numeric codes. Within each group use stable case-ID
order. An optional **failures first** ordering promotes failures within each
group, or globally when ungrouped; order remaining categories explicitly and
stably. With failures-only detail this option is redundant. These affect only
detail presentation, never the leading failed-test summary or totals. Exact CLI
spelling and menu widgets belong to later implementation, not this design stage.

Host and on-device AgonDev C++ decoders share the format and golden vectors, not
duplicated reporting semantics. Optional progress printing occurs only after
capture/checkpoint boundaries and cannot be mistaken for the final verdict.

Required implementation checks include register-capture controls; valid/truncated/
corrupt/version-mismatched/duplicate record vectors; partial-write and sync-failure
injection; buffer-full handling; fresh-image deterministic repetition; script
comment selection/error stopping; and recovered SRAM consistency. Hardware
recovery remains unqualified until exercised. These are W03 design requirements,
not passed tests. No compiler/MOS/runtime patch is authorized by this document.

## First implementation batch and sequence — W04

### Chosen MOS slice

Start with 12 deterministic case IDs across three functions, using two valid
register seed patterns for each case (24 observations per call route, not 24
separate tests). Initially qualify the direct RST assembly route; add C++ binding
comparisons only after verifying that a matching binding exists and its prototype
is correct. The C++ runner can use a narrow assembly adapter when a binding is
absent; do not label that adapter an independent compiler binding comparison.

| Function | Four initial cases | Why it is first |
| --- | --- | --- |
| mos_getError (0F) | Codes 0, 4, 19 and 26 into separately guarded 128-byte buffers; verify each pinned string fits before execution | Observable bytes plus explicit HL/BC/DE preservation; valid inputs avoid ambiguous truncation behavior |
| mos_getleafname (3A) | `name` -> offset0; `/dir/name` -> offset5; empty string -> offset0; `dir/` -> offset4 | Pure pointer result and simple independent oracle; no advertised preservation list, so unpromised clobbers are characterization |
| mos_pmatch (28) | Literal equal; literal mismatch; mixed case with flags0; same mixed-case input with case-insensitive bit0 set | Independent match/nonmatch expectations and advertised HL/DE/BC preservation; one meaningful flag/default contrast |

For pmatch, choose concrete input pairs in fixture implementation and assert
zero versus nonzero for mismatch unless the pinned contract defines the exact
ordering expectation being tested. For getError, pin expected message bytes from
the selected baseline and annotate these as version-specific text expectations;
never obtain the expected string by calling the same API during the test.
No failure/short-buffer assumptions are smuggled into this first slice. The wider
W02 cases remain planned, including errors and boundaries not selected here.

Each test records raw full-width state, promised preservation masks, guards and
expected/observed output. Callbacks, peripherals, filesystem mutation cases,
classic mode, C-function pointers, BASIC and destructive controls are outside
this first slice. SD reporting is still a dependency and must be qualified.
A run can say all selected tests passed while explicitly identifying this narrow
selection; it must not claim the whole coverage matrix has passed.

### Implementation order and bounded follow-up proposals

These are proposed scopes/dependencies for Author review, not additional active
checklists or authorization to begin implementation. Only promoted tasks belong
in TODO. MAIN-02 already exists; other task documents should be created when
selected, with stable local work IDs.

| Stage | Owner / proposed scope | Exit evidence and dependency |
| --- | --- | --- |
| Entry points | Existing MAIN-02: human/agent front doors and wrappers around already-qualified operations | Human can find and invoke current smoke workflows; unsupported hardware procedures labelled; no dependency on an unbuilt general runner |
| Runner foundation | Proposed MAIN-03: catalogue/selection, SRAM capture boundary, binary v1 typed payloads, SD checkpoints, host text decoder and editable startup bundle | Buildable thin implementation with immutable fixture manifests and candidate format vectors; finalize payload schemas before encoder/decoder interoperability claims |
| Validate the tester | Proposed TEST-01: deliberate preserving/clobbering controls, golden records, damaged/incomplete/duplicate inputs, reporting and checkpoint failure paths | Known mutations detected, preserving controls pass, no corrupt/incomplete evidence yields all-pass; foundation is not trusted before these checks |
| Restart recovery | Planned [MAIN-05](tasks/MAIN-05.md): startup journal, recovery gate and explicit dispositions | Qualified synthetic interrupted-boot/recovery controls; no automatic retry; prerequisite to MAIN-04 |
| First MOS slice | Proposed MAIN-04: implement the 12 cases above using the qualified foundation and accepted MAIN-05 recovery gate | Two seed observations per case; ordinary headless raw-image run produces binary plus summary-first text; per-function script selection agrees with shared catalogue |
| Human hardware parity | Follow-on scope to promote after first slice: same bundle on hardware, retrieval and on-device C++ report helper | Physical run independently reported; no emulator result substituted for hardware validation; device/report procedure actually exercised |

MAIN-03 and TEST-01 have an intentional iteration: implement a candidate capture
or decoder component, exercise its independent controls, then correct that
component before consuming its output as MOS evidence. This is not permission
to patch MOS when a control or case fails. New on-device helpers remain
C++/AgonDev, with reviewed assembly only at the exact capture/call boundary.

The initial text report uses a leading verdict and counts, failed-test list,
then failure details in stable order. Verbose/grouping/menu features are deferred.
The host decoder is the first implementation; human hardware reporting includes
an on-device C++ decoder in the later parity scope rather than pretending it
exists in the foundation. Humans may initially retrieve a binary card report
for host decoding once that retrieval procedure is documented and verified.

### Subsequent coverage order

After the first slice, expand deterministic strings/default flags, status and
sysvar queries, then handle-based filesystem lifecycle and direct FatFS routes
with independent image inspection. Add path/variable translation and stateful
sequences; only then widen to mixed-mode/C-function ABI and selected BASIC routes.
Keyboard/VDP/RTC follow once stimulus and observation capabilities are qualified.
UART/I2C/interrupt and fault-injection branches need explicit hardware fixtures
or verified emulator capabilities. Raw-media/remount/reset/crash profiles remain
separate because they can invalidate the reporting or script execution environment.

Order within each group follows prerequisites and available independent oracles,
not selector number. Retain preservation/default coverage across all relevant
paths as each family is implemented. Minimize discrepancies into documentation
reproducers; keep MOS-01 parked. Runtime/hardware claims begin only when the
corresponding implementation tasks produce evidence.
