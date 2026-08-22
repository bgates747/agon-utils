# ADR-0002 — Direct GPIO video architecture

- Status: Accepted
- Completeness: Complete
- Date: 2026-08-22
- Related tasks: ARCH-001, HARDWARE-001, VIDEO-001, TIMING-001

## Context

The original machine keeps a packed 7,168-byte 1-bit framebuffer that is both
display memory and collision state. Dedicated board logic reads and serializes
that memory while the 8080 executes game code. A complete 60 Hz transfer of
the buffer through Agon's UART exceeds its 8N1 payload capacity before VDU
protocol overhead.

Tom Morton's direct eZ80 GPIO driver instead supplies a 320×240 RGB332 15 kHz
mode at approximately 60 Hz. It avoids UART presentation bandwidth but owns
Timer 1 and the GPIO scanout interval, leaving application execution largely
to the vertical interval. The original electrical raster fits as a centered
256×224 image.

## Decision

1. Use the direct eZ80 GPIO driver and its mode 8 as the only display backend
   for this project. Stock-VDP sparse updates and pseudo-scanout are deferred.
2. Keep the original packed 1-bit framebuffer authoritative for drawing,
   collision, shield damage, and player-state behavior. Maintain a separate
   RGB332 presentation shadow incrementally; do not expand every pixel every
   frame.
3. Present the raw centered 256×224 electrical raster and physically rotate
   the display into the original 224×256 portrait orientation. Do not transpose
   it in software.
4. Run official MOS v3.0.2 with the application-bundled, position-fixed static
   GPIO driver copied to `0x0b8000` and called directly. Rainbow MOS and its
   reset-vector extension are not dependencies. Stock VDP firmware remains
   available independently for normal console output.
5. Preserve the two original interrupt phases as ordered scheduler phases once
   per GPIO frame. Observe the driver's frame counter and run game work during
   application time without installing a competing Timer 1 handler. Restrict
   the pre-image callback to bounded signaling or pointer swaps.

## Consequences

The physical adapter and a 15 kHz-capable display are required. Emulator
qualification proves integration and raster mapping but not electrical signal
quality or the real application-cycle budget. HARDWARE-001 owns physical
qualification and TIMING-001 owns measured cadence, margin, jitter, and
overruns.

Every write affecting the packed framebuffer needs a coherent presentation
strategy. VIDEO-001 must favor changed-byte, span, or dirty-region expansion
and demonstrate that its cost fits beside game logic. The original framebuffer
continues to determine collision outcomes even if the RGB332 shadow is a frame
behind while being updated.
