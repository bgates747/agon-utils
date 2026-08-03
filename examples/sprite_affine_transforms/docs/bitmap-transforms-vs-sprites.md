# Why Agon bitmap matrix transforms do not apply to sprites

Status: verified technical précis, 2026-08-02. This is a static source and
history analysis; no firmware, emulator, or hardware behavior was changed or
tested.

## Executive conclusion

Steve Sims is correct about **live** matrix transforms: the affine matrix
selected for normal bitmap drawing is graphics-context state consumed by one
specific bitmap drawing function. It is not an attribute of the bitmap's pixel
data. When that same bitmap is attached to a sprite, the sprite retains only a
plain `Bitmap *`; neither the matrix ID nor the matrix follows it.

Both sprite renderers then bypass the transformed-bitmap drawing function:

1. A software sprite is redrawn with the ordinary axis-aligned bitmap blitter,
   which also saves and restores an untransformed rectangular background.
2. A hardware sprite is copied directly from the raw frame into each outgoing
   VGA scanline.

There is therefore no transform state for either renderer to consult.

The important qualification is buffered operation 40 (`&28`), **Create a
transformed bitmap**. It applies a matrix once and materializes the result as a
new RGBA2222 bitmap. That new bitmap can be attached to a sprite because the
transformation is already baked into its pixels. This is a practical workaround,
but it is not a live matrix transform on a sprite.

## Source baseline

The conclusion was checked against:

- canonical `agon-vdp` at
  `c7ac293d2aa81ddfa693390549bcd909069c8fc3`, exactly tag `v2.16.0`;
- its installed `vdp-gl` `all-the-plots` dependency at
  `ac2dd5986daf496c43ae8e7fe41836274aec54a0`; and
- canonical `agon-docs` at
  `f9806bd3cbff6ed5d1c08bef1d51fed11764b86b`.

The `agon-vdp` worktree was clean. All local heads, remote-tracking refs, tags,
commit diffs, messages, and Git notes were searched; no local ref implements a
sprite transform.

## The architectural split

| Operation | State carried to the renderer | Render path | Live selected matrix used? |
| --- | --- | --- | --- |
| Bitmap `PLOT` (`&E8`-`&EF`) | `Context::bitmapTransform`, bitmap, position | Canvas `DrawTransformedBitmap` primitive | Yes |
| Immediate bitmap command `VDU 23,27,3` | The same `Context` state | The same `Context::drawBitmap` function | Yes in v2.16.0 source |
| Software sprite | Raw frame `Bitmap *`, x/y, paint and visibility state | `showSprites` → `absDrawBitmap` | No |
| Hardware sprite | Raw frame `Bitmap *`, x/y, paint and visibility state | VGA scanline decorator → direct pixel copy | No |
| Bitmap made by buffered operation `&28` | Already transformed RGBA2222 pixels | Either ordinary sprite path | No live matrix; transformed appearance is baked in |

### 1. The matrix belongs to drawing state, not to `Bitmap`

Buffered affine operation `&20` constructs a row-major 3×3 float matrix in a
buffer. The system command

```text
VDU 23,0,&96,flags,matrixBufferId;
```

does not modify a bitmap. With flag bit 0 set, it merely stores the buffer ID in
`Context::bitmapTransform`. Bits 1-7 are reserved, and the implementation tests
only bit 0.

A FabGL `Bitmap` contains width, height, format, mask colour, and a pixel-data
pointer. It has no transform member. FabGL instead defines a separate
`BitmapTransformedDrawingInfo` payload containing a bitmap pointer, forward
matrix, and inverse matrix for the one transformed draw operation.

This distinction is the core reason for Steve's answer: a transformed plot is a
render-time operation on otherwise unchanged bitmap pixels.

### 2. A normal bitmap plot explicitly selects the transformed renderer

For bitmap `PLOT` codes, the call chain is:

```text
VDU 25 / PLOT &E8-&EF
    → Context::plot
    → Context::plotBitmap
    → Context::drawBitmap
    → Canvas::drawTransformedBitmap
    → DrawTransformedBitmap primitive
```

`Context::drawBitmap` looks up `bitmapTransform`, validates the referenced
matrix buffer, ensures that an inverse is cached, and submits both matrices with
the bitmap to the Canvas. The display controller transforms the four corners to
obtain a destination bounding box, then inverse-maps destination pixels back to
the source bitmap.

Changing the matrix changes subsequent bitmap plots because this lookup happens
for each draw. It still does not change or decorate the source `Bitmap` object.

### 3. Attaching a bitmap to a sprite loses the drawing context

