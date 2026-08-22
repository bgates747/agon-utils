# ADR-0001 — agondev and ADL=0 execution baseline

- Status: Accepted
- Completeness: Complete
- Date: 2026-08-22
- Related tasks: SETUP-001, PORT-001

## Context

The preserved source targets Intel 8080 hardware and ASMX. Agon’s eZ80 can run
Z80-compatible code in `ADL=0`, preserving 16-bit register, stack, and address
semantics more closely than a 24-bit ADL translation. The project’s intended
assembler toolchain is agondev rather than ASMX or ez80asm.

## Decision

1. Use agondev as the target assembler for the runnable Agon port.
2. Execute the adapted game code in eZ80 `ADL=0` mode.
3. Preserve the downloaded ASMX source unchanged as provenance and comparison
   evidence; place translated or adapted code in a separate source layer.
4. Use explicit mixed-mode boundaries only where MOS, a video driver, or
   24-bit memory access requires them.

## Consequences

The port still requires a MOS-compatible header and entry/exit boundary,
resolution of low-address/RST-vector conflicts, and explicit access to any
24-bit framebuffer or driver structure. Source conversion must remain
traceable to the preserved original.
