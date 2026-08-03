# Sprite affine-transform regression fixtures

This project exercises buffered bitmap affine transforms when the transformed
bitmap is used as a sprite frame. It keeps test programs and image assets out
of the VDP firmware repository while testing the mutable firmware checkout at
`~/Agon/mystuff/agon-vdp-sprite-transforms`.

## Layout

- `src/` — eZ80 assembly fixtures (the incoming fixture template goes here).
- `assets/source/` — vendored PNGs and hand-authored mask sources.
- `assets/rgba2222/` — generated RGBA2222 bitmap inputs.
- `assets/rgba8888/` — generated row-major RGBA8888 bitmap inputs.
- `assets/mask/` — generated row-aligned, MSB-first 1bpp mask inputs.
- `assets/manifest.json` — deterministic dimensions, formats, provenance, and
  SHA-256 checksums for sources and generated inputs.
- `expected/` — expected records, hashes, or reference captures.
- `docs/` — technical reports and chronological development evidence.
- `build/` — ignored assembler output.
- `emulator/` — ignored, mutable bespoke emulator profile.

## Environment

Use the repository environment explicitly:

```bash
cd /home/smith/Agon/mystuff/agon-utils
.venv/bin/python tests/test_agonutils.py
```

Regenerate the bitmap fixtures and manifest with that same environment:

```bash
.venv/bin/python \
  examples/sprite_affine_transforms/scripts/prepare_assets.py
```

The generator fails closed if a vendored source, the Agon64 palette, image
dimensions, Pillow mode, output byte count, or the 9x5 mask packing differs
from the pinned inputs. RGBA2222 conversion uses this checkout's compiled
`agonutils` module. RGBA8888 is Pillow's row-major `R G B A` byte stream. Mask
rows round up independently to whole bytes, with the leftmost pixel in the
most-significant bit and all padding bits clear. It also generates a 12x8
RGBA8888 binary-alpha oracle containing exact alpha values 0, 1, 63, and 255.

## Assembly fixtures

Build the interactive transform, all-format, and lifecycle-torture fixtures
from `src/`:

```bash
cd examples/sprite_affine_transforms/src
ez80asm app.asm ../build/sprite_affine_transforms.bin -c -x -l -s
ez80asm formats.asm ../build/sprite_affine_formats.bin -c -x -l -s
ez80asm torture.asm ../build/sprite_affine_torture.bin -c -x -l -s
```

The first executable preserves the interactive RGBA2222 transform matrix
tests. The second presents RGBA2222, RGBA8888, and Mask rows through raw,
software-sprite, and hardware-requested columns. Mask is expected to fall back
to software. The third exercises two-frame cache generations, binding-ID
switches, invalid/resource retention, live bitmap destruction/recreation,
status variable `&1413`, a 67584-byte two-block RGBA8888 upload, and gated
stream synchronization. It also covers same-ID replacement while ordinary and
transformed plots are queued, plus immediate raw/sprite consumption of a fresh
screen capture. See `src/FIXTURE.md` and `src/TORTURE.md` for the visual oracles
and controls.

After assembling with symbols, audit every emitted VDU packet and embedded
payload across all three fixtures:

```bash
cd /home/smith/Agon/mystuff/agon-utils
.venv/bin/python \
  examples/sprite_affine_transforms/scripts/audit_fixture_packets.py
```

Create the emulator profile from this project directory:

```bash
./scripts/setup_emulator.py
```

Build the native module from the dedicated VDP project:

```bash
make -C /home/smith/Agon/mystuff/agon-vdp-sprite-transforms/userspace \
  FAB_ROOT=/home/smith/Agon/mystuff/fab-agon-emulator-sprite-transforms
```

Build ESP32 firmware through the fixture project's paired-dependency wrapper:

```bash
./scripts/build_firmware.sh
```

The wrapper fingerprints both mutable Git worktrees, gives each source state an
isolated PlatformIO build/libdeps directory under ignored `build/`, and verifies
that PlatformIO compiled an exact copy of the dedicated
`vdp-gl-sprite-transforms` source. This avoids silently reusing the stock
`all-the-plots` dependency or a stale `.pio/libdeps` copy. Additional PlatformIO
arguments are passed through, so a connected target can be flashed with, for
example, `./scripts/build_firmware.sh -t upload --upload-port PORT`.

The profile expects the resulting module at:

```text
/home/smith/Agon/mystuff/agon-vdp-sprite-transforms/video/build/userspace/vdp_sprite_affine_transforms.so
```

Launch the existing autoexec selection only after its module and fixture
binary exist:

```bash
./scripts/run_emulator.sh
```

Select any generated fixture for the next launch without hand-editing
`autoexec.txt`:

```bash
./scripts/run_emulator.sh transforms
./scripts/run_emulator.sh formats
./scripts/run_emulator.sh torture
```

The explicit selector first verifies that the corresponding transform, format,
or torture binary exists, then replaces `autoexec.txt` with the exact CRLF
load-and-run sequence. An unknown selector or absent binary fails before Fab
starts. With no selector, the launcher does not alter `autoexec.txt`.

The setup script creates a CRLF `autoexec.txt` on first use that loads and runs
`/sprite_affine_transforms/sprite_affine_transforms.bin`. It preserves an
existing user-modified autoexec file unless fixture selection is explicitly
requested, so interactive selections otherwise remain under user control. On
profile refresh it migrates the three Fab executable/MOS symlinks only when
their targets exactly match those formerly generated for
`/home/smith/Agon/mystuff/fab-agon-emulator`; any other target or regular path
is refused.

The launcher uses absolute paths, a temporary fallback-free working directory,
the dedicated sprite-transform Fab emulator, its matching Console8 MOS
image/map, and the bespoke VDP module. It never falls back to stock firmware.

## Deploy to the physical SD card

With the Agon card mounted at `/media/smith/AGON`, deploy the three accepted
fixture binaries with:

```bash
./scripts/deploy_sdcard.sh
```

The script has no destination argument. It validates the mount point, source
hashes, and every existing destination component; refuses symlinks and special
entries; then recursively replaces only the contents of
`/media/smith/AGON/mystuff/tests/sprite_xfrms`. Each copied file is verified
before the card is synchronized.