`addSpriteFrame(bitmapId)` resolves the ID to a bitmap and calls:

```cpp
sprite->addBitmap(bitmap.get());
```

The FabGL `Sprite` holds x/y, an array of `Bitmap *` frames, frame indexes,
saved-background fields, paint options, and visibility/hardware flags. It holds
no bitmap ID, transform ID, forward matrix, inverse matrix, pivot, or transformed
bounds. Activating sprites hands that array directly to `vdp-gl` with
`setSprites`.

Consequently, a later sprite refresh cannot recover the `Context` that happened
to be current when the frame was attached, and there is no per-sprite transform
to apply.

### 4. The software-sprite renderer is a separate untransformed blitter

Software sprites are framebuffer overlays with background preservation. For
each frame, `vdp-gl`:

1. allocates saved-background storage from the frame's untransformed
   `width * height`;
2. saves the axis-aligned rectangle at sprite x/y;
3. calls `absDrawBitmap` on the raw frame; and
4. records the same raw width and height so that the rectangle can later be
   restored.

This path neither enters `Context::drawBitmap` nor submits a Canvas primitive.
The existing transformed primitive cannot simply replace this call: it hides
sprites before drawing, does not capture a transformed background, and can
produce a bounding box larger than or offset from the source dimensions.

### 5. The hardware-sprite renderer is even further removed

Hardware sprites are not painted into the framebuffer. During VGA signal
generation, `VGAPalettedController::rawDrawSpriteScanline` takes the raw frame
width and height, derives a source row from `scanRow - spriteY`, and advances
linearly through RGBA8888 or RGBA2222 source pixels. It has no matrix inputs and
performs no coordinate mapping.

This direct loop is in the timing-critical output path. The normal transformed
bitmap implementation performs floating-point 3×3 inverse mapping over the
destination pixels and is a queued framebuffer primitive; it cannot be reused
as a hardware-sprite scanline decorator.

## Evidence that this is a known support boundary

The history makes the scope unusually explicit:

