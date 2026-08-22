# Space Invaders Port Architecture

This document contains accepted architecture only. Open questions and
implementation work belong in `TODO.md` and `docs/tasks/`.

## Source lineage

`src/invaders.asm` is the checksum-pinned extraction of David Levy’s ASMX
reconstruction. It remains unchanged as the upstream baseline. Runnable Agon
sources live under `src/agon/` so mechanical translation, platform
adapters, and intentional game changes can be distinguished.

## Execution baseline

The target assembler is agondev. Adapted game code runs in the eZ80’s
Z80-compatible `ADL=0` mode from a zero-based logical image with a MOS header
at file offset `0x40`. Calls into MOS or 24-bit driver state use narrow,
explicit mixed-mode adapters. See
[ADR-0001](decisions/ADR-0001-execution-baseline.md).

The emulator correctness proof keeps the original `0000-3fff` machine map
intact without changing MBASE: a disposable MOS launch stub transfers to an
agondev loader above `8000`, which installs the byte-identical original ROM at
`0000-1fff`. Original RAM and packed video memory retain `2000-3fff`.

## Compatibility objective

Preserve recognizable original code, data, gameplay timing, collision
behavior, and the packed 1-bit framebuffer model wherever the selected Agon
hardware permits. Original cabinet hardware dependencies are isolated behind
named video, timing, input, shift-register, and audio adapters.

## Display architecture

Direct GPIO VGA using Tom's eZ80 framebuffer implementation is the accepted
display backend. This project will not implement stock-VDP sparse updates or
UART scanline streaming; pseudo-scanout may be explored as a separate future
project.

The driver's 320×240 60 Hz 15 kHz mode can contain the original 256×224
raster. Official MOS v3.0.2 with Tom's application-bundled static driver at
`0x0b8000` is the accepted firmware integration; Rainbow MOS is not required.
The original packed 1-bit framebuffer remains authoritative game state. An
incrementally maintained RGB332 shadow at `0x080000` supplies mode-8 scanout;
full-frame conversion is not part of the design. A centered 256×224 raw raster
is shown without software transposition and the physical display is rotated to
the original portrait orientation.

The GPIO driver owns Timer 1 and performs visible scanout without yielding.
The port therefore observes the driver's frame counter and runs the original
mid-screen phase followed by its end-screen phase once per frame during
application time. The pre-image callback may set flags or swap pointers but
must not run game logic. Physical output and timing margin remain qualification
work under HARDWARE-001 and TIMING-001. See
[ADR-0002](decisions/ADR-0002-direct-gpio-video.md).
