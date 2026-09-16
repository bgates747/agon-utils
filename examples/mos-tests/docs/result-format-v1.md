# Result format v1 and runner data contracts

## Status and scope

Frozen baseline for MAIN-03 W01 / TEST-01 W01. This specifies the first encoder,
decoder and runner; it is not evidence that they exist or work. Change incompatible
layouts by increasing the relevant version and retaining old fixture meaning.
The [strategy](test-strategy.md) owns workflow/presentation; this document owns
exact bytes, identities and state semantics. No compiler structs go on disk.

## Scalar and identity rules

All integers are unsigned little-endian unless explicitly stated. u8/u16/u24/u32
mean exactly 1/2/3/4 bytes, regardless of target C++ sizeof(int). No implicit
padding. Text is UTF-8 without trailing NUL; reject invalid encoding. Hashes are
32 raw SHA-256 bytes, not hex text. JSON manifests use lowercase hexadecimal
hashes and IDs; hash the exact UTF-8 file bytes (including final newline), not a
re-serialized object. Producers emit LF; consumers retain original bytes.

The 16-byte opaque run ID is nonzero. Allocate a new directory exclusively; never
reuse or overwrite a run. A host may supply a random ID. On-device allocation
uses an explicit 8-byte installation namespace plus a monotonically allocated
u64 counter encoded LE, with collision checking and allocation persisted before
execution. If allocation cannot be trusted, stop; no clock-derived uniqueness
claim. Counter/sequence/generation overflow stops before wrap. Resuming creates
a new run with parent identity; it never extends an uncertain file tail.

## Manifests

JSON objects reject duplicate keys. The baseline schemas are version 1; the W03 child-run extension below adds
run.json schema2. Required fields
below cannot be omitted. Integers must fit their specified widths. Unknown fields
are rejected in v1 to expose typos. Relative artifact paths use slash separators,
remain below the bundle/run root, and exclude traversal or symlink escape.
These JSON files are authoritative host-visible artifacts; the Agon runner may
use a generated compact table carrying their hashes, not a second divergent
catalogue. The image builder verifies compact table and manifests agree.

| File | Required fields |
| --- | --- |
| catalogue.json | schema, cases (ordered array) |
| each case | key (nonzero u32), id (stable ASCII string), function, route, group, expectation_sha256, fixture_sha256, capabilities (string array), isolation, samples (ordered distinct u16 IDs), timeout_ms (positive u32) |
| plan.json | schema, catalogue_sha256, selectors (string array), case_keys (ordered distinct keys), backend, capabilities (string array), script_sha256 |
| target.json | schema, backend, declared_by, mos_binary_sha256, mos_map_sha256, toolchain_manifest_sha256, emulator_binary_sha256, vdp_binary_sha256 |
| bundle.json | schema, catalogue_sha256, artifacts (ordered array of objects with path, size (u32), sha256) |
| run.json | schema, run_id, parent_run_id, bundle_sha256, catalogue_sha256, plan_sha256, target_sha256 |

Nullable fields: parent_run_id; emulator_binary_sha256 on hardware; vdp_binary_sha256
and mos_map_sha256 only when unavailable on hardware. Unavailable is not an all-zero
hash or a claim of identity verification. Backend is emulator or hardware;
declared_by identifies the operator/profile or verified host mechanism. Catalogue
route is rst08, c-function, rst, or synthetic; isolation is pure, stateful, media,
exclusive, or control. Capabilities are exact catalogue-owned strings. IDs use
[A-Za-z0-9._-]+; no wildcard ID identities. Function selectors are expanded by the
bundle planner; the runner accepts only keys in the persisted plan.

Unknown selectors, duplicate IDs/keys, unknown case keys and an empty plan are
configuration errors before execution. Hashes tie cases to their exact fixture
and expectation files; those files must ship in the bundle, not merely be named.
Keep grouping and numeric lookup distinct from stable case identity.

### Editable script and selected-plan agreement

Before executing any test, a begin operation scans the human-edited autoexec.txt
using the documented generated subset: full-line # comments, LOAD of the runner,
RUN . for begin/function-group/finalize, blank lines and specified boot setup.
The implementation must validate group pairing and reject unsupported syntax
rather than pretending to interpret arbitrary MOS scripts. From active group
commands derive the ordered union of case keys and persist plan.json (no duplicates).
The begin/finalize commands are fixed scaffolding, not optional group lines.
This scan is a prerequisite for reporting only the human-selected cases while
still detecting a group that failed to execute. Missing begin means no trusted
run; missing finalize means incomplete. A script hash mismatch between invocations
stops the run. Agents use the same planner/selection semantics.

## Record envelope

Keep the strategy's MSTR envelope. Offsets are decimal; total length is 45+P.