1. Steve's commit
   [`5ddf8890`](https://github.com/AgonPlatform/agon-vdp/commit/5ddf8890cbbb2bf1286f3faa78a6ad6c03120fe5)
   is titled **"add command to set a transform on bitmap plots"**. It added the
   `Context` member, `VDU 23,0,&96`, and the conditional call inside
   `Context::drawBitmap`. PR 222 was titled **"Transformed bitmap plots"** and
   the feature shipped in VDP 2.9.0.
2. The official command documentation assigns flag bit 0 to bitmap drawing and
   reserves bits 1-7. The PLOT documentation likewise promises the feature for
   bitmap plots, not sprites.
3. Steve's later commit
   [`e598a27e`](https://github.com/AgonPlatform/agon-vdp/commit/e598a27e380a64d7e90ebc985d50c264d3174af0)
   added adjacent context-variable slots for bitmap and sprite state. The source
   contains the literal comment:

   ```cpp
   // case 0x412: // Current sprite transform ID - not supported
   ```

   That comment is unchanged in every release from VDP 2.12.0 through 2.16.0.
   Official variable documentation exposes bitmap transform `0x1402` and sprite
   ID/count `0x1410`/`0x1411`, but no sprite transform at `0x1412`.

This shows a knowingly unsupported API boundary, not merely a transform call
that was accidentally omitted from one sprite command. It does not prove that a
future sprite-transform implementation was planned.

## What works now: bake transformed sprite frames

Buffered operation 40 decimal (`&28` hexadecimal), added by Steve in
[`8665b985`](https://github.com/AgonPlatform/agon-vdp/commit/8665b9850fb9cd1d61dff5665996d71306240adb),
uses this protocol shape:

```text
VDU 23,0,&A0,targetBitmapId; &28,options,matrixId;sourceBitmapId; [width;height;]
```

It inverse-samples the source into a new one-byte-per-pixel RGBA2222 buffer and
registers an ordinary bitmap with `targetBitmapId`. That ID can then be attached
to the current sprite with the 16-bit-ID command:

```text
VDU 23,27,&26,targetBitmapId;
```

RGBA2222 is valid for both software and hardware sprites. For a rotation or
shear whose result should not be clipped to the original dimensions, options
value `5` combines resize (`&01`) with automatic translation (`&04`). Multiple
derived IDs can be attached as animation frames to provide discrete rotated or
scaled variants.

Practical constraints are:

1. This is nearest-neighbour rasterization into RGBA2222, so RGBA8888 colour
   and alpha channels are reduced from eight bits to two; sprite rendering
   still treats every nonzero alpha value as opaque.
2. Each variant consumes its own output-width × output-height bytes of PSRAM,
   plus bitmap bookkeeping.
3. Automatic translation makes sprite x/y refer to the transformed bounding
   box's top-left. Differently sized rotation frames can appear to wobble around
   a desired pivot unless the caller uses common padded dimensions or adjusts
   positions.
4. Generate target bitmaps before attaching them. Replacing a buffer/bitmap ID
   already used by a sprite invokes `clearBitmap`, which clears that sprite's
   entire frame list; regeneration is not a transparent live update.

No emulator or hardware timing measurements were made, so this report does not
claim that generating transformed frames every display frame is performant.
The implementation does a matrix calculation for every output pixel, making
precomputed variants the conservative use.

## Why native live sprite transforms require renderer work

Passing a matrix ID into `Sprite` would solve only the first plumbing problem.
A complete feature has materially different requirements for the two sprite
types.

For software sprites, the renderer would need transformed bounds and pivot
semantics, background allocation using those bounds, save/restore at the
transformed offset, inverse-sampled drawing with sprite paint modes, and correct
update rectangles. The current transformed bitmap routines have no background
capture parameter.

For hardware sprites, `vdp-gl` would need a new scanline compositor that clips
against transformed bounds and maps output x/y to source coordinates within the
VGA timing budget. A safe implementation would also need a stable matrix and
inverse snapshot because the VDU processor can mutate or clear buffers while
the scanline renderer is running. Full floating-point matrix multiplication per
output pixel would be a poor fit for the existing tight direct-copy loop; an
incremental or fixed-point implementation, or pre-baked frames, would be the
likely design space.

At the firmware/API level, a design must also decide whether transforms are
global, per sprite, per frame, or snapshotted when a frame is attached; how a
matrix update affects a visible sprite; and what point is the sprite's anchor.
The existing bitmap transform is one `Context`-wide setting, so those semantics
do not already exist.

## Incidental documentation discrepancy

Official bitmap documentation says the legacy one-shot command
`VDU 23,27,3,x;,y;` does not obey bitmap-plot transforms. In the inspected
v2.16.0 source it calls `Context::drawBitmap`, the same function that applies
`bitmapTransform`, so static analysis says it does obey the selected transform.
That command still draws a bitmap once; it is not an active sprite-render path
and does not alter the conclusion above.

## Bottom line

The most precise reading of Steve's statement is:

> A matrix selected for live bitmap/PLOT drawing does not apply to sprites,
> because it is Context/Canvas draw state rather than Bitmap or Sprite state,
> and both sprite renderers bypass the transformed draw primitive.

The supported low-risk alternative is to use buffered operation `&28` to bake
one or more transformed RGBA2222 bitmaps, then use those bitmap IDs as sprite
frames.

## Primary sources

- Firmware transform state and render selection:
  [`video/context/graphics.h`](https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/context/graphics.h#L857-L898)
- Explicit unsupported sprite-transform variable:
  [`video/context.h`](https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/context.h#L922-L938)
- Sprite frame attachment and activation:
  [`video/sprites.h`](https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/sprites.h#L87-L164)
- Baked transformed-bitmap implementation:
  [`video/vdu_buffered.h`](https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/vdu_buffered.h#L2044-L2182)
- FabGL bitmap, transformed-draw payload, and sprite layouts:
  [`src/displaycontroller.h`](https://github.com/AgonPlatform/vdp-gl/blob/ac2dd5986daf496c43ae8e7fe41836274aec54a0/src/displaycontroller.h#L527-L689)
- Software-sprite draw path:
  [`src/displaycontroller.cpp`](https://github.com/AgonPlatform/vdp-gl/blob/ac2dd5986daf496c43ae8e7fe41836274aec54a0/src/displaycontroller.cpp#L652-L758)
- Hardware-sprite scanline path:
  [`src/dispdrivers/vgapalettedcontroller.cpp`](https://github.com/AgonPlatform/vdp-gl/blob/ac2dd5986daf496c43ae8e7fe41836274aec54a0/src/dispdrivers/vgapalettedcontroller.cpp#L409-L499)
- Official affine-transform command scope:
  [`System-Commands.md`](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/vdp/System-Commands.md#L334-L353)
- Official bitmap and sprite architecture:
  [`Bitmaps-API.md`](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/vdp/Bitmaps-API.md#L129-L159)
- Official baked-transform operation:
  [`Buffered-Commands-API.md`](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/vdp/Buffered-Commands-API.md#L718-L735)
