# MAIN-05 — Recover interrupted runs on restart

## Summary

Add a startup recovery gate before real MOS testing. A restart must preserve and
report unfinished work, then wait for an explicit disposition instead of rerunning
a crashing case indefinitely. SD checkpoints support restart recovery; SRAM
retrieval is a separate before-reset opportunity.

## State and sequencing

W01 authorized on 2026-09-16. MAIN-03 W07 and TEST-01 accepted.
This checkpoint freezes W01 scope before contract design; implementation is unstarted.
Runs **before the proposed MAIN-04 first MOS slice**. MAIN-04 retains its existing
proposed identity; task numbers do not prescribe execution order.
W01 delivers docs/restart-recovery.md plus independent transition expectations
in docs/tasks/MAIN-05/W01/. Validate field offsets/bounds and review all restart
windows against current startup/recording code. Do not implement W02 in W01.
The subproject-root TODO is the sole unfinished-work index.

Design authority: [restart recovery](../test-strategy.md#restart-recovery-gate--planned-main-05).
No firmware patch, physical deployment, automatic watchdog, general crash
debugger, menu application or claim of power-loss atomicity is included.

## Work

- W01 [ ] Freeze the recovery state and storage contract.
  Specify journal fields/version, alternating-slot CRC/generation rules,
  run/case/phase identity, publication ordering around CASE_START, CASE_END,
  RUN_END and close, and bounded discovery/reconciliation when the journal is
  missing or damaged. Define empty-installation evidence and ambiguous-state
  handling. Specify acknowledgement publication and interruption-safe behavior.
  Freeze independent expected outcomes before building the reader/writer.
- W02 [ ] Implement the shared startup recovery gate.
  Inspect before run allocation and before test execution through autoexec.
  Reuse validated manifests/records; preserve originals and surface interrupted,
  corrupt, conflicting or unreadable state prominently. Retain confirmed
  failures. Never infer a reset cause or a pass from missing evidence.
  Implement the on-device helper in C++/AgonDev with bounded storage operations.
- W03 [ ] Add explicit recovery dispositions to human tools.
  Document and implement retry, selected continuation and acknowledgement/parking
  with durable provenance. New execution gets a new run identity and parent link;
  require fresh fixture prerequisites and explicit selection. Agents invoke the
  same tools. No default retry, uncertain-tail append or silent evidence deletion.
- W04 [ ] Qualify restart and recovery interruption behavior.
  Use independent synthetic controls and fresh/reused raw images. Cover clean
  completion/reboot; interruption before/after synced CASE_START and CASE_END;
  RUN_END versus close/journal boundaries; missing/corrupt/conflicting journal;
  unavailable storage; truncated records; repeated boots without disposition;
  interruption during acknowledgement; explicit retry/continuation and previous
  evidence preservation. A forced process stop/reboot is a controlled
  interruption, not proof of a real CPU reset or card power-loss behavior.
  Verify no test re-entry without disposition and no false all-pass. Retain
  exact identities, binary/text evidence and closed-process checks.
- W05 [ ] Deliver recovery guidance and record qualification limits.
  Promote mature helpers from docs/tasks/MAIN-05/ into maintained locations.
  Update human startup/recovery instructions, agent links, handoff and status.
  Distinguish supported pre-reset capture from post-reset SD recovery; hardware
  remains unqualified until independently exercised. On acceptance checkpoint
  results before freezing/starting the first real MOS cases.

## Acceptance criteria

1. An unresolved prior run blocks normal startup execution on repeated boots;
   an explicitly verified clean installation/completed run follows normal startup.
2. Last valid case/phase and confirmed failures are reported accurately, with
   uncertainty prominent. Corruption, missing records or pending close cannot
   create a false pass; no unsupported causal diagnosis is made.
3. Recovery and disposition survive interruption conservatively. Prior evidence
   is retained; retry/continuation cannot form an automatic reboot loop.
4. Humans and agents share tools and semantics. Both deployment routes have
   instructions; emulator qualification does not claim hardware validation.
5. Synthetic qualification evidence supports every claimed transition and limit.
   No production testing begins until this prerequisite is accepted.

## Task workspace

Keep experiments and evidence in docs/tasks/MAIN-05/Wnn/. W identifiers are
immutable; preserve completed, deferred and canceled items and their rationale.
