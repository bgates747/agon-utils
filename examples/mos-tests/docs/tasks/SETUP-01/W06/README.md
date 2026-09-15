# W06 — Raw SD-image baseline

W06 is complete. Preferred MOS 3 !boot.obey startup removes the missing-file
cleanup failure from the normal path. Both C++ and hand-assembly raw-image
runs passed exact output, HL=0x123456, stack balance and IX preservation.
The fallback defect is tracked separately in MOS-01; historical failures below
remain evidence of that defect.

## Implemented

1. `scripts/prepare_sd_image.py` creates a 65 MiB MBR disk with a 64 MiB FAT32
   partition at LBA 2048, matching BPB hidden-sector metadata. It copies only
   `/!boot.obey` and `/mystuff/test.bin`, verifying both byte-for-byte before
   MBR assembly and again through the final partition offset. It records hashes.
2. Existing output paths are refused. Images and local tools remain in ignored
   `.emulator/`. No mount, sudo, host disk formatting, or upstream edits are used.
3. `scripts/run_emulator.py` requires an existing image and supplies
   `--sdcard-img` to the canonical profile wrapper, with dummy SDL video/audio
   and software rendering. Conflicting SD backend arguments are rejected.
   The core disables hostfs when an image is selected. Missing-image validation
   fails before emulator launch.
4. `make sd-image` builds the current test and creates `.emulator/test-sd.img`.
   `make headless` runs that image. Do not use the inherited `make em`/`copy`
   targets for qualification: those are upstream hostfs conveniences.
5. mtools 4.0.43-1build1 was downloaded from the host's configured Ubuntu
   repository and extracted into `.emulator/tools/mtools` without system
   installation. `mkfs.fat` 4.2 was already installed. Recreate tools with:

```bash
cd .emulator/tools
apt-get download mtools
dpkg-deb -x mtools_*.deb mtools
```

## Qualification failure and trials

1. `trial-01-raw-fat32-fault/`: unpartitioned FAT32 image, default RAM; fault
   reading 0xa26300, PC 0x00e58c after `LD A,(IY+0)` at 0x00e589.
2. `trial-02-zero-ram-fault/`: zero RAM initialization, same fault.
3. `trial-03-mbr-fault/`: MBR-partitioned FAT32, same fault.
4. `trial-04-mount-trace-timeout/`: trace beginning at MOS `_f_mount` (0xe5e4)
   progressed within mount-related code but hit the 30-second harness deadline
   before the expected checkpoint. Compressed traces are retained. Timing was
   heavily affected by logging; this is an incomplete run, not a passing variant.
5. `trial-05-precise-interrupts-fault/`: precise interrupts, same pre-main fault.
6. `evidence/cpp/`: final MBR builder with matching BPB hidden sectors and
   final-partition readback, same pre-main fault. Assembly qualification was
   not attempted after the C++ boot failed.
7. The first FAT32 image passed read-only `fsck.fat -n` with four files and
   six used clusters. This and byte readback validate host-side structure;
   they do not prove emulator SPI/FatFS correctness.
8. No evidence yet establishes whether the defect belongs to MOS, Fab's CPU/
   SD implementation, or another boot assumption. The failure occurs before
   the W04 fixture, so this is not evidence of an AgonDev-generated test fault.

## Reproduce qualification

From the MOS tests subproject root:

```bash
../../.venv/bin/python docs/tasks/SETUP-01/W06/run_image_comparison.py
```

The runner uses a fresh `.emulator/w06-boot-obey-cpp.img` and refuses an existing
trial image. Preserve/move that image and the prior `evidence/` before rerunning
with changed inputs. It derives addresses from the fresh fixture map and
records raw/clean debugger transcripts; unexpected stops fail qualification.
All owned emulator processes were closed, including the timed-out trace run.

## Successful qualification

`evidence/cpp/` and `evidence/assembly/` contain the passing run receipts,
image manifests, captured output, debugger transcripts and built artifacts.
Runs used default RAM initialization and interrupt mode, stock MOS 3.0.2 and
Fab 1.2.4, with raw MBR/FAT32 images and CRLF !boot.obey startup.
The earlier final-MBR failure is preserved in `trial-06-final-mbr-fault/`.

The default `.emulator/test-sd.img` was rebuilt with !boot.obey; its predecessor
was preserved under `.emulator/pre-boot-obey-test-sd.img`. No MOS patch was
needed to establish this baseline. MOS-01 owns correcting the separate missing
OBEY file cleanup and preparing a PR. No physical hardware or commit approval
is implied. All test processes exited zero.
