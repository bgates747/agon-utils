# AGNB-002 — Bounded C++ plain-buffer reader

Provide an application-neutral C++ reader for the accepted plain-buffer format,
so AgonDev applications can stream containers without embedding an assembly
parser or a whole file. Generic format and transport stay here; compiler names,
setup/native activation and application UI remain consumer-owned.

The Author released the Golem C++ loader tranche on2026-10-23, under the existing
explicit assignment of generic AGNB ownership. Preserve unrelated utility work.

- API-001 [x] Implement a freestanding bounded0.3 reader with caller-owned8KiB workspace, exact framing/order/padding/bounds, explicit IDs and completed-record callbacks. Preserve writer and assembly APIs/bytes.
- IO-001 [x] Provide ordinary stdio/file and AgonDev MOS transport adapters. Propagate read/send/close failures; do not execute records, allocate IDs, infer assets or add production readback/rollback.
- TST-001 [x] Test writer-produced data, multi-window/large/repeated-ID loading, malformed metadata/order/bounds/padding/truncation and injected read/send errors; preserve completed callbacks and earlier installed records on late failure.
- QUA-001 [x] Cross-compile and execute a real AgonDev consumer on stock VDP and applicable actual-Xtensa firmware via the Golem-owned fixture. Record memory/large-file boundaries and clear qualification scope.
- DOC-001 [x] Document the public API, memory/lifetime/error/partial-load contract and exact consumer evidence. Keep Golem concepts out of generic production headers.
- PUB-001 [x] Human review accepted; the Author explicitly authorized scoped commit/push on2026-10-23. Publish on codex/agnb-plain-buffers, preserving unrelated changes and divergent history.

No wire-format revision, native SDK/firmware change or implicit source execution
is required. stdio's signed-long file-position limit is documented rather than
silently truncating large files. Caller serializes transport and owns completion.


### Implementation and qualification — 2026-10-23

The generic headers are implemented without format/assembly API changes. Twenty
sanitized C++ host checks pass, including exact decoded output for515,648payload
bytes,8KiB reads, callbacks/duplicates/late errors and injected I/O failures.
The compiled extension smoke, nine existing plain-buffer, four image-container
and one image-manifest tests pass unchanged.

A real AgonDev C++ consumer loads553,664-byte stock and545,168-byte native
containers using the same source and explicit layouts as the accepted assembly
consumer. Stock runs pass on Pi/Oryx; native JIT/interpreter pass on Oryx with
actual runtime results, fresh handles/unload, MOS return, image samples and zero
execution faults. Missing/bad/truncated/late failures and subsequent success
also pass. Consumer evidence is retained under Golem GOLEM-046/cpp; its separate
profile is staged/stopped for human review. No physical target or performance
acceptance is claimed. Human acceptance/publication remains PUB-001.


### Human review accepted — 2026-10-23

The Author reports "works." for the separate AgonDev C++ consumer review.
Agent retrieval verifies all95 saved result bytes and the application log's
final PASS, pinned runtime/fixture inputs, no failure output and a stopped
emulator. `AGNB-002/human-review.json` retains the receipt; the source consumer
receipt is Golem `docs/tasks/GOLEM-046/cpp/human-review.json`.
PUB-001's human-review portion passes; explicit publication approval and scoped
publication remain. No implementation changes or further emulator runs were
needed, and no unrelated utility work was touched.
