# Original Machine Contract

This is the port-facing contract extracted from the preserved source and the
Computer Archeology analysis. It records behavior the Agon adapters must
preserve, not every detail of the Midway board.

## Display memory and orientation

The game treats `0x2400-0x3fff` as its framebuffer. The region is 7,168 bytes:
224 rows of 32 bytes, or a 256×224 one-bit electrical raster. Within that raw
raster, byte offset `n` and bit `b` map as:

```text
raw_x = (n mod 32) * 8 + b       b = 0..7, least-significant bit first
raw_y = floor(n / 32)            n = address - 0x2400
```

The arcade CRT is physically rotated. After rotation the player sees a
224×256 portrait image. Keeping the 256×224 electrical raster and physically
rotating the target display therefore avoids a software transpose.

The source advances by 32 bytes to move one raw-raster row. `ClearScreen`
clears exactly `0x2400-0x3fff`; startup places the stack immediately below it
at `0x2400`.

## Framebuffer semantics

The packed framebuffer is game state, not merely presentation. Drawing code
reads existing screen bytes, collision routines AND sprites with them, shield
damage is retained in them, and multiplayer shield state is copied to and
from them. The port must keep those reads coherent even if scanout uses a
separate RGB332 buffer.

The board's external 16-bit shift register converts arbitrarily aligned sprite
bytes into adjacent framebuffer bytes:

- output port `2` selects the shift amount;
- output port `4` shifts a new byte into the register; and
- input port `3` reads the selected eight-bit window.

This behavior must become a software primitive or an equivalent sequence;
ordinary eZ80 rotate instructions alone do not model the retained adjacent
byte in the hardware register.

## Timing contract

The board supplies two restart interrupts per video frame:

- vector `0x08` (`RST 1`) near raw scanline 96; and
- vector `0x10` (`RST 2`) at raw scanline 224 / vertical blank.

Each handler runs 60 times per second. They are two phases of every frame, not
alternating 30 Hz callbacks. The handlers partition game-object work based on
the object's unrotated Y high bit so the original renderer updates memory away
from the CRT beam. The mid-screen phase also processes the player and advances
alien/object work; the end-screen phase owns coin handling, delay counters,
fleet/saucer timing, and the complementary object half.

The port may schedule both phases during the GPIO driver's vertical blank,
but it must preserve their order and once-per-frame cadence. Exact raster-phase
execution is not required for collision correctness if the packed buffer
remains authoritative and RGB presentation is isolated.

## Source anchors

The preserved `src/invaders.asm` supplies the fixed interrupt vectors,
`RunGameObjs`, `CnvtPixNumber`, `DrawSprite`, `DrawSprCollision`,
`CompYToBeam`, and `ClearScreen` behavior summarized above. The source remains
checksum-pinned and is not modified by this document.
