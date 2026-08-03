# Sprite affine lifecycle torture fixture

`torture.asm` is the deterministic destructive companion to the visual
transform and all-format fixtures. It targets the experimental sprite binding
variable `&1412`, selected-sprite status variable `&1413`, affine test flag 1,
sprite-affine test flag 3, and hardware-sprite test flag 2.

Build it from `src/` after regenerating the project assets:

```bash
ez80asm torture.asm ../build/sprite_affine_torture.bin -c -x -l -s
/home/smith/Agon/mystuff/agon-utils/.venv/bin/python \
  ../scripts/audit_fixture_packets.py
```

The byte audit covers all 63 packet templates in this executable, all four
embedded payloads, the exact `65535 + 2049 = 67584` wide-panel split, and the
six gated stream-synchronization packets. It also continues to audit the two
earlier fixtures by default.

## Stage and status oracle

The baseline fixture activates four sprites:

1. sprite 0 is a software RGBA2222 animation with a 16x16 ship and 5x13 laser;
2. sprite 1 has the same two RGBA2222 frames and explicitly requests hardware;
3. sprite 2 is a bright-cyan Mask bitmap that explicitly requests hardware but
   must use the transformed software fallback; and
4. sprite 3 is a hidden hardware-requested 352x48 RGBA8888 panel. Phase `P`
   binds it cold to scale 8; its 2816x384 result exceeds the conservative
   frame-pixel and cache limits and must be rejected without allocating a
   cache. The phase unbinds it after reading `S8` so it does not retry every
   VSYNC.

Phase `C` temporarily activates sprite 4 as a software capture probe. It first
uses a cyan placeholder frame, then replaces that frame with a freshly captured
16x8 RGBA2222 bitmap and immediately refreshes a scale-2 cache. Returning to any
ordinary phase activates only the four baseline sprites again.

Raw ship, laser, and mask references appear above the three visible sprites.
The fixture uploads ten short VDU-text buffers, one for each current `&1413`
enum value. To display status, it selects a sprite and sends ten 16-bit
conditional buffered calls against variable `&1413`; exactly one text buffer
executes. This is a VDP-side read of the real status, not a hard-coded expected
label or a CPU-side inference.

The displayed values are:

- `S0` unbound;
- `S1` disabled, raw path with binding retained;
- `S2` pending/matrix missing;
- `S3` cached software or software fallback;
- `S4` cached hardware;
- `S5` stale software with last-good retained;
- `S6` stale hardware with last-good retained;
- `S7` invalid with no last-good cache;
- `S8` resource limit with no cache; and
- `S9` source missing and sprite hidden.

## Deterministic phases

Every destructive key except `9`, `D`, and `K` can be followed by `0` or `R`
to reconstruct the original ship buffer/bitmap, both two-frame sprites,
primary scale-2 matrix, bindings, software activation, and explicit hardware
requests. Most phases perform that reset first themselves, so results do not
depend on key order.

- `0` or `R`: recreate the live ship bitmap and both animated sprites, bind
  primary scale 2, and show sprite 1 status `S4`.
- `1`: select ship frame 0 on both animated sprites; sprite 1 remains `S4`.
- `2`: select laser frame 1 on both sprites. Both differently sized frames
  must already exist in the transactional cache; sprite 1 remains `S4`.
- `3`: XOR the colour bits of all 256 ship-source bytes in place, without
  recreating the bitmap or rebinding either sprite. The raw ship and both
  transformed ships change colour, proving source-generation invalidation and
  rebuild; sprite 1 returns to `S4`.
- `4`: change only sprite 1 from primary scale 2 to alternate top-left rotate
  90. Sprite 0 stays scaled. Sprite 1 must rotate and report `S4`; retaining
  the scale-2 image catches cache reuse across binding IDs.
- `5`: return sprite 1 to the primary matrix; it is scale 2 and `S4` again.
- `6`: publish scale 2, then replace the same primary matrix ID with a singular
  scale. The scaled result remains and hardware sprite 1 reports stale `S6`.
- `7`: publish scale 2, then compose an IEEE-754 quiet-NaN X scale into that
  live ID. The result remains and software sprite 0 reports stale `S5`.
- `8`: publish scale 2, then compose finite scale 32767 into the same live ID.
  Bounds/resource admission rejects the candidate, scale 2 remains, and sprite
  1 reports `S6`.
- `9`: explicitly clear the primary matrix buffer. This is not an internal
  matrix replacement: sprites 0, 1, and 2 become unbound/raw and sprite 1
  reports `S0`. The Mask is switched to software before becoming raw.
