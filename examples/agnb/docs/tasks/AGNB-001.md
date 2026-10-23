# AGNB-001 — Generic plain buffers and incremental loading

Allow arbitrary buffer data and executable buffered-command bytes to be loaded
from one AGNB file through bounded eZ80 memory. Explicit IDs stay in the file;
the loader never allocates/remaps them or executes loaded commands. This is a
generic AGNB capability, independent of compilers or particular applications.

The Author assigned ownership, documentation and scoped commit/push duties to
the Golem agent on2026-10-23. Preserve unrelated agon-utils changes. All new task
fixtures/scripts/evidence belong under docs/tasks/AGNB-001/ until promoted.

## Format and host tools

- FMT-001 [x] Define provisional0.3 plain records: existing RIFF/AGNB envelope and VERS, LIST BUFR with BHDR/RAWD/DATA in order. RAWD is one byte0, meaning plain data consolidated into one VDP block. No auto-call, bitmap/sample finalization, resource allocation or application metadata.
- WRT-001 [x] Publish a dependency-free writer/reader for explicit-ID nonempty plain buffers, sharing the existing proven alignment/chunk code. Provide a JSON-manifest CLI whose source paths are build inputs, not runtime names.
- TST-001 [x] Test exact framing, alignment, IDs, truncation/oversize/order/version rejection, multi-window and large aggregate containers; preserve existing image/audio output compatibility.

## Runtime loader

- LDR-001 [x] Add agnb_load_buffers and callback variant to the canonical eZ80 API using its existing FIL/state/8KiB window/stream/consolidate helpers. Preserve image/audio behavior and entry signatures.
- QUA-001 [ ] Assemble real consumers and qualify stock MOS/VDP success/failure/consecutive-load paths, payloads spanning transfer windows and aggregate data larger than eZ80 application RAM. Separate file/host validation from target claims and respect human emulator publication gates.
- DOC-001 [ ] Document buffer/block semantics, limits, callback/error/partial-load behavior and ownership. Keep format/API docs current and append dated results.
- PUB-001 [ ] Commit/push only owned and qualified changes in logical groups; retain any emulator-coupled work uncommitted until applicable Author validation/approval.

## Boundaries

1. Use the existing four-byte RIFF payload padding convention, explicit u16 IDs0..65534, and u32 chunk sizes. The bounded runtime currently accepts DATA lengths1..0xFFFFFF; VDP memory availability is a separate limit. Version0.1 image and0.2 audio remain unchanged and reject the new version.
2. RAWD0 always consolidates transfer blocks into one logical VDP block. Preserving multiple logical blocks is a future descriptor extension, not inferred from the transfer-window size. No new checksum/readback, rollback or runtime ID allocator.
3. The host writer rejects duplicate IDs in one package. The current runtime parser does not retain a global ID set; record order is explicit replacement order if a hand-authored file repeats IDs. This distinction must be documented rather than adding a costly hidden runtime table.
4. Metadata and enclosing bounds validate before each DATA is uploaded. A failed later record may leave earlier records installed; caller must not invoke a package until loading succeeds. Cleanup policy remains the caller's.
5. Golem controls assigned IDs, symbols, entry/setup order, native loading/handle binding, package ownership and target selection under GOLEM-046. Generic AGNB accepts opaque bytes and does not interpret those compiler semantics.


First host tranche: compiled extension smoke,9 plain-buffer test methods,
4 existing image writer tests and1 image manifest test pass. Same-version
Pillow repair replaced stale x86_64 wheels with native aarch64 in the project
venv. A real assembled loader consumer also passes. Runtime implementation is
additive; actual target/human qualification remains QUA-001. Host-only format/
writer publication can be separated from pending runtime qualification.
