# Bitmap and sprite assembly fixture

`app.asm` is a self-contained eZ80 MOS application that exercises one
asymmetric RGBA2222 image through three render paths:

1. clear, write, and consolidate a 16-bit VDP buffer;
2. create and directly plot a regular untransformed buffered bitmap;
3. use the same bitmap as both a software-sprite and hardware-requested frame;
4. bind both sprites to live matrix buffer `0x5101` through VDP variable
   `0x1412` and replace that matrix interactively.

Build it from this directory:

```bash
ez80asm app.asm ../build/sprite_affine_transforms.bin -c -x
```

`formats.asm` is the companion all-format regression executable. Regenerate
its inputs first, then assemble it from this directory:

```bash
/home/smith/Agon/mystuff/agon-utils/.venv/bin/python ../scripts/prepare_assets.py
ez80asm formats.asm ../build/sprite_affine_formats.bin -c -x -l -s
```

It displays three rows and three columns. The rows are RGBA2222, RGBA8888,
and Mask/1bpp; the columns are an untransformed regular bitmap, a transformed
software sprite, and a transformed hardware-requested sprite. The program
starts at scale 2x. Press `0` for identity, `2` for scale 2x, `3` for a
top-left 90-degree rotation, or Escape/`Q` to exit.

The RGBA2222 row embeds the generated 16x16 ship. The RGBA8888 row embeds a
generated 12x8 binary-alpha oracle with opaque white/yellow orientation rows
and these three-pixel vertical bands in between:

- magenta with `A=0`, which must remain transparent;
- red with `A=1`, which must become opaque in the transformed RGBA2222 cache;
- green with `A=63`, which must likewise become opaque; and
- blue with `A=255`, which is the opaque control.

The regular RGBA8888 reference retains its original fractional alpha, so the
two low-alpha bands can be faint there. Both transformed copies must apply the
firmware's binary-alpha rule and show the red and green bands as opaque. This
specifically guards against extracting only the high two alpha bits, which
would incorrectly erase every nonzero alpha value below 64.

The mask row embeds the generated, row-aligned, MSB-first 9x5 payload. Its
deliberately asymmetric glyph has both corners set on top but ends in
`#.#...###` on the bottom, so reflections and 90-degree orientation are
unambiguous. Bitmap creation captures mode 8 logical foreground colour 14
(bright cyan), which is distinct from every RGBA8888 oracle band; the cyan
must survive cache conversion. Its right sprite receives command 19 exactly
like the other right-column sprites, but a Mask source cannot use the hardware
backend; it must remain visibly coherent through the transformed software
fallback. RGBA2222 and RGBA8888 right-column sprites are expected to use the
hardware path.

All format-suite inputs fit in one upload block. The generated 352x48
RGBA8888 control panel deliberately exceeds 65535 bytes and is reserved for a
separate multi-block/resource-limit torture phase; it is not needed to prove
format correctness.

Generate symbol and listing files for both executables and byte-audit every
packet template plus all three embedded format-suite payloads with:

```bash
ez80asm app.asm ../build/sprite_affine_transforms.bin -c -x -l -s
ez80asm formats.asm ../build/sprite_affine_formats.bin -c -x -l -s
/home/smith/Agon/mystuff/agon-utils/.venv/bin/python \
  ../scripts/audit_fixture_packets.py
```

The audit fails if a packet label is missing or unaccounted for, if an exact
packet byte/length changes, if the two programs use the wrong transform ID, or
if an embedded payload differs from its generated file. Listing and symbol
files are ignored build evidence.

The fixture uses screen mode 8. The ordinary bitmap is at the top, while two
fixed copies appear along the bottom: sprite 0 is software and sprite 1 is
hardware-requested. Number keys select deterministic transform states:

- `0`: identity;
- `1`: translation `(+8,+4)`;
- `2`: scale 2x;
- `3`: anticlockwise 90-degree rotation around the top-left;
- `4`: X shear `-0.5`;
- `5`: X reflection;
- `6`: anticlockwise 90-degree rotation around the 16x16 frame centre;
- `7`: publish scale 2x, then submit a singular matrix which must be rejected
  while scale 2x remains visible; and
- `8`: unbind both sprites and return them to the ordinary raw path.

Press `H` or `S` to change sprite 1 explicitly; press Escape or `Q` to exit.
Both sprites are initially activated as software so the VDP allocates the
saved-background storage needed for a later `H` to `S` transition; sprite 1 is
only marked hardware after that activation. The transition helpers hide and
refresh a software sprite before marking it hardware, preventing a stale
framebuffer image from being left behind.

Hardware sprites require VDP 2.12 or newer and RGBA2222/RGBA8888 frames. This
fixture targets VDP 2.12+ explicitly: it enables test variable 2 with the
currently recommended value zero, then uses sprite command 19. There is no
production capability query in this scaffold, so gate the variable commands
before adapting it to older firmware. The unconditional batch refresh is
retained because the left sprite is software.

The interactive source is intentionally independent of a file-container
format. Replace `fixture_upload_bitmap` with a loose-file or AGNB loader when
desired; keep the stable buffer ID and all downstream bitmap/sprite code
unchanged. The embedded asset may likewise become an `incbin` generated by the
project asset pipeline.
The one-block upload helper accepts exactly 1..65535 bytes and rejects larger
24-bit counts before clearing or writing the target. For larger assets, call
the guarded append hook with multiple blocks and consolidate once at the end.

Every runtime-populated 16-bit VDU packet field is populated bytewise. This is
deliberate: in ADL mode, storing BC, DE, or HL directly into `dw` writes 24 bits
and corrupts the following packet byte. Static matrix packet literals use
`dw`, which the assembler emits as exactly two little-endian bytes.

`vdu_sprite_bind_transform` and `vdu_sprite_clear_transform` use the
per-selected-sprite variable `0x1412`. The fixture enables affine matrix flag 1
and provisional sprite-affine flag 3, both with the recommended value zero.
Every non-identity matrix operation is preceded by identity so each numbered
state is independent; transitions while bound still mutate the same live
matrix ID without rebinding. Stock VDP v2.16 consumes and ignores `0x1412`, but
does not implement these transformed sprite results.

The restart/cleanup order is also part of the fixture contract: reset sprites
before globally clearing VDP buffers, recreate everything on every `RUN`, clear
the hardware-sprite test/preference variables on exit, and restore the caller's
screen mode.
