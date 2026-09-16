# MAIN-05 W03 — Disposition integration contract

## Summary

Implement explicit park/retry/continue using the same target C++ engine for
humans and agents. No automatic retry. Preserve subject evidence and consume an
authorization before allocating a new child. W02 is accepted; this contract is
frozen with that result checkpoint before W03 implementation.

## Interfaces and supported scope

1. Add target command RUN . recover, reading a bounded /mos-tests/request.json.
   Required fields: schema=1, subject_run_id, journal_generation (decimal string),
   action (park/retry/continue), case_ids (ordered unique IDs), script_sha256
   (null for park), actor, reason, prerequisites_confirmed. Reject duplicate,
   missing/unknown keys, stale generation/subject, unsupported selection and
   unconfirmed prerequisites for execution. Park selects no cases.
2. Retry accepts explicit selected cases from the subject plan; continuation
   accepts only explicit selected cases without a valid terminal CASE_END.
   An empty selection is rejected. The actual current autoexec script must match
   its requested hash and selected IDs. Original saved script is never edited.
3. The human front end prepares requests and selected scripts, and can execute
   the target recover command headlessly in a disposable recovery boot chain on
   an existing image. Restore the original !boot.obey afterward. A host crash may
   leave recovery boot installed, but stale expected generation prevents replay.
   Manual users copy prepared files and invoke RUN . recover on the target.
   Host preparation does not constitute target acceptance.
4. W03 initially supports identified runs with valid manifests and a readable
   valid record prefix, including missing finalization. Corrupt journal pairs,
   allocation gaps and identity-ambiguous artifacts remain blocked; no repair
   or legacy migration is inferred. Limit recovery history to 64 receipts in
   this synthetic profile, with bounded JSON and artifact reads.

## Durable acceptance and child provenance

1. Publish DISPOSING before creating receipt/snapshot files. Save both original
   journal slots as <generation>-a.bin and -b.bin; the immutable JSON receipt
   follows W01 fields and hashes all subject run files plus these snapshots.
   All receipt paths are relative to /mos-tests; no unsafe paths or silent omission.
2. Publish PARKED or ARMED after receipt sync/close/readback. Add a separate
   immutable 256-byte acceptance certificate <generation>.accepted after that
   publication, synced/closed/read back. This provides durable evidence of
   acceptance after the mutable journal moves to later runs. Missing/invalid
   certificate blocks automatic consumption, including an otherwise ARMED slot.
3. Certificate: bytes 0..3 MSTA; u16 schema1 at4, size256 at6; u64 receipt generation
   at8; receipt SHA256 at16; subject run ID at48; action at64; selected mask at65;
   reserved66..67 zero; selected script SHA256 at68 (zero for park); reserved
   100..247 zero; CRC32 over0..247 at248; A5 at252; reserved253..255 zero.
   Validate fields against the parsed JSON receipt and immutable evidence, not
   merely its CRC. Certificate is a publication witness, not an authentication
   signature or a claim of physical power-loss atomicity.
4. ARMED consumes once: publish child ALLOCATING before counter/directory changes,
   retaining receipt hash and setting parent run ID. Partial child allocation
   blocks; never re-use the prior ARMED slot. Park remains blocked across boots.
5. Child run.json uses schema2: schema1 fields plus disposition_sha256. Its
   parent_run_id must equal receipt subject. Copy disposition.json into the child
   and append that file to the per-run bundle artifact list, binding its bytes
   into RUN_START's bundle digest. Ordinary runs retain schema1. Decoder validates
   the child receipt/selection linkage; parent verdicts are never folded into the
   child's pass count. Original parent evidence remains separate.
6. Receipt selection and accepted-parent checks apply during future history
   reconciliation. Completed child runs can permit later ordinary runs; accepted
   incomplete parent runs retain their original incomplete/failure verdicts.
7. An interruption during acknowledgement stays stopped. An explicit new request
   at the current DISPOSING generation may retry disposition for the same subject:
   preserve orphan recovery files and include their hashes in the new receipt.
   A subsequently accepted receipt may account for those orphan bytes, but does
   not confer an accepted verdict on them or another run. Unknown unaccounted
   recovery files always block. Never overwrite a receipt or certificate.

## Validation

Exercise park/repeated-parked boot, explicit retry, selected continuation,
stale request replay, wrong generation/subject/script, prerequisite omission,
duplicate/unknown fields, altered receipt/certificate, consumed authorization,
and preserved parent bytes on raw images. Test schema1/schema2 host reports and
existing startup/gate regressions. Include interruption during disposition and a
fresh explicit retry of that disposition. W04 still owns exhaustive individual
write/sync/close boundaries. Save exact source/runtime identities and close all
owned emulators. Hardware remains unqualified.
