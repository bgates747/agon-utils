# Independent register capture controls

expected.json defines 52 controls: for each of two seeds, one preserving control,
15 single-byte mutations (all bytes of BC/DE/HL/IX/IY), one A mutation, eight
individual F-bit mutations and one post-return SP+3 injection. These are synthetic
assembly tests, not MOS conformance cases. Source is apps/capture-controls/src.

The shared capture implementation lives in apps/runner/src/capture.asm and is
included by the qualification app. agents/check_capture.py observes CPU state at
the first instruction of each capture entry point, independently reads SRAM,
normalizes the debugger's SP by the known three-byte capture-call return address,
and compares both actual register values and explicitly expected mutation deltas.
It then verifies guards across all unused onboard SRAM. Deliberate reporting
clobbers occur after capture but before SRAM inspection.

Limits: ADL/MB0 only; MB and ADL values checked in that mode, not across mode
changes. IFF validity is clear, alternate registers omitted. SP offset is injected
after a returning synthetic action, not via an unsafe corrupted RET. The probe
borrows the caller's stack for a balanced AF save; it does not yet use the reserved
capture stack. Normal interrupts remain enabled; nested/user concurrent capture
is unsupported. Backend is emulator only; hardware remains to be checked.
