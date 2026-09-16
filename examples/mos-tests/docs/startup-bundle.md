# Editable startup bundle implementation

MAIN-03 W06 connects the qualified capture/recorder/reporter through actual MOS
OBEY and EXEC, with target-side plan derivation, distinct repeated-boot identities
and conservative same-boot continuation. It exercises synthetic controls only.
[Human startup instructions](../human/startup.md) own the user workflow.

## Ownership and paths

1. apps/startup-runner is a C++14 AgonDev application. It includes the shared
   catalogue, capture, recorder, storage and lifecycle components. A small assembly
   fixture supplies two seeded preserving/clobbering capture routes. No MOS or
   emulator source is changed. apps/runner remains the shared catalogue selector.
2. scripts/startup_bundle.py uses the existing validated catalogue generator,
   builds the helper, creates exact file hashes and verifies raw-image deployment
   by independent mtools readback. Target-side SHA-256 is checked against hashlib
   across block/padding boundaries and against actual report hashes.
3. The generated subset uses LOAD /mos-tests/runner.bin followed by RUN . begin,
   RUN . function NAME or RUN . finalize. apps/startup-runner/include/script.h
   owns the bounded target parser; native qualification compiles that same code.
   The planner's ordered function selection matches the shared catalogue. Seven
   compact plan templates represent the three current controls. This is explicitly
   bounded foundation tooling, not a scalable thousand-function template strategy.
4. The actual autoexec bytes are scanned and hashed at begin; active groups select
   one template, whose script hash is filled before plan.json is persisted. A run
   carries real bundle/catalogue/plan/target hashes plus all bundle artifacts.
   The bundle's files.lst digest is checked against bundle.json, and listed files
   are hashed before copying. These are integrity links and declared provenance,
   not cryptographic attestation of hardware or resistance to a malicious operator
   rewriting an entire bundle. The host builder owns the generated table.
5. /mos-tests/install.bin is 24 bytes: installation namespace8, monotonic u64 LE
   counter8, CRC32 over those16, then MSTI. Allocation checks CRC, increments and
   write/sync/closes the counter before mkdir of a run-ID directory. Counter wrap,
   allocation corruption/collision or failed persistence stops. Power-loss atomicity
   is not claimed; collision refusal prevents overwriting earlier evidence.
6. Results live in /mos-tests/runs/<32-hex-digit-ID>/. Each contains manifests,
   fixtures, exact selection bytes and results.bin. Reboot allocates a new run,
   never resumes an uncertain record tail. Hardware target identities are explicit
   operator declarations; emulator execution verifies profile hashes before launch.

## Across LOAD/RUN boundaries

1. A private CRC-protected invocation context occupies SRAM offsets A00–CFF,
   within the already reserved capture area. It contains identity/hashes, selection,
   next expected group, counters, expected file length and run path. This private
   same-build C++ layout is not a public result format and is never dumped onto
   disk as a wire record. Captures remain at 900/920; control/staging/emergency
   regions retain the frozen format. These writes are intentional user allocation.
2. The next command checks the script hash, invocation context and next group.
   continuation.h restores only a valid highest-generation READY control slot
   with zero current case/staging and consistent confirmed/next sequence. Equal
   conflicting generations, foreign identities, reserved-field errors and unsafe
   states are refused. The reopened result file must have the exact expected
   length before seeking to its end. This is clean command continuation, not
   crash recovery or resume after reset.
3. Shared lifecycle hooks sync case-start before register seeding and observations/
   case-end before advancing. Both samples are checked against the case's explicit
   expected register delta. The known-clobbering case masks only the expected IX
   upper bit out of its preservation promise and separately checks that exact delta.
4. Clean per-group close precedes saving the next invocation context. Discrepancies
   remain FAILED records but return zero to EXEC; later groups continue. A fatal
   error returns nonzero, and EXEC stops. Finalize requires all selected groups,
   writes/syncs RUN_END, closes, publishes ENDED state and invalidates continuation.
5. Qualification fault.bin is an explicit hashed bundle artifact: 0 ordinary,
   1 deliberate first-control discrepancy, 2 injected infrastructure stop, 3 comment
   mutation after begin to test script-hash rejection. These are test controls,
   never silent production fault injection. Default preparation writes zero.

## Observation and limits

agents/run_startup.py reuses human/shared preparation and reporting, adding PTY
orchestration. It observes each command boundary and eventual _mos_input, extracts
complete card run directories and SRAM, and closes its emulator. Report provenance
records before-reset acquisition. The observer uses -u for speed and makes no
timing claims. Existing unrelated processes are not touched.

Qualification uses raw --sdcard-img exclusively. The initial throttled full run
was about 48 seconds; -u trials with preparation excluded but execution/retrieval/
decoding included were about 9 seconds each. These are host durations, not device
benchmarks. Hardware, arbitrary crash/reset recovery and power-loss durability
remain unqualified. An inspected unused SRAM range contained FF, not zero; no
zero-initialization or fresh guard qualification is inferred from these trials.

Read-only source references: agon-mos/main.c startup selection and src/mos.c
mos_EXEC/mos_cmdOBEY at the pinned MOS revision; AgonDev libcrt0 argument processing
and MOS file wrappers. !boot.obey explicitly invokes EXEC /autoexec.txt to retain
the local missing-OBEY workaround. MOS-01 remains parked.
