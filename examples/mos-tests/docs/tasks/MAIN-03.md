# MAIN-03 — Runner foundation

## Summary

Implement the smallest shared runner that selects cases, captures trustworthy
binary observations in onboard SRAM, checkpoints early and often to SD, and
produces summary-first human reports. Deliver an editable autoexec.txt workflow
through the existing human/agent entry points. Qualify each component with
[TEST-01](TEST-01.md) before using it as evidence about MOS.

## State and scope

Reconstructed contract checkpoint. Completed items: W01, W02.
Remaining work is frozen and unstarted at this checkpoint. The subproject TODO
owns unfinished task indexing. This is a retrospective grouping, not an exact
previous edit version or a backdated acceptance record.

## Work

- W01 [x] Freeze the executable data contracts.
  Specify typed v1 payload layouts, register snapshot fields and preservation
  masks, catalogue/selection manifest and run identities, checkpoint state and
  error dispositions. Confirm envelope, CRC, SRAM bounds and generation rules
  against the strategy. Define known-answer bytes with TEST-01 W01 independently
  of serialization code. Publish maintained format documentation; do not dump
  compiler structs or duplicate upstream API contracts.
  **Completed** — [frozen format](../result-format-v1.md), maintained
  fixtures/format-v1 (six record types, 44 capture vectors, 14 report scenarios)
  and [W01 checks](MAIN-03/W01/validation.txt). These define independent
  expectations; production encoding/capture/report qualification remains pending.
- W02 [x] Implement the shared catalogue and bounded runner lifecycle.
  Add synthetic case descriptors and immutable IDs, per-function/group/exact-case
  selection, stable ordering, declared backend capabilities and fresh run output.
  Reject unknown/empty selections and collisions. Persist the selected plan;
  distinguish skipped, unsupported, blocked and incomplete outcomes from passes.
  Keep the root smoke and promoted comparison usable while adding the runner.
  **Completed** — shared host/Agon C++ selector, validated synthetic catalogue,
  persisted planning artifacts, lifecycle hooks and human front ends are in
  maintained locations. [W02 checks](MAIN-03/W02/validation.txt) cover native
  lifecycle/selection failures and the AgonDev build. Plans remain unexecuted;
  capture, durable hooks and binary run records connect in subsequent items.
- W03 [ ] Implement and qualify immediate register capture and SRAM staging.
  Use the agreed $B7E000–$B7FFFF user-owned layout, explicit mapping checks and
  guarded boundaries. Capture full-width entry/exit registers, applicable flags
  and stack context before reporting. Retain disassembly and probe accounting.
  Integrate TEST-01 W02 preserving/clobbering controls; do not trust register
  discrepancies until those controls pass. Record intentional user writes so
  SRAM ownership-violation findings can be attributed correctly.
- W04 [ ] Implement binary recording and frequent SD checkpoints.
  Serialize v1 records, CRC and commit marker; sync case-start before entry and
  observations/end before advancing. Track confirmed progress, preserve emergency
  state and halt cleanly on short writes, sync errors or capacity exhaustion.
  Keep filesystem operations outside capture windows and establish preconditions
  after checkpoint side effects. Integrate TEST-01 W03/W04. Do not claim
  power-loss durability or run destructive media cases from an open script.
- W05 [ ] Implement the host decoder and initial human report.
  Validate identities, lengths, CRC, version, duplicate sequences and selected-plan
  completion. Decode saved files and explicit recovered buffers with provenance.
  Lead with all-pass only for complete selected coverage; otherwise give failed
  test counts/list or prominent incomplete/limited coverage, then failure details.
  Use PASSED/FAILED operation/effect/return wording, white-on-green/red badges on
  supported terminals and a plain mode without control codes in saved text.
  Keep OBSERVED/ERROR/INCOMPLETE distinct. Integrate TEST-01 W03/W05. Defer verbose,
  grouping, menu and on-device decoder enhancements to later bounded work.
- W06 [ ] Deliver and validate editable startup selection and shared front ends.
  Supply a verified !boot.obey -> EXEC /autoexec.txt chain with commented function
  groups and LOAD/RUN commands. Preserve run identity/plan across group invocations
  so missing groups/finalization cannot yield all-pass. Test disabling a complete
  group and unknown selection. Persist discrepancies but return normally so EXEC
  continues; infrastructure errors stop it. Reuse human/mos-tests and link agent
  guidance to the same operations. Verify with raw images, headlessly; document
  what can be copied to hardware without claiming an unperformed hardware run.
- W07 [ ] Exercise end-to-end qualification and record delivery limits.
  Run the complete TEST-01 synthetic acceptance set and a fresh-image repeat,
  retaining binary/text evidence and exact runtime/toolchain identities. Verify
  all processes close and previous runs survive. Attempt controlled emulator SRAM
  retrieval before reset using supported tools; report recovery as unsupported
  if that capability cannot be established rather than manufacturing evidence.
  Promote mature helpers into maintained locations and update human/agent guides,
  handoff and task status. No real MOS conformance claim from synthetic controls.

## Dependencies and sequencing

MAIN-03 W01 and TEST-01 W01 establish independent contracts/oracles. Implement
one component and qualify it immediately: W03 with TEST-01 W02; W04 with TEST-01
W03/W04; W05 with TEST-01 W03/W05; W06/W07 with TEST-01 W06. The two tasks
iterate together, rather than deferring all harness checking until the end.
A failing synthetic control is a foundation problem to resolve before MOS cases.

## Acceptance criteria

1. The same catalogue and shared execution/report semantics serve human and agent
   tools; no duplicated engine or routine dependency on task-silo experiments.
2. Independent controls detect intended register/flag/stack changes without false
   preservation failures; binary records decode identically against golden data.
3. Normal, partial and faulty runs produce truthful summaries. Missing evidence,
   skips, corruption and reporting failures cannot become an all-pass headline.
4. Raw-image startup selection and checkpoints work end-to-end with a fresh run;
   exact binary/map/runtime/configuration identities and evidence are retained.
5. Hardware, recovery and unsupported features have explicit qualification limits.
   SRAM is not reset-persistent. Behavior discrepancies do not authorize patches.
6. TEST-01's required foundation controls pass before proposing the first real
   MOS case batch. Human review/commit requirements remain in AGENTS.md.

## Workspace

Use MAIN-03/ for bounded trials and evidence. Promote production code/docs as
specified in the strategy, retaining provenance. Preserve all W identifiers and
explicit Completed/Deferred/Canceled dispositions; no silent scope deletion.
