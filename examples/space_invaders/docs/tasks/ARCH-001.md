# ARCH-001 — Select the video and timing architecture

## State

- Status: Not started — candidate architectures identified
- Started: --
- Finished: --

## Intent

Select the display, framebuffer representation, orientation, and timing
boundaries before game-specific video or interrupt adaptation begins.

## Scope

Compare the stock VDP buffered-bitmap path with direct eZ80 GPIO video. Define
which framebuffer is authoritative, how the rotated cabinet image is
presented, and how the original two 60 Hz interrupt phases interact with the
selected scanout system.

## Implementation gate

Stop after a bounded comparison and Author review. Promote accepted material
decisions into an ADR and `docs/architecture.md` before implementation.

## Work

- [ ] **ARCH-001-W01 — Verify source contracts:** Record the original 256×224,
  1-bit framebuffer layout, rotated-monitor mapping, 60 Hz refresh, two
  interrupts per frame, shift-register behavior, and collision dependency.
- [ ] **ARCH-001-W02 — Characterize VDP path:** Measure or bound UART payload,
  sparse buffer updates, bitmap redraw cost, VSync behavior, and rotation.
- [ ] **ARCH-001-W03 — Characterize GPIO path:** Confirm available 60 Hz modes,
  CPU budget, RGB332 layout, frame callbacks, interrupt ownership, keyboard
  polling, audio facilities, and current-MOS integration.
- [ ] **ARCH-001-W04 — Prototype critical risk:** Use the smallest program
  needed to prove the chosen candidate can present a stable 256×224 test
  raster with correct orientation and enough application time.
- [ ] **ARCH-001-W05 — Decide and document:** Present the decision register,
  obtain Author acceptance, write the ADR, and update the architecture.

## Dependencies and references

- [Computer Archeology Space Invaders analysis](https://computerarcheology.com/Arcade/SpaceInvaders/)
- [EZ80 Framebuffer Agon](https://github.com/tomm/ez80-framebuffer-agon)
- [vga-ez80](https://github.com/tomm/vga-ez80)
- Official Agon VDP buffered-command and bitmap documentation
- [HARDWARE-001](HARDWARE-001.md)

## Task précis

A complete original monochrome framebuffer is 7,168 bytes. At 60 Hz it would
require 430,080 bytes/s before VDU overhead, exceeding the 1,152,000-baud
UART's theoretical 8N1 payload ceiling. Sparse VDP-side deltas remain viable,
but full scanline streaming does not.

The GPIO project offers a 320×240 60 Hz 15 kHz mode into which the original
unrotated 256×224 raster fits. Its scanout framebuffer is RGB332, not the
original packed 1-bit format, and full-resolution scanout consumes most eZ80
time. These are the critical feasibility questions.

## Decision register

- [ ] **ARCH-001-D001 — Display backend:** GPIO framebuffer, stock VDP sparse
  updates, or a staged implementation supporting both.
- [ ] **ARCH-001-D002 — Authoritative framebuffer:** Preserve the original
  packed 1-bit buffer with a presentation shadow, or replace the renderer.
- [ ] **ARCH-001-D003 — Orientation:** Physically rotate a compatible display,
  transpose in software, or transform in the selected display backend.
- [ ] **ARCH-001-D004 — GPIO integration:** Current stock MOS plus static
  driver, custom Rainbow MOS, or another reviewed integration boundary.
- [ ] **ARCH-001-D005 — Timing boundary:** True scan-phase callbacks,
  frame-level emulation with double buffering, or another measured scheme.

## Validation gates

1. Bandwidth and CPU conclusions have measured or source-backed evidence.
2. The chosen mode displays a stable correctly proportioned raster.
3. Interrupt ownership and MOS compatibility are explicit.
4. An accepted ADR closes all five decisions before dependent implementation.