| Offset | Width | Field |
| --- | --- | --- |
| 0 | 4 | ASCII MSTR |
| 4 | 1 | major=1 |
| 5 | 1 | type, 1–6 |
| 6 | 2 | header size=40 |
| 8 | 16 | run ID |
| 24 | 4 | sequence, starts at 1 |
| 28 | 4 | case key, zero for run-level records |
| 32 | 4 | payload size P, 2–1024 |
| 36 | 4 | reserved zero |
| 40 | P | typed payload |
| 40+P | 4 | CRC32 over header and payload |
| 44+P | 1 | A5 commit byte, written last |

CRC-32/ISO-HDLC: reflected polynomial EDB88320, initial and final xor FFFFFFFF;
ASCII 123456789 -> CBF43926. No record padding. Zero payload is malformed for v1
because every type requires a schema word. The earlier design's generic 0–1024
range is narrowed here to 2–1024; type-specific lengths are stricter below.
Commit validity is not filesystem durability or atomicity. Before reusing RAM,
clear its old commit location, write bytes/CRC and publish A5 last.

## Typed payloads

Offsets below are relative to payload start. All schema words are u16=1.
Reserved fields are zero and exact payload length must agree with type fields.

| Type | Layout and total length |
| --- | --- |
| 1 RUN_START | schema@0; backend u8@2 (1 emulator,2 hardware); reserved u8@3; selected_count u32@4; bundle hash@8; catalogue hash@40; plan hash@72; target hash@104. P=136; case key=0 |
| 2 CASE_START | schema@0; sample_count u16@2 (>0); fixture hash@4; expectation hash@36. P=68; case key must be selected |
| 3 OBSERVATION | schema@0; kind u8@2; flags u8@3=0; sample_id u16@4; chunk_index u16@6; chunk_count u16@8 (>0); data_length u16@10; observation_id u32@12 (>0); data@16. P=16+data_length, max data1008 |
| 4 CASE_END | schema@0; disposition u8@2; reserved u8@3; assertions u32@4; failed_assertions u32@8; observation_count u32@12; reason_length u16@16; reserved u16@18; reason text@20. P=20+reason_length |
| 5 CHECKPOINT_ERROR | schema@0; operation u8@2 (1 write,2 sync,3 close,4 staging-full,5 allocation); reserved u8@3; status u32@4; attempted_sequence u32@8; confirmed_sequence u32@12. P=16; case key current or0 |
| 6 RUN_END | schema@0; reserved u16@2; eight u32 case counts@4 in disposition order1–8; plan hash@36. P=68; case key=0 |

OBSERVATION kinds: 1 register-pair (fixed96 data bytes, exactly one chunk),
2 bytes (chunkable), 3 diagnostic UTF-8 (chunkable; validate after concatenation).
Observation IDs are unique per case/sample. Chunk indices start0; identical
ID/kind/sample/chunk_count across chunks; each index appears once unless merging
byte-identical duplicate whole records. observation_count counts logical IDs,
not chunks. All required chunks/samples must be present before claiming pass.
Large content uses chunks, not unversioned sidecar layout in initial v1.

Disposition codes: 1 PASSED, 2 FAILED, 3 OBSERVED, 4 SKIPPED, 5 UNSUPPORTED,
6 BLOCKED, 7 ERROR, 8 INCOMPLETE. Reasons mandatory for 2–8. PASSED requires
assertions>0 and failed_assertions=0; FAILED requires 0<failed_assertions<=assertions.
OBSERVED has both counts0 and is not a conformance pass. Skipped/unsupported/
blocked have both counts0 and no observations. ERROR/INCOMPLETE may retain valid
partial observations; their failed_assertions cannot exceed assertions.

A selected key has one CASE_START and one CASE_END in a normal stream, including
skips (sample_count still matches catalogue). Samples do not inflate case counts.
Cases execute serially: finish the current case before starting the next. A
checkpoint failure terminates ordinary execution. Recovery error records may
exist only in RAM; identify their retrieval provenance outside the wire bytes.
Normal sequencing begins RUN_START and ends RUN_END, with no records after it.

RUN_END counts are claims to verify, never trusted totals. Match them to selected
keys and case-end records. A missing case/end/chunk/sample, hash mismatch, ERROR
or INCOMPLETE prevents all-pass. OBSERVED/skip/unsupported/blocked prevent the
ALL TESTS PASSED headline even if the run is structurally complete. Missing run-end
is incomplete. Identical run/sequence duplicates from file and RAM merge once;
conflicting duplicates are corruption. Sequence gaps require an incomplete verdict.

## Register pair and preservation mask

Register-pair data consists of entry snapshot32, exit snapshot32, mask32. Mask
bytes select promised preserved bits only, not expected output values. Expected
outputs are independently defined in the hashed expectation fixture. Invalid
snapshot fields cannot satisfy a nonzero preservation mask: mark ERROR/capture
failure. Unmasked changes can be recorded without declaring contract failures.

