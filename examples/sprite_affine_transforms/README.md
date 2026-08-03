# Sprite affine-transform regression fixtures

This project exercises buffered bitmap affine transforms when the transformed
bitmap is used as a sprite frame. It keeps test programs and image assets out
of the VDP firmware repository while testing the mutable firmware checkout at
`~/Agon/mystuff/agon-vdp-sprite-transforms`.

## Layout

- `src/` — eZ80 assembly fixtures (the incoming fixture template goes here).
- `assets/source/` — hand-authored source images.
- `assets/rgba2222/` — generated RGBA2222 bitmap inputs.
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

Create the emulator profile from this project directory:

```bash
./scripts/setup_emulator.py
```

Build the native module from the dedicated VDP project:

```bash
make -C /home/smith/Agon/mystuff/agon-vdp-sprite-transforms/userspace \
  FAB_ROOT=/home/smith/Agon/mystuff/fab-agon-emulator
```

The profile expects the resulting module at:

```text
/home/smith/Agon/mystuff/agon-vdp-sprite-transforms/video/build/userspace/vdp_sprite_affine_transforms.so
```

Launch only after that module and a fixture binary exist:

```bash
./scripts/run_emulator.sh
```

The setup script creates a CRLF `autoexec.txt` on first use that loads and runs
`/sprite_affine_transforms/sprite_affine_transforms.bin`. It preserves an
existing user-modified autoexec file so interactive selections remain under
user control.

The launcher uses absolute paths, a temporary fallback-free working directory,
the owned Fab emulator, its matching Console8 MOS image/map, and the bespoke
VDP module. It never falls back to stock firmware.
