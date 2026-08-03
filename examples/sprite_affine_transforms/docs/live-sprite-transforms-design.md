# Removing the live-transform restriction from Agon sprites

Status: **IMPLEMENTED ON EXPERIMENTAL PAIRED BRANCHES**, updated 2026-08-03.
The implementation and fixtures are intentionally uncommitted and unpushed
pending final review and the repository's human-validation/commit gate. This is
not yet a released protocol contract.

This report follows
[`bitmap-transforms-vs-sprites.md`](./bitmap-transforms-vs-sprites.md),
which establishes why the restriction exists. The short version is that the
matrix is currently `Context` draw state used by one bitmap primitive, while a
sprite carries only raw frame pointers and is rendered by two independent,
untransformed paths.

## Implementation result

The functional restriction has been removed for the three bitmap formats that
can be sprite frames: Mask, RGBA2222, and RGBA8888. A software sprite or a
hardware-requested sprite can bind a valid 2D affine matrix and use translation,
scaling, reflection, rotation, shear, or any nonsingular composition of those
operations. Perspective matrices, singular matrices, non-finite coefficients,
and results outside the documented resource/coordinate limits fail closed.

The implementation deliberately does **not** execute floating-point affine
sampling in the VGA scanline ISR. Firmware copies and validates the matrix,
inverse-samples every animation frame into a private RGBA2222 cache, and then
publishes immutable ordinary sprite frames. The existing software compositor or
hardware overlay consumes that cache without knowing about matrix buffers. This
gives both requested sprite kinds the same public transform behavior while
keeping unbounded work and mutable buffer state out of scanout.

This differs from one detail of the original staged recommendation below: the
software path also consumes the shared pre-rasterized cache instead of gaining a
second affine sampler inside its background-saving compositor. One cache
implementation proved smaller, made all animation frames transactional, and
kept the renderer-facing lifetime protocol identical for both backends.

### Experimental control and status

The feature is gated by experimental test flag 3
(`TESTFLAG_SPRITE_AFFINE`). The binding is per sprite:

```text
VDU 23,0,&F8,&1412; matrixBufferId;
```

`&FFFF` unbinds the selected sprite. VDP variable `&1412` reads the selected
sprite's binding and `&1413` reports its current state:

| Value | Meaning |
| ---: | --- |
| 0 | unbound |
| 1 | feature disabled |
| 2 | pending (for example, matrix buffer not yet present) |
| 3 | valid private cache using software composition |
| 4 | valid private cache using hardware composition |
| 5 | last-known-good software cache retained after a rejected update |
| 6 | last-known-good hardware cache retained after a rejected update |
| 7 | invalid matrix or unreliable source identity |
| 8 | coordinate, frame-count, allocation, or memory-reserve limit |
| 9 | sprite source frame missing |

Changing a bound matrix or source bitmap generation makes the binding dirty;
the next sprite presentation rebuilds it. All frames are prepared before a new
generation is published. A rejected matrix update retains the complete
last-known-good cache only while every source bitmap and generation still
matches. An explicit public clear of the bound matrix buffer unbinds it; normal
in-place replacement preserves the ID binding and causes regeneration. Sprite
reset/full reset clear all bindings.

The existing `VDU 23,0,&96,flags,matrixBufferId;` affine selector also accepts
bit 1 for the current sprite. Every gated affine command now consumes its full
payload even while the underlying affine test flag is disabled, so probing or
conditional use cannot leave payload bytes to desynchronize the VDU stream.

### Formats and renderer choice

- RGBA2222 is copied directly into the private cache.
- RGBA8888 RGB channels are reduced to their top two bits. Alpha preserves the
  existing sprite convention: zero remains transparent and every nonzero value
  becomes fully opaque RGBA2222 alpha (`A=3`).
- Mask frames are sampled through the source bitmap's RGBA2222 accessor and use
  software composition.
- A hardware-requested transformed sprite remains on hardware for `Set`, and
  for `XOR` only when every source is RGBA2222. Mask, unsupported logical paint
  modes, and RGBA8888 XOR are pinned to the software path so their semantics are
  not silently changed. The selected status makes that choice observable.

Nearest-neighbour sampling uses transformed pixel-cell corner bounds and
inverse-mapped destination pixel centres. This is internally consistent for
negative bounds and right-angle rotations, but fractional transforms can
rasterize edge pixels differently from the older regular transformed-bitmap
plot helper. The public bitmap and cache sources are never overwritten.

### Admission and safety limits

The experimental implementation admits at most 64 frames per transformed
sprite, 1024x768 pixels per transformed frame, 2 MiB of cached pixels per
sprite, and 65,536 pixels per frame when software composition is required. It
also preserves 256 KiB of PSRAM and, for software sprites, 96 KiB of internal
RAM, while checking largest contiguous blocks and every dimension/product
conversion. These are conservative safety limits, not a statement of maximum
ESP32 performance. Rejection is visible as status 8 and leaves a qualifying
last-known-good generation intact.

