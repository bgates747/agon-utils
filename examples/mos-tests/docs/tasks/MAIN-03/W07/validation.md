# MAIN-03 W07 — Aggregate qualification

All required synthetic foundation checks and the independent fresh-image repeat
passed on Linux. The runner is ready for acceptance; this does not establish
real MOS API conformance. W06 is committed as 6bc13e9; W07 results remain
uncommitted pending Author acceptance. No push or physical hardware run occurred.

## Execution and evidence

1. Executed from /home/smith/Agon/mystuff/agon-utils/examples/mos-tests using
   /home/smith/Agon/mystuff/agon-utils/.venv/bin/python and the shared human tools.
   [qualify.py](qualify.py) is the task replay record; routine usage belongs in
   [human qualification guidance](../../../../human/qualification.md).
2. [result.json](result.json) records all 12 commands, exit statuses and durations.
   Total command wall time was 119.309 seconds, including builds, debugger pauses,
   retrieval and reporting. This is a host-duration observation, not eZ80 timing.
3. [qualification.tar.gz](qualification.tar.gz), checked by SHA256SUMS, retains
   1,165 evidence files: binary records, complete manifests, target binaries/maps,
   text/JSON reports, debugger transcripts, 8 KiB SRAM captures, run identities,
   toolchain/runtime hashes and negative-case evidence. Large raw images and host
   executables remain under .emulator/qualification/w07-01 and are excluded;
   archive-omissions.json lists them.
4. [source-identities.json](source-identities.json) pins tested source hashes,
   Git checkpoint, Python and native compiler. Runtime is Linux Fab 1.2.4 with
   MOS 3.0.2 Arthur; individual identity/target/toolchain manifests pin actual
   MOS/map, Fab, VDP, compiler, assembler, linker and test binaries.
5. The initial remote shell write of the task replay script lost quoting and
   produced a Python syntax error before any checks or outputs. Rewrote it using
   safely quoted SSH input; the full qualification then passed without a
   production-code change.

## Results

| Area | Observed result |
| --- | --- |
| Environment, planner, target build | Existing Python extension check, planner rejection/preservation controls and Agon runner build passed |
| Lifecycle | All 11 native controls passed |
| Capture | All 52 controls matched independent debugger state; reporting clobbers did not damage saved captures; SRAM guards intact |
| Recording | Six frozen record types, typed bounds, 22 fault controls and 1,064 interrupted SRAM publications passed; two target cases yielded eight card records; collision preserved prior results |
| Reports | All 58 scenarios, including 14 frozen verdict oracles, plus 690 truncations and 690 bit mutations passed |
| Startup | All ten raw-image scenarios passed; 13 SHA vectors, seven valid/seven rejected scripts, nine continuation controls passed |
| Smoke regression | C++ and independent assembly variants both passed |
| Independent fresh image | Two selected controls passed; four successful commands; return to MOS prompt observed |
| Preservation and shutdown | Repeat boot allocated a new identity and preserved earlier files; ten W06 results.bin hashes unchanged; no Fab processes remained |

Intentional failure/incomplete/unsupported scenarios matched their expected
verdicts. Default three-case startup correctly reported two passes and one
unsupported UART case, never all-pass. The explicit fresh-image selection omitted
that unavailable fixture and produced ALL TESTS PASSED for its two selected cases.

## Recovery and delivery limits

1. Supported: controlled debugger retrieval of all 8 KiB SRAM before reset,
   saved alongside raw card evidence and passed to the production decoder with
   explicit acquisition provenance. Captures and guarded recording agree with
   independently observed controls.
2. Unqualified: arbitrary CPU/VDP crash recovery, power-loss durability, physical
   hardware, IFF/alternate-register capture and alternate CPU modes. Do not reset
   before recovering SRAM. No physical confirmation is required for the synthetic
   emulator claim, but hardware behavior still needs its own run.
3. Reusable helpers already live in human/, scripts/, agents/, apps/ and tests/.
   Added a human aggregate procedure and agent link; no duplicated execution
   engine or new application was needed.
4. !boot.obey remains the local workaround. MOS-01 is parked; no firmware patch.
   The current startup parser supports three synthetic functions and seven plan
   templates, not an arbitrary large catalogue.
5. Next proposed work is MAIN-04's first 12 real MOS cases (getError, getleafname,
   pmatch), starting with direct assembly call boundaries and register evidence.
   Freeze that task contract before implementation; this run did not start it.
