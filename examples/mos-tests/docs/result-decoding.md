# Result decoding and report contract

The v1 host decoder is implemented in scripts/report_results.py. It shares human
and agent entry points and passed the independent TEST-01 W03/W05 fixtures.
It validates recorded claims and preservation masks; it does not independently
re-execute every test-specific assertion or infer unspecified return semantics.
[Human usage](../human/reports.md) owns commands and report options.

## Validation stages

1. Strict manifest keys/version, duplicate JSON rejection, lowercase identities,
   cross-file SHA-256 links, target/backend declarations and bundle artifact
   size/hash checks. Paths remain below the run root, including symlink resolution.
   Fixture/expectation hashes must identify artifacts actually present. Script
   bytes and selector expansion must agree with the saved ordered plan.
2. Bounded v1 headers, payloads, schema, reserved fields, CRC and commit marker;
   all six typed payload shapes, disposition count rules and UTF-8 reasons.
   Parsing stops at the first invalid record unless forensic mode is requested.
3. Run identity, serial sequence, duplicate equality, run/case boundaries and
   catalogue order. Case hashes and sample counts agree with the catalogue;
   observation sample IDs, chunk identity/completeness and logical counts agree
   with case-end claims. UTF-8 diagnostic observations validate after assembly.
4. Register-pair width, reserved fields, validity bits and preservation-mask rules.
   Unavailable masked fields or masked differences in a claimed pass make the
   evidence incomplete. Raw entry/exit/mask bytes remain in decoded evidence.
   Test-specific output assertions remain the identified runner's claims; the
   decoder does not invent function-specific prose or change expectations.
5. RUN_END totals must reconcile with the selected cases' valid completions.
   Error/incomplete results, sequence gaps, missing observations or endings,
   invalid identities and supplied recovery faults prohibit all-pass. Identical
   card/RAM records merge once, while conflicting copies remain corruption.
6. SRAM control selection checks CRC/commit, bounds, run and manifest identity,
   highest generation and equal-generation conflicts. Staging is read only within
   a valid declared extent. The emergency record can be decoded independently of
   control slots. Stopped/non-ended state and inconsistent confirmed progress are
   explicit problems; arbitrary fault recovery is not established by this parser.

## Reports and evidence limits

Summary precedes details and counts unique failing tests. A known failure remains
listed when later missing evidence makes the overall verdict incomplete. Human
failure text uses the recorded operation/effect/return reason, with assertion
counts and captured observations beneath it. The decoder makes no additional
claim about API effects beyond its evidence. Passed case detail is retained in
JSON evidence but omitted from the initial human summary. Colour is supplementary.

All-pass means complete selected coverage in the validated supplied evidence.
It is not cryptographic attestation of firmware execution, independent proof of
all target assertions, or proof that unsupplied SRAM contained no error. Target
identity/provenance is declared in the hashed target manifest. No emulator pass
establishes hardware behavior. The human guide makes file-only and recovery
limits explicit. The current W04 sample's placeholder manifests are not accepted
as an authenticated full-suite run; startup/bundle integration remains W06.

## Qualification

[W05 evidence](tasks/MAIN-03/W05/validation.md) records 58 scenarios, including
all 14 pre-agreed report oracles, plus rejection of 690 truncated records and 690
single-bit corruptions across six frozen types. Literal fixture construction is
independent of the production C++ encoder and Python parser. Additional controls
cover max/zero/oversize payloads, CRC-correct malformed records, unknown keys/run
IDs, missing/reordered/conflicting/duplicate records, chunk/UTF-8 handling,
preservation-mask contradictions, manifest/artifact/script corruption, traversal,
symlink escape, SRAM generation/commit faults, independently recovered emergency
records, CLI exit codes, output refusal and terminal controls. No emulator or
hardware execution was needed for this host-only component qualification.