Bitmap and matrix generations cover buffered mutation and bitmap recreation.
Publication is failure-atomic: replacement storage and bitmap metadata are
allocated before retiring an old bitmap, source generations are rechecked after
cache construction, and renderer-facing pointers are published only as one
validated list. Old pointers are detached, fenced across a presentation
boundary, and only then freed. `vdp-gl` now has checked bitmap/list admission,
coherent pointer/count/stride snapshots, and an explicit sprite-retirement
fence. The userspace renderer serializes that fence with framebuffer readers;
the ESP32 renderer crosses a scanout boundary.

### Validation completed

- Native userspace VDP module build passed against the dedicated Fab emulator.
- The renderer's deterministic publication/lifetime regression passed ten
  consecutive runs.
- Five deterministic source assets cover RGBA2222, RGBA8888 (including alpha
  0, 1, 63, and 255), Mask, a 5x13 rectangle, and a 352x48 RGBA8888 upload whose
  67,584-byte payload crosses the 65,535-byte protocol block boundary.
- Three eZ80 fixtures assembled successfully. A packet audit checked 153 VDU
  templates across their binaries, and the ADL-width audit reported zero
  hazards.
- The Author accepted the interactive transform fixture, the all-format
  fixture, and the lifecycle/parser torture fixture in the bespoke emulator.
  In the final extended torture run, the Author also accepted the queued
  same-ID replacement (`U`) and immediate screen-capture consumer (`C`)
  oracles; `Q` completed teardown and the emulator exited with status 0. That
  73,211-byte executable has SHA-256
  `c7c1ca74dea30b15cab1d99ccf6af780e5aaa159a1126e8c610bb10e9dcbb99c`.
- The final paired ESP32 build used 45,840 bytes RAM and 1,098,025 bytes flash.
  Its 1,098,400-byte `firmware.bin` has SHA-256
  `db603aabeadad68f1529c83e3691034391aa94ef334e191bb69bf43bf736bebe`.
  Esptool wrote and hash-verified that exact artifact on the connected
  ESP32-PICO-D4, then hard-reset the board. The Author confirmed the custom
  firmware signature, AgonJukebox audio and ordinary-bitmap operation, and
  successful entry into mode 20 (512x384x64, single buffered). No affine
  assembly fixture has yet been staged on the physical machine.

- After the VDP and renderer changes were committed locally, the paired wrapper
  rebuilt their clean trees under fingerprint `d7671adb9fda4d10`. It reproduced
  the same 45,840-byte RAM and 1,098,025-byte flash usage and the same
  1,098,400-byte image size. That later image has SHA-256
  `45830ade28cd87b3599708047a0f7f5ba82236edc4f42343cd16af45ef94220e`.
  It was not flashed; the preceding `db603a...bebe` image remains the exact
  hardware-validated artifact. The two builds used identical source content
  but different fingerprint/build directories, so their binary hashes are
  recorded separately rather than claiming byte reproducibility.

The first full-feature hardware artifact exposed an important admission
regression before the final build above. It reserved 28,672 bytes of new sprite
state and renderer arrays unconditionally in BSS, increasing reported RAM from
the 44,688-byte upstream baseline to 73,496 bytes. The machine booted and ran
AgonJukebox, but a request for mode 20 remained on the 640x480 mode-0 display
because the framebuffer allocation no longer fit. Transform state is now
allocated lazily per bound sprite in preferred PSRAM, and the renderer proxy is
a checked exact-size internal-RAM allocation for only the active high-water.
The final static increase is 1,152 bytes, and the repeated physical mode-20
test passed.

### Delivery boundary and remaining limitations

The paired renderer change is mandatory. The stock `agon-vdp` PlatformIO
dependency still names upstream `vdp-gl#all-the-plots`, which does not contain
the checked publication/retirement API. The fixture project's
`scripts/build_firmware.sh` fingerprints both mutable worktrees, builds in an
isolated directory, installs the exact dedicated renderer checkout, verifies it
byte-for-byte, and fails closed on a mismatch. Before this can be merged or
released, the renderer changes need their own published commit and the VDP
dependency must be advanced to that commit.

Cache construction and list replacement are synchronous and conservative. A
dirty update can briefly detach the active list while rebuilding/publishing,
and the ESP32 retirement fence assumes active scanout after VGA initialization;
it is not a general fence for a controller whose scanout has been stopped.
Native on-the-fly hardware affine sampling, asynchronous cache jobs, a stronger
completion command, and protocol stabilization remain future work rather than
requirements for removing the functional restriction.

The lazy layout also makes two admission details explicit. Activating `N`
sprites needs a checked internal-RAM proxy of approximately `32 * N` bytes in
addition to the renderer's canonical list, so the tightest framebuffer modes
may admit fewer than the protocol maximum even though ordinary mode selection
is no longer penalized by an unconditional reservation. A failure to allocate
the small per-bound transform-state object currently leaves that sprite
reported as unbound rather than resource-limited; later cache and proxy
admission failures do report status 8. Both are implementation limitations,
not changes to transform semantics.

The remainder of this document preserves the original design reasoning and
alternatives. Future-tense recommendations below are historical unless the
implementation-result section above says they were adopted.

