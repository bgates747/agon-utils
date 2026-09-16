# W01 contract review

W01 defines the recovery contract and 30 independent transition expectations.
No recovery implementation or emulator qualification is claimed.

1. Reviewed startup allocation/session/finalization in apps/startup-runner/src/main.cpp,
   durable case hooks in recorded_lifecycle.h, recorder end/sync/close ordering
   in recording.h and raw status/count handling in mos_storage.h.
2. Existing allocate() modifies install.bin before directory creation: the planned
   ALLOCATING publication must precede it. Existing execute() must remain after
   CASE_START and new IN_CASE publication, with register setup after storage I/O.
3. finish_run() returns success only after close, providing the planned COMPLETE
   hook. It cannot establish durable completion if the journal publication fails.
4. The 256-byte field table is contiguous through offset 255; CRC covers 248
   bytes, commit is byte 252, reserved tail is bytes 253..255.
5. idle-slot-b.bin is an independent literal-format fixture: namespace
   0102030405060708, generation 2, IDLE/counter zero. Python struct/zlib generated
   its declared LE fields and CRC; checked zlib against 123456789/CBF43926.
   This is an oracle for future encoder/decoder qualification, not a passing
   production test. expected-transitions.json supplies R01–R30 outcomes before
   implementation. These expectation IDs are retained, never renumbered.
6. Reviewed reset windows from pre-allocation through case entry/end, cleanup,
   close, disposition and authorization consumption. Ambiguous states block;
   parking does not trigger the unchanged crashing script on next boot.
7. Target manifest validation, raw-image persistence and interruption injection
   remain W02–W04 work. The contract permits conservative rejection of unsupported
   valid inputs, never unsupported acceptance. Physical hardware remains untested.
8. A trailing blank line in the accepted W07 replay script was reported by
   staged whitespace checking; removed as formatting only in this work item.
