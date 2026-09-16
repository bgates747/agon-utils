# MAIN-03 W06 — editable startup qualification

PASSED: ten raw-image startup scenarios, seven valid function selections, seven
rejected script forms, 13 SHA-256 boundary vectors and nine continuation-state
controls. Real OBEY/EXEC chaining and MOS prompt return were observed. The local
!boot.obey workaround remains; firmware and hardware were not modified.

## Reproduction

On Linux from /home/smith/Agon/mystuff/agon-utils/examples/mos-tests:

```sh
./human/mos-tests startup-check --output .emulator/startup/review
```

Use a new directory. Final comprehensive run: qualification-03. result.json lists
all scenarios and durations. qualification.tar.gz preserves scripts, deployment
readbacks, bundle/runtime/source identities, generated manifests, target binary/
map, debugger transcripts, SRAM, retrieved run directories and reports. Raw images
and native executables remain in ignored .emulator/startup/qualification-03.
The archive also includes positive and negative CLI checks; their target build
predates the final continuation hardening, while the final comprehensive run
qualifies that hardening. source-identities.json records the final maintained code.
Archive checksum and a directly readable autoexec example are retained here.

## Results

1. Full script: begin, three groups and finalize returned zero; report has two
   passes plus one unsupported UART control, honestly labelled limited coverage.
2. Single function and a commented-out whole group produce complete all-pass
   reports for exactly their selected cases. Run/plan hashes are real generated
   identities, not the earlier W04 illustrative hashes.
3. A deliberate discrepancy is saved as one failed test and later groups continue
   and pass. Injected infrastructure failure stops after begin with status35 and
   an incomplete report. Script mutation after begin stops with status26 and
   incomplete evidence. Unknown function stops with status20 before allocation.
4. Controlled stops before the second selected group and before finalize both
   remain incomplete. No attempt is made to present interrupted work as a pass.
5. Reboot preserves the first run byte for byte, retains its namespace, increments
   the persisted counter from1 to2 and creates a distinct directory. All owned
   emulator processes close. Final helper verifies live runtime hashes before use.
6. Native SHA vectors match hashlib across padding/block boundaries. The shared
   parser rejects missing scaffolding, unmatched pairs, unknown/duplicate groups,
   unsupported commands and NULs. The continuation parser rejects torn, foreign,
   dirty, non-ready, inconsistent and conflicting same-generation control slots.
7. Human CLI begins with the report headline and returns0 for all-pass; invalid
   startup begins INCOMPLETE and returns2. Saved reports remain plain text. The
   positive CLI check additionally exercised a third boot of a prepared image.

## Trials and limits

build-01/run-01 exposed a packaging mistake: catalogue/target files were copied
once as manifests and again as artifacts into exclusive destinations. It stopped
before tests; retained partial evidence is under .emulator/startup/run-01.
Fixed duplicate copying; build-02/run-02 passed the full chain. qualification-01
and qualification-02 passed incremental acceptance sets; qualification-03 adds
shared continuation integrity checks and current runtime verification.

A supplemental inspection incorrectly assumed reset SRAM was zero-filled; dumps
showed FF throughout the unused stack/guard region instead. No system writer was
attributed and no zero-init or freshly seeded guard qualification is claimed.
The main capture qualification remains separate. Host elapsed times are not
hardware timing. Physical hardware, power-loss atomicity and arbitrary crash
recovery remain unqualified. No firmware patch, new commit or push in W06.
W06 is implemented and qualified pending Author acceptance; W07 remains frozen
and unstarted until the acceptance checkpoint is committed.
