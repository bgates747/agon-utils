# MOS tests setup results

All SETUP-01 implementation subtasks are complete. Raw-image C++, independent
assembly, and Jeroen BBC BASIC V ADL smoke checks passed headlessly. This is a
bounded execution baseline, not general MOS, language, filesystem, or hardware
conformance. SETUP-01 remains pending Author acceptance/commit approval.

## Recorded results

| Run | Interpreter/toolchain | Expected and observed | Evidence |
| --- | --- | --- | --- |
| W06 C++ | AgonDev 1.0, Clang 15.0.7, Binutils 2.45 | Exact marker/CRLF; HL=0x123456; stack balanced; IX preserved | tasks/SETUP-01/W06/evidence/cpp/ |
| W06 assembly | Independent GNU AS routine; same toolchain runtime | Same independently expected bytes and return/stack/IX checks | tasks/SETUP-01/W06/evidence/assembly/ |
| W05 BASIC repeat | Jeroen Venema BBC BASIC V ADL v1.0RC1 | Exact W05 BASIC PASS/CRLF; QUIT returned to MOS PC 0x000D5F with HL=0 | tasks/SETUP-01/W05/ |

## Environment and provenance

1. Linux x86_64; Fab 1.2.4; hash-pinned MOS 3.0.2 Arthur and matching map;
   bundled platform native VDP module. All successful qualified runs used
   raw MBR/FAT32 images, !boot.obey, SDL dummy video/audio and software rendering.
2. `tasks/SETUP-01/W07/run-register.json` consolidates existing receipts, image
   manifests and evidence hashes. It also records current runtime/VDP hashes
   retrospectively; those are not falsely presented as hashes captured at each
   earlier launch. VDP semantic version was not independently queried.
3. W01 retains toolchain identity and input hashes; W05 records the pinned source
   commit, byte-identical interpreter rebuild, and deployment filename
   `bbc-basic-v-adl.bin`. Every BASIC fixture must identify its target port.
4. W06 host execution durations were 1.192 s (C++) and 1.258 s (assembly),
   excluding preceding builds, including deployment/debugger/shutdown overhead.
   BASIC duration was not recorded. These are not calibrated hardware timings.
5. W07 verified retained executable hashes and exact captured bytes against
   the three success receipts without rerunning already-passing emulator tests.

## Reproduce and interpret

1. Follow `tasks/SETUP-01/W06/README.md` for raw-image C++/assembly comparisons;
   preserve existing trial images/evidence before a new experiment.
2. Follow `tasks/SETUP-01/W05/README.md` for the BASIC fixture and fresh-image
   preparation/runner. Each run must keep its own image and result records.
3. For future runs record source/build identity, executable/map and runtime
   hashes, storage-image before/after identity, fixtures, startup, launch flags,
   debugger observations, exact expected/actual results, durations and cleanup.
   Capture identities at launch time rather than relying on this retrospective
   consolidation. W07's register describes these runs, not a generic runner API.
4. Preserve discrepancies as minimal reproducers. Separate compiler call-site
   behavior, ABI wrappers, MOS, VDP, emulator, filesystem backend and fixture faults.
   RST observation proves bytes at the MOS entry, not framebuffer appearance.
5. W03 and original W04 hostfs results remain bootstrap history. They are not
   evidence of raw-image filesystem semantics. W06 reran both comparison paths
   using raw images; BASIC also used a raw image.

## Open acceptance boundary

1. MOS-01 separately tracks the missing-OBEY cleanup bug and proposed upstream
   PR, with a failing image, stack trace and successful !boot.obey comparison.
2. No physical hardware test occurred. No visual display qualification is
   asserted or needed for these CPU/output-boundary checks.
3. Changes remain uncommitted and unpushed. Author acceptance/commit approval
   is still required before closing SETUP-01 under its acceptance criteria.
