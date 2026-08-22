# Space Invaders Project Instructions

Read the repository `AGENTS.md` and the canonical Agon development guidance
before working in this subproject. This file contains only Space
Invaders-specific workflow rules.

## Project management

`TODO.md` is this project's single authoritative list of unfinished work.
Every TODO item must have one corresponding tracked detail file at
`docs/tasks/<TASK-ID>.md`. Keep implementation steps, research, dependencies,
open decisions, and validation gates in the detail file rather than expanding
the TODO entry.

Accepted architecture belongs in `docs/architecture.md` and an ADR under
`docs/decisions/`. Open questions remain in their owning task. Record accepted,
rejected, completed, or superseded work in the current dated file under
`docs/development/` before removing it from the TODO.

## Technical authorities

1. Use the extracted `src/invaders.asm` as the preserved upstream source
   baseline. Keep porting changes distinguishable from that extraction.
2. `agondev` is the target assembler and eZ80 Z80-compatible `ADL=0` is the
   accepted application execution mode.
3. Consult official Agon documentation before changing MOS, GPIO, interrupt,
   or firmware contracts.
4. Treat `ez80-framebuffer-agon`, `vga-ez80`, official Agon checkouts, and
   other repositories outside `mystuff` as read-only references.
5. Record machine-local bench inventory, device identity, wiring state, and
   deployment paths in ignored `HARDWARE.local.md`, not tracked task files.

## Hardware and emulator gates

Do not flash firmware, power new wiring, or alter a physical target as an
implicit part of a software task. Resolve the exact board, adapter revision,
wiring, recovery path, and validation procedure first. Emulator-related
changes remain uncommitted until the Author completes the canonical human
validation gate.