## Original executive recommendation

Do not try to make sprites inherit the current bitmap transform, and do not
silently regenerate public bitmap buffers. Add an explicit **per-sprite matrix
binding**, then introduce a renderer-owned, immutable transform snapshot.

The lowest-risk delivery is staged:

1. Implement full live affine transforms in the **software-sprite** compositor.
2. For a hardware-requested sprite, prepare a private transformed RGBA2222
   frame outside the ISR and atomically hand it to the existing fast hardware
   compositor. Cache it while frame and matrix generation remain unchanged;
   coalesce rapid updates, and keep the **entire previous render entry** active
   until its replacement is ready. Choose and pin a software backend instead if
   cache memory/update limits cannot be admitted when the binding is activated;
   do not switch paths opportunistically between matrix generations. This
   preserves hardware overlay/double-buffer behavior where practical without
   silently replacing any public bitmap.
3. Measure and optimize the shared inverse-sampling implementation. The
   existing public buffered operation `&28` remains a manual workaround; the
   private cache is an implementation detail of the live binding.
4. Add native **hardware-sprite** transforms only after a fixed-point,
   incremental scanline implementation demonstrates safe worst-case VGA timing
   on physical ESP32 hardware. Until then, cache/software fallback removes the
   functional restriction without risking scanout corruption.

This is not a one-line plumbing change. It spans the VDU contract, buffer
lifetime tracking, sprite state, software background preservation, and—if
native hardware support is required—the IRAM VGA scanline compositor.

## Author scope clarification

The Author asked whether this proposal means that any supported transform can
be used with either a software sprite or a hardware sprite.

Yes, at the public behavior level: any sprite may bind any valid supported 2D
affine matrix, including translation, positive or negative scaling,
reflection, rotation, shear, and compositions of those operations. Software
sprites use the affine-aware software compositor. A hardware-requested sprite
initially uses a private transformed RGBA2222 frame with hardware scanout where
resource limits permit; an explicit policy may instead allow a status-visible,
pinned software fallback.

This behavioral guarantee does **not** require every transform to execute
natively inside the timing-critical hardware-sprite scanline renderer. Native
on-the-fly hardware rotation and shear remain a later, physical-hardware-
qualified optimization. Non-affine or perspective matrices, singular or
malformed matrices, and transforms outside documented memory or timing limits
are not covered by the guarantee.

## Source baseline and meaning of “live”

The design was derived from:

- canonical `agon-vdp` at
  `c7ac293d2aa81ddfa693390549bcd909069c8fc3`, exactly tag `v2.16.0`;
- its installed `vdp-gl` `all-the-plots` dependency at
  `ac2dd5986daf496c43ae8e7fe41836274aec54a0`; and
- canonical `agon-docs` at
  `f9806bd3cbff6ed5d1c08bef1d51fed11764b86b`.

Here, “live” should retain the existing bitmap-transform contract: the sprite
is bound to a matrix **buffer ID**, and changing that matrix affects the next
sprite rendering operation. It should not mean that the scanline ISR reads the
mutable matrix buffer directly. The logical state remains a live binding; the
renderer consumes a validated snapshot of its current contents.

Preserve the current presentation rule rather than making command 15 newly
mandatory. Matrix mutation marks affected bindings dirty; the next renderer
sprite-presentation cycle may resolve and publish them. `VDU 23,27,15`
(refresh sprites) explicitly requests such a cycle, while an ordinary drawing
primitive may trigger it first, as `showSprites()` already does today. Multiple
edits before that cycle coalesce.

Hardware cache preparation complicates that rule. The initial implementation
should either finish the cache before declaring the candidate publishable, or
leave the entire old hardware render entry active and expose the requested
generation as pending. If cache building is asynchronous, command 15 requests
generation; it does not promise that an unfinished generation is visible when
the command returns. Completion queues an automatic next-vblank publication—no
second refresh is required. A later synchronous/wait option can provide a
stronger fence. This distinction must be explicit in the protocol documentation.

For hardware entries, any completed pending state is promoted automatically at
the next frame boundary. Current raw sprite fields can change during a frame;
latching them coherently introduces at most one frame of latency and is an
intentional compatibility tradeoff required to prevent mixed matrix/frame/
position state.

## Public VDU contract

### Canonical control: activate the reserved variable `&1412`

The source already reserves internal variable `0x412` with the comment
“Current sprite transform ID - not supported.” Implement its read and write
cases and expose it as VDP variable `0x1412`:

```text
VDU 23,0,&F8,&1412; matrixBufferId;
```

The command applies to the currently selected sprite (`&1410`). A value of
`&FFFF` clears the binding. Reading `&1412` returns the selected sprite's bound
ID, or `&FFFF` if none is bound.

This is preferable to allocating a new sprite subcommand with trailing
arguments. `&F8` has a fixed payload, so old firmware consumes both 16-bit
values and harmlessly ignores unknown variable `0x412`. An old parser presented
with an unknown sprite subcommand consumes only the command byte; any following
matrix ID bytes become new VDU commands and can desynchronize the stream.

