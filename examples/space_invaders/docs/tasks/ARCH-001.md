# ARCH-001 — Select the video and timing architecture

## State

- Status: Complete — direct GPIO architecture accepted in ADR-0002
- Started: 2026-08-22 03:41 EDT
- Finished: 2026-08-22 04:39 EDT

## Intent

Select the display, framebuffer representation, orientation, and timing
boundaries before game-specific video or interrupt adaptation begins.

## Scope

Qualify direct eZ80 GPIO video for this port. Define which framebuffer is
authoritative, how the rotated cabinet image is presented, and how the
original two 60 Hz interrupt phases interact with direct scanout. Stock VDP
and pseudo-scanout work are explicitly deferred to a possible later project.

## Implementation gate

Stop after a bounded comparison and Author review. Promote accepted material
decisions into an ADR and `docs/architecture.md` before implementation.

## Work

- [x] **ARCH-001-W01 — Verify source contracts:** Record the original 256×224,
  1-bit framebuffer layout, rotated-monitor mapping, 60 Hz refresh, two
  interrupts per frame, shift-register behavior, and collision dependency.
- [x] **ARCH-001-W02 — Retire VDP path:** Bound full-frame UART bandwidth and
  defer VDP sparse-update or pseudo-scanout experiments outside this project.
- [x] **ARCH-001-W03 — Characterize GPIO path:** Confirm available 60 Hz modes,
  CPU budget, RGB332 layout, frame callbacks, interrupt ownership, keyboard
  polling, audio facilities, and current-MOS integration.
- [x] **ARCH-001-W04 — Prototype critical risk:** The Author verified two
  Rainbow/resident-driver runs and a corrected stock-MOS/static-driver run of
  `gpio-raster.bin`. The stock run proves a stable 256×224 test raster with
  correct centering and orientation markers without custom MOS. Physical
  output and application-cycle measurement transfer to HARDWARE-001 and
  TIMING-001 respectively.
- [x] **ARCH-001-W05 — Decide and document:** The Author accepted the complete
  decision register; ADR-0002 and the accepted architecture record it.

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

- [x] **ARCH-001-D001 — Display backend:** Direct GPIO VGA using Tom's eZ80
  framebuffer implementation. VDP alternatives are not part of this port.
- [x] **ARCH-001-D002 — Authoritative framebuffer:** Preserve the original
  packed 1-bit buffer with a separately maintained RGB332 presentation shadow.
- [x] **ARCH-001-D003 — Orientation:** Physically rotate a compatible display,
  using a centered 256×224 raw raster without software transposition.
- [x] **ARCH-001-D004 — GPIO integration:** Official MOS v3.0.2 plus the
  application-bundled static driver at `0x0b8000`. Rainbow MOS is not a
  project dependency.
- [x] **ARCH-001-D005 — Timing boundary:** Run the two original phases in
  order once per GPIO frame during application time. Do not compete for Timer
  1 or run game logic inside the visible scanout callback.

## Validation gates

1. Bandwidth and CPU conclusions have measured or source-backed evidence.
2. The chosen mode displays a stable correctly proportioned raster.
3. Interrupt ownership and MOS compatibility are explicit.
4. Accepted ADR-0002 closes all five decisions before dependent implementation.

## Current evidence

- [Original machine contract](../original-machine-contract.md)
- [Direct GPIO video contract](../gpio-video-contract.md)
- [GPIO raster probe](../gpio-raster-probe.md)

The emulator display gate passed twice with Rainbow/resident-driver setup and
once with the accepted official-MOS/static-driver setup by Author observation
on 2026-08-22. The remaining W04 evidence requires the physical adapter and a
timing probe.
