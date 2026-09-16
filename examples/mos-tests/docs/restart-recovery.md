# Restart recovery contract v1 — MAIN-05 W01

## Summary

A boot must inspect durable recovery state before allocating or executing a run.
Unresolved or ambiguous evidence stops automatic execution. Explicit disposition
can park a run or authorize one new linked retry/continuation. This is a planned
contract. W02 now implements the restricted synthetic-profile gate; W03
dispositions remain planned. No physical power-loss guarantee is made.

The result wire format remains [v1](result-format-v1.md). This document adds an
SD journal and disposition sidecars; it does not change record meanings. MAIN-05
W02 implements the gate; W03 adds user actions; W04 qualifies interrupted boots.

## 1. Installation and inspection

1. Keep /mos-tests/install.bin and immutable run directories. Add two fixed-size
   files /mos-tests/recovery-a.bin and recovery-b.bin. Provision both journal
   slots before first deployment with IDLE generations 1 and 2, the installation
   namespace, counter zero and all other fields zero. They are mutable installation
   state, excluded from immutable bundle artifact hashes, like install.bin.
2. Every begin command inspects before counter allocation, mkdir or clearing SRAM.
   A function/finalize invocation must also match the journal's run/plan/phase to
   its valid same-boot session; it cannot bypass a rejected begin. A cold boot with
   ACTIVE state never silently restores that session from card.
3. Validate both slots, install.bin CRC/namespace/counter, and bounded directory
   reconciliation. An empty installation requires valid provisioned IDLE slots,
   counter zero, and an empty runs directory. A missing directory, journal or
   allocation file is not evidence of a new installation.
4. Existing pre-recovery bundles require explicit migration on a copied image,
   with full retained-run inspection and recorded baseline. Missing journal never
   silently enables legacy startup. W02 may reject legacy state and document it;
   an automatic migration utility is outside this first implementation.
5. Directory reconciliation recognizes only 32 lowercase hexadecimal run IDs in
   the installation namespace, contiguous counters 1 through install.counter.
   Every counted run must exist and have valid identity-linked artifacts. Gaps,
   foreign/unknown entries, counter rollback, unreadable storage or unexplained
   artifacts block startup. Previous runs require validated completion or an
   immutable accepted disposition; an acknowledged incomplete run stays incomplete.
6. Initial bounds: 4,096 run directories, 4,096 disposition receipts total,
   1 MiB results per run, 64 MiB total record bytes per inspection, 16 KiB per
   JSON manifest/receipt and 8 KiB script. Stream record checks with at most one
   1,069-byte envelope buffer; do not load the history into target RAM.
   Hitting a bound is BLOCKED, never an invitation to ignore remaining evidence.
   Future expansion requires a contract revision; no claim of unlimited history.
7. Gate classification is separate from test verdict. COMPLETE authorizes ordinary
   next-boot startup only after evidence reconciliation; it does not mean all
   tests passed (a completed run may contain failures or unsupported tests).
   PARKED, unfinished phases, corruption and inspection limits stop autoexec
   with nonzero status. Report confirmed failures and the last trustworthy phase.

## 2. Journal encoding

Both slots are exactly 256 bytes, explicitly serialized little endian, no C++
struct dumps. Integers have the specified wire widths even with 24-bit target int.
CRC is CRC-32/ISO-HDLC as in result v1.

| Offset | Bytes | Field |
| --- | --- | --- |
| 0 | 4 | ASCII MSTJ (distinct from record MSTR) |
| 4 | 2 | Schema 1 |
| 6 | 2 | Size 256 |
| 8 | 8 | Installation namespace |
| 16 | 8 | Positive generation; no wrap |
| 24 | 16 | Current/subject run ID; zero only IDLE |
| 40 | 16 | Parent run ID; zero for ordinary runs |
| 56 | 32 | Plan SHA-256; zero until prepared |
| 88 | 32 | Selection-script SHA-256; zero only IDLE |
| 120 | 1 | Phase, below |
| 121 | 1 | Disposition action: 0 none, 1 park, 2 retry, 3 continue |
| 122 | 2 | Reserved zero |
| 124 | 4 | Case key, zero when no identified case |
| 128 | 4 | Last confirmed record sequence; zero before records |
| 132 | 8 | Last confirmed result byte length |
| 140 | 8 | Reserved/allocated run counter |
| 148 | 32 | Disposition receipt SHA-256, or zero |
| 180 | 68 | Reserved zero |
| 248 | 4 | CRC over bytes 0..247 |
| 252 | 1 | Commit A5 |
| 253 | 3 | Reserved zero |