Use `&F8,&1412,&FFFF` as the canonical clear operation. The current
`clearVDPVariable()` implementation does not route the `0x1000`–`0x1FFF` VDU
variable range back to `Context`, so `VDU 23,0,&F9,&1412;` must not be documented
as equivalent unless that general clear path is first corrected.

### Optional shorthand: affine flag bit 1

The existing command can also be extended symmetrically:

```text
VDU 23,0,&96,flags,matrixBufferId;
```

Keep bit 0 as “current bitmap” and assign reserved bit 1 to “current sprite.”
Bits 0 and 1 may be combined. This shorthand is optional; `&1412` is sufficient
and is safer for cross-version software.

If bit 1 is added, the handler must read `flags` and `bufferId` **before**
testing the affine feature gate. The v2.16.0 handler returns before consuming
those bytes when the gate is disabled, which is already a stream-alignment
hazard for a caller that sends `&96` prematurely.

### Semantics that should be fixed in the contract

1. The binding is **per sprite**, not per frame. It applies to whichever frame
   is current; changing to a differently sized frame recomputes bounds.
2. Sprite x/y remains the screen position of local `(0,0)`. The matrix acts in
   sprite-local coordinates and can move pixels to negative local offsets.
   Rotation is therefore around the frame's top-left by default, matching
   bitmap plots. A caller rotates around another pivot by composing
   translate-to-pivot, transform, and translate-back matrices.
3. The selected bitmap transform and selected sprite transform are independent.
   Attaching a frame never captures `Context::bitmapTransform`, so existing
   applications retain their current behavior.
4. Clearing frames should preserve the sprite binding just as it preserves
   position and paint state; reset-sprites and full reset should clear every
   binding to `&FFFF`.
5. Binding an ID that does not yet exist is a pending binding and draws through
   the ordinary untransformed path until a valid generation is available. If a
   later mutation is invalid, retain the last-known-good published image/state
   and report it stale; do not expose a torn matrix or silently jump to identity.
   Explicit `&FFFF`, sprite reset, or an explicit public clear of the bound
   buffer unbinds it.
6. Existing nearest-neighbour and alpha semantics should remain initially:
   Mask, RGBA2222, and RGBA8888 for software; RGBA2222/RGBA8888 and only the
   paint modes already supported by hardware for a future native hardware path.

Keep the existing affine-matrix gate for matrix construction and add a separate
experimental sprite-affine gate/kill switch; assign its numeric ID through
protocol review rather than assuming the next value is free. The minimum
support probe is still safe without a write: new firmware reports VDU variable
`&1412` as existing even when its value is `&FFFF`, while v2.16.0 reports it
absent. Keep this read/existence behavior independent of whether the
sprite-affine gate is currently enabled, avoiding a circular probe. Existing
buffered read-variable or conditional-variable commands can distinguish those
cases with a default sentinel. Do not use “set and read an unknown test flag”
as discovery, because old firmware stores unknown flags and would produce a
false positive. Clearing the sprite-affine gate should publish the feature
disabled safely without discarding bindings, so re-enabling it can rebuild
snapshots.

Before enabling automatic backend selection, reserve adjacent read-only
variables through the same review: one selected-sprite status variable (valid,
pending, stale/error, private-cache, software fallback, native hardware) and one
API-revision/capability bitfield. Status is required because software fallback
changes observable ordering and buffering; it should not be merely a future
diagnostic. Also provide a policy/opt-out that rejects a transform rather than
falling back when the caller requires hardware overlay semantics. A future
generic VDP identity packet may carry the same capability, but this design need
not wait for that unfinished protocol work.

## Split logical state from render state

The VDU side should store, per sprite:

- bound matrix buffer ID;
- last observed buffer generation;
- dirty/valid status; and
- the requested hardware/software and fallback policy.

The renderer should receive no buffer ID and no `BufferStream *`. It should
receive a compact, immutable `SpriteTransformRenderState` containing at least:

- active/valid flags;
- the six coefficients of the inverse 2D affine transform;
- a transformed local bounding rectangle;
- the source frame dimensions used to compute that rectangle; and
- a generation or sequence number.

For the eventual ISR path, store coefficients as a proven fixed-point format
such as signed Q16.16 in internal DRAM. Double-buffer the **whole hardware render
list**, not just six coefficients per sprite: a coherent entry also needs its
frame/cache pointer, dimensions, stride, position, bounds, format, paint mode,
and generation. Build the inactive list, issue the required memory barrier, and
publish it by one aligned atomic pointer/index change at vertical blank. Retire
the old list and any cache only after the ISR acknowledges a later generation.
Do not expose a `shared_ptr`, PSRAM vector, float inverse cache, or partially
writable field set to the ISR; `volatile` alone is not synchronization.

Private cache work must also retain immutable ownership of its source bitmap
and record that bitmap's generation. A frame clear/replacement cancels pending
jobs; publication revalidates both source and matrix generations. Published
source/cache pixels cannot be freed until the frame-boundary acknowledgment has
retired their render list.