- `C`: paint adjacent opaque red and cyan 8x8 blocks, flush that source, then
  capture their 16x8 rectangle into a fresh buffer ID. In one uninterrupted
  VDP input block, queue a raw plot of the capture, replace already-active
  software sprite 4's placeholder frame with it, and refresh its primary
  scale-2 cache. There is no post-capture queue flush or sprite activation to
  mask an incomplete `CopyToBitmap`. Left-to-right in the probe band, the
  red|cyan source must exactly match the raw capture, and sprite 4 must show
  the same image at 2x with status `S3`.
- `D`: disable sprite-affine flag 3 while preserving a valid binding. Sprite 1
  uses its raw frame and reports `S1`; the Mask is first made software because
  an untransformed Mask is not a hardware-sprite format.
- `E`: disable and re-enable flag 3 in one deterministic phase without any
  intervening rebind. The transformed hardware cache returns with `S4`.
- `K`: clear the live ship backing buffer while sprites 0 and 1 reference it.
  Both complete frame lists are safely detached and cleared, the unrelated
  mask remains alive, no stale renderer pointer may be dereferenced, and
  sprite 1 reports `S9`. Press `0` or `R` to rebuild.
- `M`: select the hardware-requested Mask sprite's status. It must remain
  visibly transformed through software fallback and report `S3`.
- `P`: select the hidden wide-panel sprite. Its multi-block RGBA8888 source is
  valid, but its cold scale-8 cache must report resource status `S8`. The
  displayed oracle remains after the one-shot probe is unbound.
- `T`: run the disabled-affine stream-consumption suite below. A complete
  `PT SYNC PASS: gated tails consumed` marker and audible BEL are the oracle;
  sprite 1 subsequently remains `S4`.
- `U`: send one compact VDP block that queues a regular RGBA8888 bitmap plot,
  immediately recreates the same bitmap ID, and repeats that lifetime race for
  a scale-2 transformed plot. The four blocks at the left of the probe band
  must be red, cyan, scale-2 red, and scale-2 cyan. A BEL after the final queue
  flush is the liveness oracle; sprite 1 remaining `S4` shows that the baseline
  affine renderer survived the replacements.
- `Q` or Escape: deactivate/reset sprites before globally clearing buffers,
  clear all feature flags used by the fixture, and restore the caller's mode.

## Disabled-feature stream synchronization

Phase `T` first establishes a valid sprite baseline and clears affine test
flag 1. It then sends these packets while their execution is gated off:

1. `&20` 2D affine scale: inline operands with per-operand `C0` integer and
   `C8` Q8.8 formats (`AFFINE_OP_MULTI_FORMAT`).
2. `&21` 3D affine scale: three buffer-value descriptors, each with its own
   format and 24-bit advanced offset (`BUFFER_VALUE | ADVANCED | MULTI_FORMAT`).
3. `&22` generic matrix set: 2x2 size plus one buffer-value/advanced-offset
   descriptor for four contiguous values.
4. `&28` bitmap transform: resize, explicit-size, and auto-translate options,
   including the explicit width/height tail.
5. `&29` data transform, inline form: explicit size, advanced source offset,
   stride, and limit.
6. `&29` data transform, buffer-argument form: size, source offset, stride, and
   limit each supplied by a buffer ID plus 24-bit descriptor, with per-block
   also selected.

Every buffer-value descriptor points into a dedicated 24-byte argument buffer
containing bounded identity/size/offset/stride/limit values. The commands must
not execute while gated, but a broken gate cannot turn arbitrary image bytes
into a hostile allocation request.

The following independent VDU block moves the text cursor and sends BEL plus
the fixed pass marker. The phase re-enables flag 1 only after that marker. An
under-consumed optional tail would be parsed as top-level VDU commands; an
over-consumed tail would swallow marker bytes. Either failure therefore makes
the visible/audible oracle incomplete.

The fixture intentionally does not claim that all enum values must occur in
one run. `S2` and `S7` remain available to the status renderer for diagnostic
completeness, while the normative phases exercise `S0`, `S1`, `S3`, `S4`,
`S5`, `S6`, `S8`, and `S9`.

After phases `6`, `7`, and `8` render their stale-status oracle, the fixture
repairs the same primary ID to scale 2 without rebinding. This leaves the
observed `S5`/`S6` text and identical last-good pixels on screen while avoiding
an unbounded rejected-candidate retry on every later VSYNC; it also exercises
recovery from invalid/resource generations.

`C` and `U` are portable visual/liveness regressions. They deliberately avoid
host-only allocator or sanitizer hooks, so they cannot by themselves prove
that retirement performs zero allocation or diagnose a scheduler that happens
to consume every queued primitive before a vulnerable replacement. The native
userspace lifetime regression remains the deterministic oracle for those
properties.
