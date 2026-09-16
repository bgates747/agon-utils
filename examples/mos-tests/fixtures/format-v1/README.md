# Format v1 independent oracles

These fixtures predate the production encoder, decoder and capture harness.
They implement the [frozen contract](../../docs/result-format-v1.md) using literal
field bytes and explicit expected offsets, not production serialization calls.

1. Six .bin/.hex pairs exercise every record type. expected-wire.json records
   manually specified sizes/fields and computed checksums. Repeated 11/22/33/44
   hashes are recognizable placeholders, not real manifest hashes. The nominal
   stream is only wire-valid; a full decoder must reject missing identity artifacts.
2. CRC uses an independent bit-at-a-time implementation checked against Python
   zlib and the standard 123456789 answer. Hex output is manually inspectable.
3. control-slot.bin/.hex fixes the 128-byte SRAM slot layout; capture-controls.json
   defines 44 expected preserving/mutating snapshots across two seed patterns.
   These are byte-level oracles, not proof that target assembly capture works.
4. report-oracles.json defines explicit counts/verdicts for 14 complete, failed,
   limited and incomplete plan scenarios. These are decoder/report expectations,
   not reports from executed tests. TEST-01 W05 extends executable presentation checks.
5. build_oracles.py is a deliberate fixture-authoring tool. Never run it to
   regenerate expected files as part of the system-under-test check; compare
   production output against frozen files. Review contract and fixture changes
   together. No fully independent reviewer or physical execution is claimed.
6. bad-crc.bin and missing-commit.bin must not establish case completion. TEST-01
   W03 adds exhaustive corruption/truncation/inconsistency cases against the real
   decoder once implemented.

Run fixture-authoring consistency checks on Linux using the repository .venv.
All mutable trials remain in task silos; these reusable oracles are maintained
here so operational tests will not depend on historical task directories.