A six-coefficient fixed-point transform plus bounds/flags is roughly tens of
bytes rather than the 72 bytes required by two full float 3x3 matrices, but the
whole render entry also includes the frame and other coherent sprite fields.
Measure the complete double-buffered list and decide whether all 256 entries are
allocated eagerly from actual internal-DRAM headroom; deterministic storage is
preferable to allocation in the scanline path.

### Matrix preparation

Preparation occurs outside the renderer/ISR and should be transactional:

1. Resolve the bound ID and copy the forward 3x3 matrix to local storage.
2. Require finite values, an affine final row, and a nonsingular 2x2 linear
   portion. Reject NaN, infinity, perspective terms, and determinants too close
   to zero for the chosen numeric representation.
3. Compute the inverse from that same copied forward matrix.
4. Transform the source pixel-cell rectangle `[0,width] × [0,height]`. Use
   `floor(min)` and `ceil(max)` to form a half-open destination rectangle, then
   convert once to FabGL's inclusive `Rect`. This avoids truncating negative
   rotated corners or adding an unused edge column.
5. Clip bounds and prove that coordinates, row strides, allocation products,
   and fixed-point conversions cannot overflow.
6. Convert the inverse coefficients, build the inactive render snapshot, and
   publish only after all validation and any required background allocation
   succeed.

The existing transformed-bitmap helper should be refactored around the same
bounds and sampling definitions rather than called from `showSprites()`.
`drawBitmapWithTransform()` hides sprites itself, owns and frees its matrix
payload, and cannot save a transformed background, so invoking it from sprite
display would recurse across the wrong lifecycle.

That refactor is also a correctness prerequisite. The existing code mixes an
inclusive `Rect` with exclusive `< X2`/`< Y2` raster loops: identity happens to
produce the expected source size, but right/bottom clipping can drop the final
visible row or column. Casting transformed negative/fractional corners to `int`
also truncates toward zero and can underestimate rotated bounds. Keep geometry
internally as checked int32 half-open boxes and convert to FabGL `Rect` only at
the boundary.

The bounds rule and sampling rule must be a matched pair. The recommended rule
samples destination pixel centers `(x+0.5,y+0.5)`, inverse-maps that point, and
uses `floor()` to select a source cell in `[0,width) × [0,height)`. It works with
the transformed cell-edge box above for negative scale/reflection; naively
combining edge bounds with the current integer-lattice sampler can omit an edge
pixel on an x/y flip. Pixel-center sampling can change a few fractional or
reflected results from the current experimental bitmap implementation, so land
it only as an explicit, golden-tested affine behavior correction and apply it
consistently to bitmap plots and sprites. If compatibility review rejects that
change, derive sign-aware open/closed bounds for the legacy integer lattice
rather than mixing the two conventions.

The current generic transformed blitters also perform a full float 3x3
multiplication for every output pixel. A shared affine scanline kernel should
instead calculate the inverse source position once at the left edge and add two
constant deltas across the row. That both accelerates software sprites and
creates the arithmetic model needed for native hardware sprites. Repeated float
addition is not automatically bit-identical to independent multiplication near
sample boundaries; use fixed point, periodic rebasing, or explicitly accept and
golden-test that numerical change.

## Buffer mutation and inverse-cache correctness

Live reference semantics require a content-generation mechanism for buffer
IDs. Increment a generation after every successful operation that creates,
replaces, clears, writes, adjusts, copies into, or otherwise mutates an ID. A
binding records the generation from which its snapshot was prepared; mutation
marks only users of that ID dirty.

This should be centralized rather than added only to matrix commands. In
v2.16.0, `checkTransformBuffer()` appends an inverse as a second buffer block
once, while general `bufferAdjust()` can mutate the first block in place without
invalidating that cached inverse. A sprite implementation must not copy that
potentially stale second block. Either:

- key the inverse cache by content generation and rebuild it after every
  mutation; or
- move inverse caching out of the user-visible `BufferVector` into internal
  metadata.

The latter is cleaner, but a generation-tagged second block is a smaller
change. Cache creation itself must not count as a user content mutation.

Maintain a reverse `transformUsers` map analogous to `bitmapUsers`, but use it
for dirtiness notification rather than dangling-pointer ownership. A public
clear of one ID unbinds its users; clear-all unbinds all. In contrast, matrix
commands that internally build a replacement must construct it off to the side,
commit it once, preserve bindings, and bump the generation once. Treating their
intermediate `bufferClear()` as a public clear would incorrectly detach every
sprite. General copy-by-reference buffers either need block-level generations
or must be rejected as live matrix sources.

## Software-sprite implementation

Software support is the recommended first production implementation because on
Agon's paletted controllers it runs in the framebuffer drawing task rather than
the VGA output interrupt. If the `vdp-gl` API is made generic for controllers
that execute sprite drawing in a VSYNC ISR, those controllers need equivalent
IRAM/FPU treatment or must initially reject affine sprites.

### Rendering and background preservation

Prepare every candidate snapshot, clipped footprint, and required capacity
before altering the visible scene. Then, while renderer mutation is suspended:

1. Hide/restore **all** old software sprites in reverse z-order using their
   recorded `savedX`, `savedY`, width, and height.
2. Atomically publish the complete new software state set.
3. Show **all** new software sprites in ascending z-order. For each transformed
   sprite, translate its prepared local bounds by x/y, intersect the viewport,
   verify preflighted capacity, and in single-buffered modes save the complete
   clipped rectangle contiguously. This full-box representation is the simplest
   correct MVP; a later span/mask representation can also restore only modified
   pixels correctly if it preserves reverse ordering.
4. Inverse-map using the agreed sampling convention, apply format/alpha and
   paint mode, record the exact clipped footprint, and merge all old/new bounds
   into the update region.
5. Preserve the existing static-sprite rule, but mark a static sprite drawable
   before the global hide whenever its frame, position, transform generation,
   or effective renderer changes.

Never interleave “hide old sprite N, draw new sprite N” across the sprite list:
with overlaps, a later upper-sprite restore can resurrect stale lower-sprite
pixels. The existing global reverse-hide/forward-show order is part of the
compositing contract.

In double-buffered modes the current engine does not save backgrounds. That is
safe only under its existing application contract that each backbuffer is
cleared/redrawn before presentation; refresh alone does not self-erase a moving
software sprite. Preserve and document that rule. Switching a bound sprite
between software and hardware/cache can otherwise leave stale pixels in one or
both buffers, so pin the backend for the binding. Any explicit transition must
occur at an application full-redraw/swap boundary or implement independent
damage/background state for both buffers.

Background storage must use checked `size_t` arithmetic and be resized only
outside an ISR. Allocate for the clipped visible bounds, not an unbounded
off-screen transformed rectangle. Still enforce a documented per-sprite and
aggregate memory ceiling: a scale can turn a tiny frame into a viewport-sized
software overlay, and many such sprites could otherwise exhaust heap. On
preflight failure, keep the prior published state or omit the new transformed
draw—never hide the old sprite and then discover that its replacement cannot be
rendered. A grow-only capacity based on the maximum clipped transformed extent
of attached frames avoids allocation during animation; frame attach/replace,
transform change, and mode change must all re-run checked capacity planning.

### Requested versus effective hardware mode

Do not destroy the caller's hardware request merely because a transform is
temporarily active. Resolve it to an explicit backend when the binding is
activated or the video mode changes:

```text
RawHardware | CachedHardware | NativeAffineHardware | Software | Rejected
```

Pin that backend for the life of the binding unless the caller explicitly
accepts a transition at a safe redraw boundary. Cache readiness changes a
generation from pending to publishable; it does not switch a cached binding to
software. Both `showSprites()` and `drawSpriteScanLine()` consult the same
published backend so exactly one renderer draws the sprite.

Software is a documented degradation, not transparent substitution: it is
baked into the framebuffer below all hardware overlays, can change XOR/overlap
results and immediacy, and inherits the double-buffer redraw contract above.
Status must expose it, and the fallback policy must allow `Rejected` when the
caller requires hardware semantics. Clearing the transform may restore raw
hardware only at a safe presentation/redraw boundary. Mask frames and
unsupported paint modes may retain their current permanent-software behavior
for compatibility, or later adopt the same explicit backend model separately.

## Native hardware-sprite implementation

Native hardware support cannot call the existing float transformed-bitmap
primitive. `VGAPalettedController::decorateScanLinePixels()` runs in each VGA
controller's IRAM ISR, and the current hardware loop is a simple sequential
copy. A transform makes both the number of destination pixels and source access
pattern data-dependent.

If native support is pursued, use inverse affine stepping. For a destination
scanline `y` and clipped left edge `x0`, calculate once:

```text
sourceX0 = i00 * localX0 + i01 * localY + i02
sourceY0 = i10 * localX0 + i11 * localY + i12
```

Then each output pixel requires only:

```text
sourceX += i00
sourceY += i10
```

plus source bounds, alpha, and paint checks. Start values must implement the
same documented sampling lattice as software. The implementation must be
IRAM-safe, avoid allocation and DSP/float library calls, and preserve the
existing RGBA2222/RGBA8888 palette conversion and RGBA2222 XOR behavior.

Even this optimized loop is materially more expensive than the raw path: it
adds two accumulators and bounds checks per output pixel, often reads source
pixels non-sequentially, and a rotation or scale can make the destination much
wider than the source. Therefore admission cannot use sprite count, source area,
or transformed width alone. Its calibrated cost for each two-row interrupt must
include controller-specific framebuffer expansion, ordinary and transformed
hardware sprites, text/mouse reserve, both rows' destination samples, source
format and memory location, Set/XOR/alpha branches, and affine access locality.
Sequential internal-DRAM and vertical/random PSRAM reads of equal width are not
equivalent. Select cache/software/rejection before the render entry is
published; never switch backend halfway through an ISR row.

