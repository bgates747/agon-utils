# Recording qualification

Use the shared human/mos-tests recording-check command; see
[recording guidance](../../docs/binary-recording.md). check.cpp builds the same
C++ recording and lifecycle code natively, compares frozen fixture bytes without
regenerating them, injects storage faults and interrupts individual SRAM stores.
Its independent CRC is deliberately structured differently from the encoder.
verify.py uses Python zlib and explicit wire fields for qualification readback;
it is not the production decoder. apps/recording-controls exercises actual MOS
writes/syncs/close with capture on a raw image and rejects existing output.
Golden fixtures remain under fixtures/format-v1. Do not regenerate expectations
to make a recorder change pass. TEST-01 W03 remains open for W05 decoding,
identity/order/corruption reconciliation and labelled recovery interpretation.
