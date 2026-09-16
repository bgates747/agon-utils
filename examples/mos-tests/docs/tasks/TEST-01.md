# TEST-01 — Qualify the runner, capture and reports

## Summary

Test the test machinery using deliberately known outcomes. Establish that capture,
serialization, checkpoints and reports detect failures without inventing them or
turning incomplete evidence into passes. This task qualifies [MAIN-03](MAIN-03.md);
it does not test MOS conformance or authorize firmware changes.

## State

Reconstructed contract checkpoint. Completed items: W01, W02, W04.
Remaining work is frozen and unstarted at this checkpoint. The subproject TODO
owns unfinished task indexing. This is a retrospective grouping, not an exact
previous edit version or a backdated acceptance record.

## Work

- W01 [x] Define independent controls and golden evidence.
  Write readable expected register changes and manually inspectable wire records,
  CRC known answers, case plans and report totals. Include explicit byte-order,
  width and upper-byte checks. Record the rationale so tests do not merely mirror
  serializer or comparison implementation. Agree contracts with MAIN-03 W01.
  **Completed** — [frozen format](../result-format-v1.md), maintained
  fixtures/format-v1 (six record types, 44 capture vectors, 14 report scenarios)
  and [W01 checks](TEST-01/W01/validation.txt). These define independent
  expectations; production encoding/capture/report qualification remains pending.
- W02 [x] Qualify the assembly capture boundary.
  Exercise preserving controls and intentional changes to each captured register,
  upper byte and promised flag; check known return values and stack accounting.
  Use at least two valid seeds and reporting code that clobbers registers after
  capture. Verify exact changes and absence of extras using independent debugger
  observations/disassembly where useful. Isolate deliberate stack deviations so
  the control does not silently corrupt the runner. Distinguish untested state
  such as alternate registers from qualified primary-register coverage.
  **Completed** — [W02 qualification](TEST-01/W02/validation.md), with 52
  synthetic controls, independent CPU-state comparisons and guarded SRAM retrieval.
  Limits include IFF, alternate registers/modes and hardware; no MOS claim.
- W03 [ ] Validate record encoding, decoding and recovery interpretation.
  Check golden records, zero/max payloads and boundaries, unsupported versions,
  invalid lengths/CRC/commit markers, truncation at each structural boundary,
  missing/reordered/conflicting records and identical duplicates. Unknown case/run
  identities cannot be accepted blindly. Test strict valid-prefix decoding and
  separately labelled forensic fragments; no recovery fragment proves completion.
- W04 [x] Exercise checkpoint and buffer failure paths.
  Inject short writes, write/sync errors, full staging buffer and interrupted
  header updates at controlled abstraction boundaries. Verify bounded emergency
  evidence, no silent overwrite, no recursive failed reporting and no progression
  to another ordinary case after unsafe failure. Preserve prior runs. Synthetic
  fault injection validates runner handling, not real card power-loss guarantees.
  **Completed** — [checkpoint qualification](TEST-01/W04/validation.md):
  storage, buffer and counter failures stop safely; interrupted publication and
  prior-run preservation checks passed. Hardware/power-loss behavior untested.
- W05 [ ] Qualify verdicts and human report semantics.
  Fixture plans cover all-pass, single/multiple failing tests, multiple failed
  assertions in one test, expected-error test passes, skips/unsupported/blocked,
  no selected cases, incomplete execution and infrastructure errors. Verify counts
  and failing-test names before details. All-pass requires complete selected
  coverage. Check plain output has no colour controls, coloured status labels
  reset correctly and messages claim only observed effects. Future presentation
  modes must reuse invariant summary totals when introduced.
- W06 [ ] Validate startup selection and an end-to-end synthetic run.
  Exercise full and single-function plans, commented-out LOAD/RUN groups, unknown
  names, missing finalization and command failures through the human front end.
  Verify discrepancies persist while later groups continue, infrastructure errors
  stop EXEC, and plan reconciliation detects missing cases. Save fresh-image
  repeat evidence with identities. Validate emulator RAM retrieval only if the
  backend supports it; separate that capability result from checkpoint evidence.

## Acceptance criteria

1. Known-preserving controls pass and intentional changes produce precisely the
   expected findings. A failed control blocks use of that observation mechanism.
2. Golden-byte evidence agrees with encoder/decoder results and malformed inputs
   are classified honestly without crashes, unbounded reads or false passes.
3. Fault handling retains earlier evidence and reports missing work explicitly.
   Summary counts do not confuse failed assertions with unique failing tests.
4. The shared human/agent startup route is verified with synthetic cases on raw
   images. No hardware or firmware conformance claim is inferred from this.
5. Evidence and control limitations are retained, with reproducible commands and
   backend/toolchain identities, before MAIN-03 is declared qualified.

## Workspace and promotion

Keep bounded trials in TEST-01/. Promote reusable controls and format/report
fixtures into maintained test locations alongside the foundation. Preserve stable
W IDs and explicit dispositions. No parallel agent work is required or requested.