Admission with headroom is still an estimate. Before starting a native sprite,
an ISR guard should compare elapsed cycles plus that entry's validated
worst-case cost and the reserved second-row/cursor tail against the hard
deadline. If it cannot fit, omit that whole low-priority sprite for the row pair
and increment an overload counter rather than beginning a partial sprite or
missing VGA DMA. Such an omission is an emergency degradation, not normal
quality-of-service; release thresholds should make it absent in qualification
so z-order and visuals remain stable.

The recommended pre-native fallback is a renderer-private pre-rasterized frame.
It keeps the scanline loop unchanged, carries the transformed bounding-box
offset alongside the cached frame, and is especially effective when the sprite
moves frequently but its frame/matrix changes rarely. Normalize RGBA8888 to one
byte RGBA2222 with binary alpha: the current hardware path already discards all
but the top two RGB bits and treats every nonzero alpha as opaque, so this loses
no visible **Set-mode** hardware output while reducing bandwidth fourfold.
Current RGBA8888 hardware drawing ignores XOR whereas RGBA2222 applies it, so a
normalized RGBA8888 cache must force the source path's effective Set behavior or
route/reject XOR rather than accidentally enabling it.

Cache pixels, not just metadata, must satisfy the ISR's memory rules. Require an
explicit internal-DRAM cache budget for cache-off-safe use. If larger caches are
allowed in PSRAM, classify their higher/random-access cost and retain the
firmware's existing coordination that deactivates sprites while flash/PSRAM
cache is unavailable (as the updater already does); otherwise route/reject
them. The cache still costs output-area memory and regeneration time. Rapid
matrix animation should coalesce to the latest generation rather than queue
unbounded jobs. It is automatic render state, not a public bitmap ID and not
the manual one-shot `&28` contract.

Native tiers should be admitted separately: retain the identity/translation
fast path; qualify mirror and axis-aligned nearest scaling next; keep general
rotation/shear Q16.16 DDA experimental; never put bilinear or perspective work
in the ISR.

## Failure behavior and resource limits

The implementation should fail closed and remain recoverable:

- initially absent matrix: pending/untransformed; malformed, non-affine,
  singular, NaN, or infinite replacement: retain the last coherent published
  generation and expose/log stale-error status;
- fixed-point or coordinate overflow, impossible bounds, or background
  allocation failure: do not publish the candidate snapshot;
- hardware cycle/admission limit exceeded before activation: select the
  caller-permitted cache/software backend or reject; emergency ISR guard:
  omit a whole low-priority entry and count/report overload;
- source bitmap/frame removed: retain the transform binding but draw nothing,
  matching ordinary empty-sprite behavior;
- reset sprites/full reset: release background state and reset all bindings;
- mode change: rebuild clipped bounds/background capacity before the next draw.

Expose selected-sprite status—valid, pending, stale, software fallback, private
cache, native hardware, missing buffer, resource failure, or overload—from the
first experimental release that can degrade automatically. Assign the variable
through protocol review; debug logging alone is not enough for applications
whose ordering or double-buffer behavior depends on the backend.

## Repository-level change map

No files were changed, but a real implementation would have these ownership
areas:

| Repository area | Required responsibility |
| --- | --- |
| `agon-vdp/video/context.h` | Implement `0x412` read/write and optional `&96` bit-1 routing |
| `agon-vdp/video/sprites.h` | Store binding/request state; reset, dirty, and refresh semantics |
| `agon-vdp/video/buffers.h`, `vdu_buffered.h` | Content generations, inverse invalidation, transform-user notification |
| `vdp-gl/src/displaycontroller.h/.cpp` | Render snapshot, bounds helper, effective mode, transformed save/draw/restore |
| `vdp-gl/src/dispdrivers/vgapalettedcontroller.*` | Optional fixed-point native scanline renderer and admission hooks |
| `agon-docs` | `&1412`, optional `&96` bit 1, anchor, refresh, fallback, limits, and format semantics |

The feature should first live on paired firmware and `vdp-gl` branches so their
ABI/layout changes cannot become mismatched through the normal PlatformIO
dependency. Only after tests and hardware qualification should the library and
firmware changes be proposed upstream in dependency order.

## Verification and acceptance gates

### Functional reference tests

Use a tiny asymmetric image with unique corner colors and transparent holes.
Compare transformed sprite output against a host/reference inverse rasterizer
for identity, integer translation, positive and negative scale, x/y flips,
90-degree rotations, non-right-angle rotation, shear, and composed center-pivot
rotation. Cover Mask, RGBA2222, RGBA8888, every supported paint mode, and
single/double buffering.

Also exercise:

1. every screen edge and a transform whose bounds extend negative from x/y;
2. overlapping software sprites, hide/show, movement, frame-size changes, and
   exact global reverse-hide/forward-show restoration with no trails;
3. hidden and static sprites, reset, mode changes, bitmap/frame removal, and
   repeated activation/deactivation;
4. matrix mutation through every buffer-writing family, transactional
   replacement preserving a binding, public clear/recreate remaining unbound,
   invalid-to-valid transitions, and cached-inverse invalidation;
5. singular, nearly singular, NaN/infinite, huge-scale, overflow, and forced
   allocation-failure cases;
