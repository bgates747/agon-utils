# Binary recording and SD checkpoints

The shared C++ recorder matches the frozen v1 byte fixtures and passed injected
storage/publication faults. A headless raw-SD run captured two synthetic cases,
recovered all eight records from the card, and refused to overwrite the prior
result on reboot. This qualifies the recording component; full-suite selection,
authenticated manifests and human report decoding are subsequent work. Hardware
and power-loss durability are not established.

## Human and agent command

From /home/smith/Agon/mystuff/agon-utils/examples/mos-tests on Linux:

```sh
./human/mos-tests recording-check --output .emulator/runs/recording-review
```

The output directory must be new. This runs native fault controls with address
and undefined-behavior sanitizers, builds the AgonDev fixture, creates a raw image,
checks the real MOS write/sync/close path, retrieves SRAM, and reboots to check
collision refusal. It closes both emulator processes. Failed setup or execution
leaves incomplete.json; inspect result.json plus native.txt and wire-checks.json.
Source, artifacts and history remain on Linux. Shared code lives in
apps/runner/include/{recording,recorded_lifecycle,mos_storage}.h and
apps/runner/src/storage.asm. The human command invokes agents/check_recording.py
for debugger automation; it does not duplicate the engine.

## Recording contract

1. The caller supplies a nonzero, collision-safe run identity and an exclusively
   allocated output. The fixture host uses a fresh exclusive directory and random
   run ID, deploys run.id, and opens results.bin with FA_CREATE_NEW. General
   on-device allocation, persisted plan and startup selection remain W06 work.
2. Check the SRAM mapping before calling Recorder.begin. The recorder owns only
   the two control slots, staging extent and emergency area in the agreed layout.
   Capture retains its independent reserved region. begin initializes a new run;
   never use it to resume uncertain evidence.
3. Payload constructors serialize explicit little-endian fields, bounded lengths
   and UTF-8 reason text. Envelope records use CRC32 and a commit byte published
   last. Storage operations are outside capture windows. The low-level encoder
   accepts caller-built typed payloads; it is not an untrusted input decoder.
4. RecordedLifecycle syncs CASE_START before calling the executor. Establish
   register and other preconditions after that checkpoint. Immediately copy
   completed capture snapshots into an observation payload before further calls;
   observation() writes and syncs each single-chunk logical observation. It rejects
   multipart input in this initial bridge; low-level framing supports chunks.
5. CASE_END is synced before cleanup/advancement. Write errors, short writes,
   sync errors, close errors, staging exhaustion and sequence/generation limits
   stop ordinary progression. Short writes are not retried into an uncertain tail.
   A missing required record remains incomplete evidence.
6. Only a successful write AND sync advances confirmed_sequence. Both control
   slots release the confirmed staging extent before reuse, so a surviving old
   slot cannot retain a claim on overwritten unconfirmed data. Alternating slot
   updates invalidate their marker, write fields/CRC, and commit last.
7. Failure publishes one CHECKPOINT_ERROR directly to reserved SRAM, followed by
   stopped control state. It never recursively attempts to save the error through
   the failing filesystem. It retains the unconfirmed staging extent. A short
   write without a MOS status uses status FFFFFFFF; allocation status 2/3/4/5
   identifies sequence/generation/encoding/observation-count exhaustion or error.
8. RUN_END is synced before close; ended SRAM state is published only after close
   succeeds. A close failure may coexist with a wire-complete file. Retrieved
   emergency errors/stop state override a file-only completion claim; absence of
   recovered RAM is not evidence that close succeeded. The W05 report must state
   its evidence scope and reconcile all supplied sources. Do not infer physical
   durability from a sync return or a complete file.
9. Storage adapter recording_write retains both A (MOS FRESULT) and BC (bytes
   written). The AgonDev ffs_fwrite wrapper returns only the count. This narrow
   assembly wrapper avoids losing the immediate status; no firmware was changed.
   The remaining adapter calls use ffs_fsync/ffs_fclose. On fatal I/O, it makes no
   further write/sync/close attempt through that uncertain handle.

## Qualification and limitations

[W04 evidence](tasks/MAIN-03/W04/validation.md) includes exact binary, map,
compiler/runtime/source hashes, disassembly, native checks, debugger transcript,
SRAM, independent card readback and collision readback.

1. Six frozen records and the control-slot fixture agree byte for byte. Exact
   payload maximum, exact 2048-byte staging fill, over-capacity, zero run identity,
   post-end writes, disposition constraints and invalid UTF-8 are checked.
2. Twenty-two failure controls cover short/error writes and sync errors at every
   checkpoint in a two-case lifecycle, plus close failure, capacity and counter
   limits. They check no further execution/I/O, prior confirmed progress and
   independent emergency framing. They simulate faults at storage abstractions;
   they do not claim actual media fault or power-failure coverage.
3. Every byte-store interruption across tested append, control publication,
   confirmed release, staging reuse and emergency publication paths was checked:
   873 ordinary plus 191 emergency interruption points. At least one valid slot
   survives; committed emergency evidence has an independently correct CRC.
   Startup allocation interruption, arbitrary wild writes and reset persistence
   are not qualified by these bounded controls.
4. Independent qualification parsing rejects 684 truncated prefixes and 690
   single-bit record mutations. This is a narrow test oracle, not W05's production
   decoder. Manifest identities, reordered/conflicting records, forensic recovery
   and verdict reconciliation remain TEST-01 W03/W05 work.
5. Target fixture hashes are explicitly illustrative, not hashes of authenticated
   real-suite manifests. Two synthetic preserving cases and the collision check
   qualify the recording path, not MOS API conformance or full-suite startup.
6. Read-only references consulted: pinned agon-docs/docs/mos/API.md sections
   0x83 and 0x86, AgonDev include/agon/mos.h and src/lib/libmos/ffs_fwrite.src,
   ffs_fsync.src. Target MOS/runtime identities are in the evidence receipt.
