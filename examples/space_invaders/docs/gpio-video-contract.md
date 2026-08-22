# Direct GPIO Video Contract

## Reference revisions

The architecture was inspected against:

- EZ80 Framebuffer Agon commit
  `882ef1a04ea923d354a14f9cafb74bc82c46eeb9` (2026-08-13); and
- `vga-ez80` commit `000f67f14fa80147dd32cf68be5b7656050fd6b0`
  (2026-08-11).

The static driver in both checkouts is 8,395 bytes with SHA-256
`a4234409ca9fd9479c3e2be7c717824e6196dc033ec3073149ebc72a6486a946`.

## Accepted mode

Driver mode 8 is the only supplied mode that directly contains the original
electrical raster without scaling or dropping lines:

| Mode | Logical pixels | Scan behavior | Flags | Suitability |
| ---: | ---: | --- | --- | --- |
| 6 | 320×120 | Alternating scanline grille | 15 kHz, 60 Hz | Too few source rows |
| 7 | 320×120 | 2× vertical scan | Slow, 15 kHz, 60 Hz | Too few source rows |
| 8 | 320×240 | One source row per scanline | Slow, 15 kHz, 60 Hz | Accepted probe mode |

Mode 8 leaves 32 pixels on each horizontal side and eight scanlines above and
below a centered 256×224 raster. Scanout is one byte per pixel in RGB332.

The 15 kHz implementation uses 262 lines of 1,176 eZ80 cycles. At 18.432 MHz
that is approximately 59.82 frames/s. Its 240-line visible section executes as
one non-yielding interrupt body. Application code can run principally during
the 22 blank lines: an upper bound of 25,872 raw eZ80 cycles per frame, or
8.4% of the CPU before handler and callback overhead. This is the principal
performance risk and requires hardware or cycle-accurate-emulator measurement.

## Driver ownership

The driver:

- owns PRT Timer 1 and rewrites its RAM interrupt vector;
- disables the normal UART0 receive interrupt and polls UART during scanout;
- disables the Agon VDP vertical-blank interrupt while active;
- owns GPIO C bits 0-7 for RGB332;
- owns GPIO D bits 6 and 7 for VSYNC and HSYNC;
- optionally owns GPIO D bit 5 for one-bit audio; and
- reenables UART and VDP interrupts when `videostop` runs.

Game timing therefore cannot install another Timer 1 handler. Code must not
hold interrupts disabled. The original two phases should initially run in
order once per increment of `frame_counter`, during the vertical-blank CPU
window, rather than adding callbacks in the visible scanout loop.

## API boundary

The public setup structure exposes a frame counter, 24-bit framebuffer
pointer, 24-bit scanline-offset-array pointer, and an ADL-mode pre-image
callback. The callback runs in interrupt context immediately before visible
scanout and must return with `RETI.LIL`; it should set flags or swap pointers,
not run game logic or expand a full frame.

The driver also supplies keyboard events through its polled UART path and a
256-byte, one-bit audio ring. In a 262-line 60 Hz mode, the scanline audio path
is approximately 15.7 ksample/s.

## Integration and memory baseline

The upstream Tetris example proves stock-MOS operation by copying the static
driver to `0x0b8000` and calling its ADL API there. This is the preferred
integration because it is application-local and does not require a firmware
change. The raster probe now uses this path and has passed under official MOS
v3.0.2; the Rainbow reset-vector extension is neither required nor used.

The current probe memory plan is non-overlapping:

| Region | Purpose |
| --- | --- |
| logical `0x0000-0xffff` in the MOS load bank | ADL=0 program, original RAM, packed 1-bit framebuffer |
| `0x080000-0x092bff` | 320×240 RGB332 presentation framebuffer |
| `0x0b0000-0x0b02cf` | 240 24-bit scanline offsets |
| `0x0b8000-0x0ba0ca` | Upstream static driver |

## Presentation consequence

The original packed framebuffer must remain authoritative because gameplay
reads it for collision and shield state. A distinct RGB332 presentation
shadow is therefore required. Full-frame expansion of 57,344 source pixels
inside an 8.4% CPU window is not credible; VIDEO-001 must update the shadow
incrementally or through bounded dirty tracking.