6. `&1412` read/write/clear, combined `&96` flags if implemented, and an old
   v2.16.0 parser trace proving the canonical `&F8` form does not desynchronize;
7. backend selection/status/opt-out, pinned z-order, private-cache pending and
   source-cancellation races, and safe return to hardware at a redraw boundary;
8. both physical backbuffers across movement, transform clear, backend change,
   and the documented full-redraw protocol.

Identity-transform output must be pixel-identical to the ordinary sprite path.
Bounds and background tests should use guard regions/canaries as well as visual
hashes so one-pixel overruns or stale restores are caught.

### Timing and hardware qualification

Enable or extend `FABGLIB_VGAXCONTROLLER_PERFORMANCE_CHECK` to record maximum,
not just average, ISR cycles for each complete two-row interrupt. The current
controllers prepare two logical rows per interrupt; illustrative
modeline-derived total budgets at 240 MHz are only about 30.5k cycles at
320-class double-scan,
15.3k at 640×480, and 9.9k at 1024×768. Those totals already include framebuffer
unpack/copy, cursors, every sprite test, and ISR overhead, so they are bounds to
measure against—not transform budgets. Benchmark worst cases on a
physical Agon at the highest-cost supported resolutions and color depths:
multiple overlapping sprites, full-width transformed bounds, RGBA8888 random
access, transparency, XOR, negative clipping, and matrix/frame publication near
vertical blank. Test while other firmware services are active and while flash
cache conditions vary.

Set the native admission threshold only from these measurements with explicit
headroom; a provisional target is to reserve 20–30% of the measured two-row
deadline until longer soak data justifies otherwise. Exercise the elapsed-cycle
guard and verify deterministic whole-entry omission/counters under forced
overload. Acceptance requires no missed DMA deadlines, visible tearing,
flicker, audio/input regression, heap growth, or coefficient/frame mismatch
during long-running animation. Emulator screenshots are useful functional
evidence but cannot qualify ESP32 ISR timing; any future emulator-related change
also remains subject to the repository's explicit human-validation gate.

## Delivery decision

The recommended definition of “restriction removed” is:

> Any sprite may bind a live affine matrix and render correctly. Firmware may
> use a private transformed hardware frame or, when policy permits, a
> status-visible pinned software backend when native affine scanout is
> unsupported or outside its measured budget.

That can be delivered without putting an inverse affine sampler in the VGA ISR,
although the cache/snapshot selection still requires small, qualified ISR-side
changes. If the stronger requirement is “retain on-the-fly hardware rendering
under arbitrary affine transforms,” the fixed-point scanline phase is
additionally required and should remain experimental until real-hardware timing
data proves it.

## Primary source anchors

- Reserved sprite transform variable and bitmap-transform counterpart:
  [`video/context.h`](https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/context.h#L915-L938)
- VDP-variable routing and current clear behavior:
  [`video/vdp_variables.h`](https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/vdp_variables.h#L20-L24)
  and
  [`clearVDPVariable`](https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/vdp_variables.h#L263-L304)
- Existing affine command gate and payload order:
  [`video/vdu_sys.h`](https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/vdu_sys.h#L260-L271)
- Sprite state and software-forcing precedents:
  [`video/sprites.h`](https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/sprites.h#L87-L102)
  and
  [`setSpritePaintMode`](https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/sprites.h#L234-L254)
- Existing unversioned inverse cache:
  [`video/buffers.h`](https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/buffers.h#L160-L181)
- Sprite layout and software save/draw/restore:
  [`src/displaycontroller.h`](https://github.com/AgonPlatform/vdp-gl/blob/ac2dd5986daf496c43ae8e7fe41836274aec54a0/src/displaycontroller.h#L651-L689)
  and
  [`src/displaycontroller.cpp`](https://github.com/AgonPlatform/vdp-gl/blob/ac2dd5986daf496c43ae8e7fe41836274aec54a0/src/displaycontroller.cpp#L652-L758)
- Current per-pixel float transformed rasterizer:
  [`src/displaycontroller.h`](https://github.com/AgonPlatform/vdp-gl/blob/ac2dd5986daf496c43ae8e7fe41836274aec54a0/src/displaycontroller.h#L2785-L2885)
- Timing-critical direct hardware-sprite loop:
  [`src/dispdrivers/vgapalettedcontroller.cpp`](https://github.com/AgonPlatform/vdp-gl/blob/ac2dd5986daf496c43ae8e7fe41836274aec54a0/src/dispdrivers/vgapalettedcontroller.cpp#L404-L499)
- Two-row VGA64 ISR and frame-boundary notification:
  [`src/dispdrivers/vga64controller.cpp`](https://github.com/AgonPlatform/vdp-gl/blob/ac2dd5986daf496c43ae8e7fe41836274aec54a0/src/dispdrivers/vga64controller.cpp#L706-L759)
- Existing OTA protection that deactivates hardware sprites:
  [`video/updater.h`](https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/updater.h#L56-L59)
- Official reference semantics and reserved affine flag bits:
  [`System-Commands.md`](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/vdp/System-Commands.md#L334-L353)