| Snapshot offset | Width | Field / valid bit |
| --- | --- | --- |
| 0 | 2 | F then A / bit0 |
| 2 | 3 | BC / bit1 |
| 5 | 3 | DE / bit2 |
| 8 | 3 | HL / bit3 |
| 11 | 3 | IX / bit4 |
| 14 | 3 | IY / bit5 |
| 17 | 3 | normalized SP / bit6 |
| 20 | 3 | observation PC / bit7 |
| 23 | 1 | MB / bit8 |
| 24 | 1 | ADL (0/1) / bit9 |
| 25 | 1 | interrupt-state code (0 disabled,1 enabled) / bit10 |
| 26 | 2 | validity bitmap, bits11–15 zero |
| 28 | 4 | reserved zero |

Invalid fields are encoded zero; zero validity means unavailable, not a measured
zero. Mask positions26–31 must be zero; PC masks zero in v1 (entry and exit are
different observation points). Mask bits for ADL/IFF outside bit0 must be zero.
AF may mask A and/or individual F bits separately. No alternate registers are
claimed. PC is the labelled call-boundary observation point, not the callee's
internal PC; keep raw probe stack/addresses in diagnostic byte observations if
needed. Normalized SP compares the same caller boundary before the call and
after its return; the probe's reviewed accounting must not hide callee imbalance.
IFF/ADL snapshots are valid only when the capture mechanism independently proves
them; do not infer interrupt state from a later flag-changing sequence.

## SRAM control layout

Retain the strategy's nonoverlapping 8192-byte allocation. Control area contains
two 128-byte slots at offsets0 and128; no separate authoritative active hint.
A slot is usable only if marker, version, reserved fields, bounds and CRC validate.

| Offset within slot | Width | Field |
| --- | --- | --- |
| 0 | 4 | ASCII MSTC |
| 4 | 2 | schema1 |
| 6 | 2 | size128 |
| 8 | 16 | run ID |
| 24 | 4 | generation >=1 |
| 28 | 4 | next sequence >=1 |
| 32 | 4 | last confirmed SD sequence,0 means none |
| 36 | 2 | staging used bytes,0–2048 |
| 38 | 1 | state:1 ready,2 in-case,3 captured,4 I/O,5 stopped,6 ended |
| 39 | 1 | reserved0 |
| 40 | 4 | current case key or0 |
| 44 | 32 | catalogue hash |
| 76 | 32 | plan hash |
| 108 | 12 | reserved0 |
| 120 | 4 | CRC over bytes0–119 |
| 124 | 1 | commit A5 |
| 125 | 3 | reserved0 |

Select highest valid generation for the same run; equal generations with different
bytes are corruption. Foreign-run slots are not merged. Update inactive slot
by invalidating commit first, writing fields/CRC, then commit. A stale slot only
bounds a known prefix; recover committed staging records by bounded scan as
needed. Do not reuse staging bytes still needed by a valid unconfirmed slot.
After write+sync confirmation, publish confirmed progress and an empty staging
extent before reusing its storage. Old file/RAM duplicates are expected and merge
by run/sequence. Fault injection must qualify every transition before claiming
crash recovery. No software sequence guarantees survival of arbitrary wild writes.

Emergency area at SRAM offset0D00 starts with one CHECKPOINT_ERROR record
(61 bytes); remainder zero. Independent envelope validation allows reading it
without trusting the control slots. Invalidate its commit before reuse. Never
recursively checkpoint an error through the failing SD path. Reset wiping is
permitted and destroys this evidence; no persistence across reset is promised.

## Oracles and validation boundary

[Golden fixtures](../fixtures/format-v1/README.md) define independent wire bytes,
snapshot mutations and report plans. Their builder is test tooling, not a
production serializer. Two differently structured CRC computations check fixed
bytes. Fixture assertions check manual lengths/offsets; future encoders/decoders
must match frozen files without regenerating expectations during their own test.
W01 establishes these contracts and controls only. TEST-01 W02–W06 still own
actual capture, decoder, checkpoint and startup qualification.


## MAIN-05 W03 child-run manifest extension

The frozen [integration contract](tasks/MAIN-05/W03/contract.md) adds run.json
schema2 for an explicitly authorized retry/continuation. All schema1 fields
remain required; parent_run_id is non-null and disposition_sha256 is added.
Ordinary runs remain schema1. Binary record envelopes remain version1.

Copy the accepted receipt as disposition.json and add its exact bytes/size/hash
to the child bundle.json artifact list. RUN_START therefore binds the receipt
through its bundle digest. The receipt subject equals parent_run_id, shares the
installation namespace, and has a smaller counter. Its ordered cases and script
digest equal the child plan; retry/continue and confirmed prerequisites are
required. Actor, reason, generation and parent/snapshot evidence commitments
remain attached.

A child-only host report validates these relationships but does not independently
re-read parent/card evidence or the acceptance certificate. The target startup
gate performs that reconciliation on the original installation. Report parent
identity prominently and keep parent outcomes separate from child counts.
