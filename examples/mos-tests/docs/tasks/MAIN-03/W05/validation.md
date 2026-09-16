# MAIN-03 W05 — decoder and report qualification

PASSED: 58 decoder/report scenarios, including all 14 agreed report outcomes;
690 truncated records and 690 corruptions rejected. The reporter leads with
truthful coverage/failure counts, preserves known failures on incomplete runs,
and never promotes forensic fragments to a complete pass.

## Reproduction

Run on Linux from /home/smith/Agon/mystuff/agon-utils/examples/mos-tests:

```sh
./human/mos-tests report-check --output .emulator/reports/review
```

Final run: check-04 (singular/plural headline polished after check-03). Inputs, binary fixtures, readable examples, CLI outputs and
result.json are copied under qualification-final/; check-03 remains under qualification/. Source hashes are retained alongside
this record. check-01 and check-02 remain ignored trial directories. All runs
passed; later runs added recovery, CLI and evidence-retention checks.

## Results

1. Frozen wire records, independent literal manifests/streams and all 14 report
   oracles passed. Counts distinguish failed assertions from failed tests.
2. Unknown/mismatched identities, missing/reordered/conflicting records, incomplete
   chunks/samples, invalid UTF-8, typed bounds and preservation contradictions
   prevent all-pass. Identical duplicates merge once. Forensic fragments remain
   incomplete even when later valid records can be recovered.
3. Artifact hashes, script changes, duplicate JSON keys, traversal and symlink
   escapes are rejected. SRAM generation conflicts, torn commits and non-ended
   states are identified. A close error overrides a complete file; emergency
   evidence survives unusable control slots in the decoder's interpretation.
4. CLI exit codes, no-overwrite output, white-on-green/red ANSI badges, explicit
   reset sequences and plain saved output passed. Untrusted controls are escaped.
   decoded-records.json retains passing as well as failing captured evidence.
5. No emulator/hardware launch, firmware edit, commit or publication. Full bundle/
   startup integration remains MAIN-03 W06. Validation concerns supplied evidence;
   file-only results do not prove close success or physical durability.
