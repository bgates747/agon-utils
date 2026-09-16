# MAIN-05 W02 — Startup recovery gate

The gate is implemented and passed headless raw-image qualification on Linux.
Interrupted or ambiguous state blocks execution before a new run is allocated;
repeated boots preserve prior evidence. W02 awaits Author acceptance/checkpoint.
W03 dispositions and W04 broader interruption coverage are still outstanding.

## Implementation

1. C++ journal primitives serialize the frozen 256-byte format, validate both
   generations/transitions, and publish by invalidate/sync, body/sync, commit/sync,
   close and exact readback. Single-slot fallback cannot authorize a boot.
2. New bundles provision IDLE journal slots separately from immutable artifacts.
   The target records allocation intent before counter mutation; case intent
   before CASE_START; IN_CASE before payload; CASE_DONE after synced CASE_END;
   COMPLETE only after result finalization and close.
3. The startup gate reconciles bounded run history, namespaces/counters, exact
   canonical manifest/hash relationships, every declared artifact, record order,
   selected controls, observations and outcome totals. It streams records and
   rejects unsupported inputs conservatively. Same-boot invocations must match
   the journal and SRAM session before proceeding.
4. RUN . inspect performs read-only inspection. Existing human startup tooling
   retrieves the target decision, both slots, allocation file, previous records,
   SRAM and debugger transcripts. Human instructions are in human/recovery.md;
   agents reuse those tools.
5. Report integration retains confirmed failed test counts/names and propagates
   unresolved journal/command evidence via --incomplete-reason. A complete-looking
   file cannot override that uncertainty. Existing record outcomes are retained.
6. W01's independent fixture and R01–R30 expectations were promoted unchanged to
   fixtures/recovery-v1; routine checks no longer depend on a task-silo path.

## Qualification

1. ./human/mos-tests recovery-check --output .emulator/recovery/check-04 passed.
   Seventeen raw-image boots took 189.629 seconds in total observed boot/retrieval
   time; this excludes some host setup/compilation and is not CPU timing evidence.
2. Native ASan/UBSan checks accepted the independently authored IDLE fixture,
   rejected all 2,048 single-bit corruptions, checked pair/semantic rejection,
   and exercised all 121 phase-pair decisions against a separate explicit edge
   list. A real captured record stream passed; CRC-correct malformed structure
   was rejected. These are synthetic harness checks, not MOS conformance.
3. Clean and repeated boots completed with new identities and preserved previous
   files. Two successive boots after interruption both stopped with target status
   41 without changing journal/allocation files or prior run evidence.
4. A debugger stop at _startup_probe, before payload execution, left synced
   CASE_START and IN_CASE. The next process boot identified case 1 and blocked.
   A known failure followed by interruption remained a confirmed failure.
5. Missing/corrupt journal slots, damaged results/manifests and an overlong JSON
   manifest all blocked. Read-only inspection changed neither journal/counter
   nor retained runs. Completed test failures permitted normal repeated boots
   and retained FAILURES verdicts.
6. Unresolved observer evidence changed a complete record stream to INCOMPLETE
   while retaining its two passed case outcomes. A final human CLI check returned
   2 with INCOMPLETE first, then “Confirmed failed tests: 1
   (control.preserve.001)” before retained-run details.
7. Regression: all ten startup scenarios and native script/hash/continuation
   controls passed; all 58 report scenarios plus 690 truncations and 690
   corruptions passed; C++ and independent assembly smoke variants passed.
   Individual bundles retain exact tested hashes. Final target-only change after
   qualification removed an EOF blank line; rebuilding produced identical bytes.
8. No project-owned Fab emulator processes remained. No graphical emulator or
   physical hardware was used. Git whitespace checks passed.

## Evidence and encountered compiler failure

[result.json](result.json) lists the final 17 boots, durations and statuses.
[qualification.tar.gz](qualification.tar.gz) retains 6,006 files spanning trials,
final qualification, regressions, records, manifests, maps, debugger transcripts,
journal bytes and reports. [SHA256SUMS](SHA256SUMS) checks both archives.
Raw images and host executables remain under .emulator/recovery/; omissions are
listed in archive-omissions.json. [source-identities.json](source-identities.json)
pins final sources; per-bundle toolchain/target manifests pin tested versions.

The first build crashed in AgonDev Clang 15.0.7 with “unable to legalize
instruction” for an i9 constant in the boolean transition expression.
[compiler-failure.tar.gz](compiler-failure.tar.gz) retains the preprocessed source,
driver script and compiler output. Replacing the expression with an equivalent
transition table avoided the crash; all table decisions are independently checked.
No compiler or firmware patch, maintainer contact or upstream publication occurred.

## Supported profile and remaining limits

1. W02 accepts this bundle's canonical serialization and the three synthetic
   controls. It rejects different builds/manifests, parent-linked runs, recovery
   receipts and W03 disposition states. This is deliberately stricter than the
   host decoder; it is not a general on-device JSON/report decoder.
2. The frozen history/record/JSON/script bounds apply. The implementation also
   caps a hashed artifact at 1 MiB and aggregate hashed bytes at 64 MiB per
   inspection. Exhaustion blocks; it never ignores remaining evidence.
3. Legacy installations without provisioned journals stop. No implicit migration,
   journal clearing, automatic retry, parking or continuation is implemented.
   Keep the stopped installation; W03 supplies explicit actions.
4. Qualification used controlled process exits/next boots, including a pre-call
   debugger stop. It does not establish physical reset causation, card power-loss
   atomicity, arbitrary crash recovery or hardware behavior. SRAM recovery must
   occur before reset. MOS-01 stays parked.
5. W04 still owns systematic interruption at every write/sync/close/acknowledgement
   boundary and broader R01–R30 coverage. W02 does not claim all 30 recovery
   expectations have been exercised end to end.
