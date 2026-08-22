# VIDEO-001 — Present the original framebuffer through the selected display path

## State

- Status: Not started
- Started: --
- Finished: --

## Intent

Display the game framebuffer at the original update cadence without changing
collision semantics or introducing visible tearing.

## Scope

Implement the presentation adapter selected by ARCH-001, including packed
1-bit interpretation, orientation, colour treatment, dirty-region handling or
RGB332 expansion, framebuffer placement, and buffer swaps.

## Implementation gate

ARCH-001-D001 through D005 must be accepted. If GPIO video is selected,
HARDWARE-001 must establish a stable reference display before final timing
claims.

## Work

- [ ] **VIDEO-001-W01 — Specify mapping:** Document the exact mapping from
  original address/bit to displayed x/y and colour.
- [ ] **VIDEO-001-W02 — Place buffers:** Allocate authoritative and
  presentation buffers without conflicting with MOS, the video driver, stack,
  game RAM, or port code.
- [ ] **VIDEO-001-W03 — Implement conversion/update:** Add the selected
  packed-to-display conversion, sparse update, or scanout mechanism.
- [ ] **VIDEO-001-W04 — Synchronize presentation:** Swap or expose frames only
  at the accepted timing boundary.
- [ ] **VIDEO-001-W05 — Verify canonical scenes:** Compare attract screen,
  rack, player, shields, shots, saucer, text, and explosions.

## Dependencies and references

- [ARCH-001](ARCH-001.md)
- [HARDWARE-001](HARDWARE-001.md)
- [PORT-001](PORT-001.md)

## Unresolved questions

1. Whether cabinet overlay colours are represented, approximated, or deferred.
2. Whether conversion is performed per changed byte, span, scanline, half
   frame, or complete frame.

## Validation gates

1. Pixel mapping and orientation pass a deterministic pattern test.
2. Collision reads continue to observe the original packed framebuffer.
3. Sustained gameplay shows no tearing or missed presentation deadlines.
