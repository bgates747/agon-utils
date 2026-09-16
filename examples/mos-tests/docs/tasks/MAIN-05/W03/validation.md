# MAIN-05 W03 — Explicit recovery dispositions

Implemented and qualified on Linux; accepted by the Author on 2026-09-16.
W02 was accepted and committed with the frozen W03 contract as a4694a9.
The Author authorized committing/pushing W03 and proceeding to W04. The W04
contract is frozen with this checkpoint before implementation.

## Implementation

- The target C++ recover command validates a bounded explicit request against the
  current subject/generation, selected original-plan cases, deployed script and
  prerequisite confirmation.
- DISPOSING precedes immutable journal snapshots and the evidence-hashed JSON
  receipt. PARKED/ARMED publication precedes a separate acceptance certificate.
  Missing or invalid acceptance evidence cannot authorize a child.
- Park stays stopped. Retry explicitly selects original-plan cases. Continuation
  excludes cases with a valid CASE_END. A child consumes authorization by publishing
  ALLOCATING before counter mutation and uses a fresh identity.
- Child schema2 binds disposition.json in its bundle/record provenance. Parent
  outcomes remain separate and original files stay unchanged. Later ordinary runs
  return to schema1.
- Human and agent workflows share human/mos-tests recover and the same target
  engine. The host restores !boot.obey after the recovery boot and retrieves
  receipts, snapshots, journals, reports and debugger evidence.
- Mature qualification lives in tests/disposition; earlier trials remain here.
  Guidance lives in human/recovery.md and the maintained result/recovery designs.

## Focused qualification

The maintained tests/disposition/check.py suite passed 18 check groups over
29 raw-image boots in .emulator/disposition/qualification-02. ASan/UBSan native
controls covered structural/duplicate JSON errors, UTF-8, depth/token/size bounds,
integer overflow, truncations and writer escaping. Target negative requests
preserved the original journal/allocation/results exactly.

Positive cases covered park/repeated stopped boots, selected continuation,
explicit retry, separate schema2 child outcomes, schema1 ordinary execution after
a completed child, and stale authorization rejection. Receipt and certificate
tampering blocked. Stops after receipt durability and ARMED publication required
fresh explicit requests; the orphan bytes were retained and committed by the
new receipt. Stopping after child ALLOCATING consumed authorization before any
counter mutation; the next boot stayed blocked.

The separate tests/disposition/failure.py check passed three more boots with a
deliberate parent failure. A passing one-case child retained the parent failure
and original bytes. It also verified the newly exposed expected-generation field.
This check is now included by the maintained disposition-check front end.

The main suite had already loaded the host observer before the generation-display
addition; the supplemental run and subsequent regressions use the final host
observer. The target implementation was unchanged between these runs. Evidence
source hashes identify the final maintained snapshot; no claim is made that
every intermediate host-driver edit was the version loaded by the first process.

## Development failures retained

Trial-01 wrote a malformed receipt evidence map. The next boot rejected it.
The implementation now derives delimiters from the output buffer and parses/
validates the complete generated receipt before publishing acceptance. No
compiler fault is inferred from this symptom. Trial-02 passed park and selected
continuation with separate incomplete-parent and passing-child reports.

The first native test used a temporary string beyond its lifetime; ASan caught
the qualification harness defect. The harness now owns input storage. This was
not a target-parser use-after-free; its scratch storage is static.

## Supported limits

Only the same canonical synthetic bundle is supported. Corrupt journal pairs,
malformed/truncated record tails, allocation gaps and identity ambiguity remain
blocked without a repair tool. Bounded JSON/history/hash limits may stop earlier
than the maximum receipt count; exceeding a limit never discards old evidence.

Controlled debugger stops and subsequent boots are not hardware reset or
physical card power-loss tests. Hardware remains unqualified. W04 owns the
broader individual write/sync/close interruption sweep. MOS-01 stays parked.

## Final regressions and evidence

All required regressions passed on 2026-09-16:

- recovery-check: 17 raw-image boots, 2,048 native bit-corruption controls and
  121 transition decisions; damaged manifests/results/slots and completed
  failure behavior remain conservative.
- startup-check: 10 boots plus SHA, selection-parser and continuation controls.
  Full/single/commented selection, deliberate failure, infrastructure stop,
  changed script, missing finalization/group and repeat identity preservation pass.
- report-check: 58 scenarios, 690 truncations and 690 corruptions.
- smoke: both C++ and independent assembly variants pass headlessly on raw images.
- Python syntax checks, front-end help dispatch and scoped git diff whitespace
  checks pass. No project-owned Fab emulator remained after qualification.

The focused 32 boots and 27 startup/gate regression boots used the pinned Fab
1.2.4 / MOS 3.0.2 Arthur profile. Runtime SHA-256 identities are verified and saved
by every startup observer invocation; maps, binaries, reports, journal bytes,
receipts and debugger transcripts are retained. Observed elapsed time is not
CPU or MOS timing evidence.

Live evidence is under
/home/smith/Agon/mystuff/agon-utils/examples/mos-tests/.emulator/disposition/.
The durable qualification.tar.gz archive excludes disposable full-card images
and Python bytecode; intentional escape-test symlinks are retained as target-name
metadata, not live archive links. evidence-manifest.json identifies file inputs by SHA-256;
qualification.sha256 identifies the archive. Trial-01 failed artifacts and
Trial-02 positive evidence are included with the final qualification.

Reproduction from the Linux subproject root:

```sh
./human/mos-tests disposition-check --output .emulator/disposition/new-check
./human/mos-tests recovery-check --output .emulator/disposition/new-gate
./human/mos-tests startup-check --output .emulator/disposition/new-startup
./human/mos-tests report-check --output .emulator/disposition/new-reports
./human/mos-tests smoke --output .emulator/disposition/new-smoke
```

Run emulator commands sequentially. The disposition-check front end includes
the deliberate-parent-failure check that was executed separately in this run.
