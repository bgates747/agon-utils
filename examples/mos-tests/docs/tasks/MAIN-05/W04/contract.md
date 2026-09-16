# MAIN-05 W04 — Interruption qualification contract

## Summary

Qualify the shared recovery engine across durable publication boundaries on
Linux raw SD images. W03 is accepted. Freeze this scope with its result commit
before adding instrumentation or executing W04 experiments. W05 remains separate.

## Work and acceptance

- Q01 [ ] Add observational boundary hooks outside register-capture windows.
  Identify journal destination phase and write/sync/close/readback stage; result
  CASE_START/CASE_END/RUN_END write/sync/close stages; allocation and recovery
  receipt/certificate publication. Hooks do not change normal outcomes or disk
  formats. Extend the shared observer to select a particular boundary and retain
  its identity, debugger trace, journals, SD files and SRAM. No invented debugger
  memory/register setters. Same binary/map establishes addresses.
- Q02 [ ] Freeze an independent case matrix before running the sweep.
  Map R01–R30 from fixtures/recovery-v1/expected-transitions.json to new trials,
  retained accepted controls, native controls or explicit supported-profile
  limits. Every ID needs an evidence/disposition entry; no inferred coverage.
  Before COMPLETE/accepted authorization, a stop must not enable fresh execution.
  After COMPLETE with matching evidence, ordinary reboot is allowed. A synced
  CASE_END retains its outcome; RUN_END without confirmed final publication is
  incomplete. Compare original bytes before/after blocked restart.
- Q03 [ ] Run lifecycle and journal interruption trials.
  Cover allocation intent/counter publication; CASE_INTENT, CASE_START write and
  sync, IN_CASE, CASE_END write and sync, CASE_DONE, group close/BETWEEN;
  FINALIZING, RUN_END write/sync, result close, COMPLETE. Sweep journal slot
  invalidation, body, commit marker, sync, close and readback using a representative
  active-case publication, and check the decisive COMPLETE publication boundary.
  Repeated blocked boots must not allocate or enter the payload.
- Q04 [ ] Run recovery-publication and damaged-state trials.
  Cover DISPOSING, receipt write/sync/close/readback, PARKED/ARMED publication,
  acceptance-certificate write/sync/close/readback, child ALLOCATING and a later
  interruption during explicitly authorized retry. Preserve orphan files and
  parent findings; no silent automatic disposition replay.
  Exercise equal-generation conflicting slots, unknown versions/phases/actions,
  exhausted generations, allocation/history mismatch, unreadable storage entries,
  truncated records and interrupted runs with confirmed failures. Inject bounded
  journal I/O error returns for write/sync/close/readback if practical, through
  explicitly labelled qualification artifacts; these are simulated returns,
  not claims that the physical card failed.
- Q05 [ ] Retain results, fix suite defects within the frozen semantics, and
  rerun affected controls plus appropriate regression checks. Promote the reusable
  checker to human/mos-tests with agents reusing it. Record runtime/source hashes,
  archive portable evidence, update task/handoff/TODO and close owned emulators.
  Do not implement firmware/compiler changes or unsupported recovery/migration.
  Any change to frozen behavior requires a separately committed contract change.

## Interpretation and limits

A boundary before fsync may already have readable bytes; it cannot prove durable
power-loss survival. Likewise a COMPLETE or acceptance marker can be durable
before the helper returns: after a fresh fully validating boot, that durable
state may authorize execution even if the previous host never observed success.
Record this distinction explicitly; do not equate missing host acknowledgement
with missing durable authorization.

Controlled debugger stop/process exit/next boot is not a CPU reset or physical
power cut. We do not cover every machine instruction, FAT internal transaction,
or all combinations of multiple simultaneous faults. Existing bounds and strict
same-bundle synthetic profile remain; malformed/truncated tails can remain
blocked without a repair tool. Hardware stays unqualified. No graphical emulator,
firmware repair, upstream contact or W05 execution is authorized by this item.
