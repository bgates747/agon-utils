# PORT-001 — Adapt the original 8080 program to an Agon ADL=0 application

## State

- Status: In progress — opcode-exact agondev translation
- Started: 2026-08-22 05:32 EDT
- Finished: --

## Intent

Create an agondev-assembled `ADL=0` port that preserves recognizable original
game code and data while supplying the MOS application boundary and explicit
hardware adapters.

## Scope

This task owns source translation, address organization, entry/exit, register
and flag compatibility, low-memory/RST conflicts, RAM layout, and adapter
call boundaries. Video, timing, input, and audio implementations remain in
their dedicated tasks.

## Implementation gate

Complete SETUP-001 and approve an address map before bulk source conversion.

## Work

- [x] **PORT-001-W01 — Map incompatibilities:** Inventory Intel 8080 syntax,
  undocumented assumptions, I/O instructions, RST vectors, ROM/RAM addresses,
  stack setup, interrupts, and self-modifying behavior.
- [x] **PORT-001-W02 — Define layout:** Resolve the original `0000–3FFF`
  address assumptions against the MOS header, loader, MBASE, and application
  memory contract.
- [x] **PORT-001-W03 — Establish adapter symbols:** Replace direct hardware
  dependencies with narrow named interfaces while retaining original call
  sites wherever practical.
- [ ] **PORT-001-W04 — Convert incrementally:** Assemble address-bounded
  sections and compare generated opcodes or control flow against the baseline.
- [x] **PORT-001-W05 — Reach inert execution:** Start, initialize RAM, execute
  the main loop with stub hardware adapters, and exit or halt diagnostically.

## Dependencies and references

- [SETUP-001](SETUP-001.md)
- [ARCH-001](ARCH-001.md)
- [ADR-0001](../decisions/ADR-0001-execution-baseline.md)

## Decisions and assumptions

The port targets agondev and `ADL=0`. The preserved extraction is evidence,
not the file to rewrite in place. The first correctness proof uses an
independently ASMX-assembled, byte-identical original ROM as the executable
core and an agondev-assembled test harness. This avoids introducing a syntax
translation as a confounding variable.

The proof establishes an all-short layout in the MOSlet's existing bank:
the launch header at `0000` is disposable, the loader runs above `8000`, and
it copies the original ROM to `0000-1fff`. Original RAM remains `2000-3fff`
and the proof harness occupies `4000`. No MBASE change or mixed-mode game code
is required.

The adapter proof uses a single address-preserving `RST 0` ABI for all 42
executable original I/O instructions. Typed descriptors distinguish IN from
OUT while retaining each two-byte footprint. See
[the I/O adapter contract](../io-adapter-contract.md).

The stock-firmware emulator run reached a stable adapter/init PASS. Original
initialization, packed status rendering, both sound-off writes, and an explicit
`DrawSprite` shift-register vector completed before the terminal diagnostic.
Packed framebuffer output is intentionally not presented by this proof.

The first W04 slice translates seven routines and matches all 121 emitted
agondev bytes against their original ASMX ROM ranges. The repeatable method
and syntax map are recorded in
[the translation strategy](../translation-strategy.md); W04 remains open for
the rest of the ROM.

## Unresolved questions

1. Whether original interrupt entry code remains linked for comparison or is
   replaced by explicit scheduler entry points.

## Validation gates

1. Every changed hardware dependency resolves through a documented adapter.
2. Listings contain no unintended ADL-mode instruction widths.
3. Original ROM data and translated code remain traceable by label/address.
