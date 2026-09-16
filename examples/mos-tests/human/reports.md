# Read result reports

The host reporter validates the supplied run manifests, artifacts and binary
records before showing a summary. Complete selected coverage can say ALL TESTS
PASSED. Failures show the number and names of failing tests before details;
missing, conflicting or invalid evidence produces INCOMPLETE instead. This does
not establish hardware behavior from emulator results.

## Use on Linux

From /home/smith/Agon/mystuff/agon-utils/examples/mos-tests:

```sh
./human/mos-tests report --run /path/to/run --output /path/to/new-report
```

The run directory must contain catalogue.json, plan.json, target.json, bundle.json,
run.json, selection-script.txt, the bundle's named artifacts and results.bin.
An existing report directory is refused. W06 will deliver the general startup
bundle; the W04 recording fixture used illustrative hashes and cannot be promoted
into an authenticated suite result merely by creating a report.

1. summary.txt contains the summary and non-passing case details, without terminal
   escape codes. report.json contains machine-readable counts, findings and source
   hashes. decoded-records.json retains decoded valid-prefix evidence, including
   passing observations, without requiring a verbose presentation option.
2. Terminal colour is automatic; --colour never disables it and --colour always
   requests it explicitly. PASSED is white on green; FAILED is white on red.
   Saved reports are always plain. Untrusted reason text cannot inject controls.
3. Exit codes: 0 complete all-pass; 1 test failures; 2 configuration error or
   incomplete evidence; 3 complete execution with limited coverage. OBSERVED,
   SKIPPED, UNSUPPORTED and BLOCKED are not passes. ERROR and INCOMPLETE prevent
   completion. Failed assertions do not inflate the number of failed tests.
4. Full verbose/grouping/sorting controls are deferred. Initial output includes
   failure and other non-passing details; an all-pass report is deliberately short.

## Recovery

```sh
./human/mos-tests report --run /path/to/run --output /path/to/recovered-report \
  --sram /path/to/sram.bin \
  --recovery-note 'Fab debugger dump acquired before reset; Linux raw SD backend'
```

Use --recovered /path/to/records.bin for an explicitly recovered record stream;
it may be repeated. --records selects a different primary saved record file.
Recovery requires a note describing the backend/source and acquisition. Supplied
files are hashed into report provenance. SRAM must be an exact 8192-byte dump.
If the default card file is unavailable, recovery evidence can still be decoded,
but the report remains incomplete. Recovery never assumes reset persistence.

Default parsing stops at the first invalid boundary and retains the valid prefix.
--forensic searches for later independently valid records; fragments are explicitly
labelled and can never establish completion. Identical records from card/RAM merge
once; conflicting copies are corruption. A checkpoint error, including close
failure, overrides a wire-complete file. Emergency SRAM records remain readable
when control slots are unusable. A file-only report cannot prove close success,
absence of an unrecovered error, or power-loss durability.

## Qualify the reporter

```sh
./human/mos-tests report-check --output .emulator/reports/review
```

This is a host-only check on Linux; it does not launch an emulator. See
[decoder contract](../docs/result-decoding.md) and [W05 evidence](../docs/tasks/MAIN-03/W05/validation.md).