Phases: 0 IDLE, 1 ALLOCATING, 2 BETWEEN, 3 CASE_INTENT, 4 IN_CASE,
5 CASE_DONE, 6 FINALIZING, 7 COMPLETE, 8 DISPOSING, 9 PARKED, 10 ARMED.
Unknown phases/actions/versions and nonzero reserved bytes block startup.

Normal transition edges are IDLE/COMPLETE -> ALLOCATING -> BETWEEN ->
CASE_INTENT -> IN_CASE -> CASE_DONE -> BETWEEN (repeat), then BETWEEN ->
FINALIZING -> COMPLETE. Disposition edges are an unresolved identified state or
PARKED -> DISPOSING -> PARKED/ARMED, and ARMED -> ALLOCATING. DISPOSING may
transition to a new DISPOSING generation only following another explicit action.
Provisioned IDLE -> IDLE is allowed; identical same-state snapshots are otherwise
not a substitute for a required transition. A damaged pair cannot be repaired
implicitly by the publication routine; explicit offline reconciliation is required.
Current run/plan/counter may change only at the defined allocation/arming edges;
phase-progress sequence and byte counts never decrease within the same run.

Require two valid slots with adjacent generations and legal successive states,
or byte-identical equal-generation copies. Equal-generation conflicting copies
block. A single surviving valid slot is diagnostic evidence only: it cannot
authorize execution. Never use an older COMPLETE slot to excuse an invalid
newer slot. The higher generation selects the candidate state; retained-run
reconciliation is mandatory even when both slots validate. Exhaustion blocks.

Publish to the older slot: invalidate its commit byte and sync; write the complete
new payload/CRC with commit zero and sync; write A5 and sync; close successfully;
reopen and verify exact bytes and successful close. Only then perform the action
that depends on publication. Check all byte counts/statuses. On any error, stop;
do not recursively attempt publication or assume the older slot clears the error.
No sector, FAT metadata, flush or directory update is assumed power-loss atomic.

## 3. Execution ordering and restart windows

1. After a clean gate, compute next run ID without modifying install.bin.
   Publish ALLOCATING with that ID, next counter and actual script hash first.
   Then persist the allocation counter, create the exclusive run directory,
   prepare/hash artifacts, write/sync RUN_START, and close results.
   Publish BETWEEN with actual plan hash and confirmed length/sequence.
   A restart anywhere before BETWEEN is incomplete allocation/preparation.
2. Before each case, publish CASE_INTENT with the next case key while preserving
   previously confirmed record progress. Then write/sync CASE_START. Publish
   IN_CASE with its confirmed sequence/length before any test payload.
   Establish register preconditions after journal/storage side effects.
   CASE_INTENT does not prove entry; IN_CASE does not prove the call executed.
3. Capture immediately around the call. Save/sync observations and CASE_END,
   then publish CASE_DONE. Complete fixture cleanup and close at group boundaries
   before BETWEEN. A CASE_END may prove its test outcome while the run is still
   interrupted during cleanup; retain that outcome without claiming run completion.
   Unsupported/skipped terminal records follow the same durable boundaries.
4. Publish FINALIZING before RUN_END. Write/sync RUN_END, successfully close
   results, then publish COMPLETE with the final sequence and byte length.
   Never publish COMPLETE from a finally block. Existing recorder.finish_run()
   already orders end/sync/close; the new COMPLETE publication belongs after
   its success. Complete file bytes plus FINALIZING still mean uncertain close.
5. Same-boot error exits leave a conservative unfinished phase. Subsequent boot
   stops, even if all expected record bytes happen to be visible.
   Observations may be newer than the journal's last confirmed progress; validate
   the prefix, retain those observations, and do not downgrade ambiguity to pass.
   A claimed confirmed extent beyond valid available bytes is corruption.
6. COMPLETE must match a validated RUN_END, plan, counts, length and identity with
   no tail. Prior complete runs are inspected using the same evidence rules.
   Firmware reset cause is unknown unless separately supported and recorded.

Reports distinguish “last started case has no completion” from “interrupted
between cases”, “allocation incomplete” and “finalization/close uncertain”.
No last-case guess when record/journal identity is damaged. Recovery preserves
bytes; it never appends speculative records to the original stream.

