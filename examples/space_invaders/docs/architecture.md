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

## Compatibility objective

Preserve recognizable original code, data, gameplay timing, collision
behavior, and the packed 1-bit framebuffer model wherever the selected Agon
hardware permits. Original cabinet hardware dependencies are isolated behind
named video, timing, input, shift-register, and audio adapters.

## Display architecture

No display backend is accepted yet. The stock VDP sparse-update design and the
direct GPIO framebuffer design are candidates. GPIO video is particularly
promising because its 320×240 60 Hz 15 kHz mode can contain the original
unrotated 256×224 raster, but RGB332 expansion, CPU availability, interrupt
ownership, monitor compatibility, and orientation require qualification.
[ARCH-001](tasks/ARCH-001.md) owns these decisions.