## 4. Explicit disposition and one-use authorization

Read-only recovery inspection is repeatable and cannot allocate, acknowledge or
rerun anything. Human and agent actions share one implementation. An explicit
action supplies subject run ID, expected journal generation, action, selected
case IDs, exact selection script hash and a fresh-prerequisites acknowledgement.

Publish DISPOSING before creating an exclusive immutable receipt at
/mos-tests/recovery/<generation-as-16-lowercase-hex>.json. JSON is UTF-8, schema 1,
duplicate keys forbidden, maximum 16 KiB. Required fields are schema,
installation_namespace (16 hex), subject_run_id (32 hex), journal_generation
(positive decimal string, uint64), action (park/retry/continue),
case_ids (ordered unique strings), selection_script_sha256 (64 hex or null for
park), evidence_sha256 (mapping safe relative artifact paths to exact SHA-256),
reason (nonempty UTF-8), actor (nonempty human/agent provenance label),
prerequisites_confirmed (boolean). Reject unknown fields and unsafe paths.
Hash the original evidence available at inspection, including journal snapshots
saved as sidecars; record unreadable/missing evidence explicitly in the reason,
never manufacture a hash. Identity-ambiguous cases cannot be re-armed.

Write/sync/close/read back the receipt, then publish PARKED for park or ARMED for
retry/continue with its digest. Only these terminal publications accept a receipt;
an orphan/partial receipt or DISPOSING blocks and requires explicit reconciliation.
Receipts are never edited or deleted; another attempt uses a new generation/name.
No receipt rewrites the interrupted run's verdict or erases confirmed failures.

PARKED stays stopped across boots: acknowledging an interruption is not permission
to rerun the unchanged autoexec script. Explicit retry/continue publishes a fresh
receipt and ARMED state. Retry selects explicit cases, possibly the interrupted
one; continuation selects an explicit remainder. No implicit “everything left”.
Both require fresh fixture prerequisites and matching deployed selection bytes.

ARMED is a one-use authorization. Before allocating a child, publish ALLOCATING
for the new child ID with subject as parent and receipt hash preserved; then
allocate/write files. If this transition fails or is interrupted, do not reuse
the authorization automatically. New run.json carries parent_run_id and a hashed
disposition sidecar referenced by bundle/run artifacts under existing identity
validation rules; freeze any necessary manifest extension before W03 implementation.
The child has a new plan and does not count omitted parent cases as passes.
Recovery from an interrupted disposition requires a new explicit action, never
automatic replay. Normal successful completion may resume ordinary boot policy.

## 5. Integration and qualification boundaries

C++/AgonDev owns on-device inspection and publication; narrow existing MOS storage
adapters retain returned status and byte counts. Reuse record/manifest validation
semantics; factor shared primitives rather than inventing weaker pass criteria.
The on-device first implementation may conservatively block unsupported valid
formats that the host can decode, but must clearly identify that limitation.

W02 delivers publication/read-only gate with no re-arm CLI. W03 delivers receipts,
explicit dispositions and parent-linked execution. W04 runs the independent
transition expectations retained in MAIN-05/W01, with raw SD images and repeated
process launches. Kill/restart trials are controlled interruptions, not proven
hardware resets or physical card power loss.

Before-reset Fab SRAM/register/trace capture remains complementary. Restart uses
SD only and never assumes SRAM survives. Hardware, arbitrary crash recovery,
storage atomicity and a trusted reset-reason source remain unqualified.

## W02 implementation status

See human/recovery.md and docs/tasks/MAIN-05/W02/validation.md. The gate and
journal publication are implemented; dispositions are unavailable. W02 requires
canonical same-bundle artifacts for the three synthetic controls and uses the
existing wire primitives with stricter streaming validation. It may reject valid
but unsupported host-decodable evidence. Additional operational bounds are 1 MiB
per hashed artifact and 64 MiB aggregate hashed bytes per inspection. W03 must
freeze any receipt/manifest integration changes before implementing dispositions.

## W03 integration extension

The frozen [W03 contract](tasks/MAIN-05/W03/contract.md) adds durable acceptance
certificates and child run schema2, preventing orphan receipts from becoming
authorizations after the journal advances. It specifies the shared request
interface, selected continuation and explicit interrupted-disposition retry.
