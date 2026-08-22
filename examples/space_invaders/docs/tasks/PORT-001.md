# PORT-001 — Adapt the original 8080 program to an Agon ADL=0 application

## State

- Status: Not started
- Started: --
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

- [ ] **PORT-001-W01 — Map incompatibilities:** Inventory Intel 8080 syntax,
  undocumented assumptions, I/O instructions, RST vectors, ROM/RAM addresses,
  stack setup, interrupts, and self-modifying behavior.
- [ ] **PORT-001-W02 — Define layout:** Resolve the original `0000–3FFF`
  address assumptions against the MOS header, loader, MBASE, and application
  memory contract.
- [ ] **PORT-001-W03 — Establish adapter symbols:** Replace direct hardware
  dependencies with narrow named interfaces while retaining original call
  sites wherever practical.
- [ ] **PORT-001-W04 — Convert incrementally:** Assemble address-bounded
  sections and compare generated opcodes or control flow against the baseline.
- [ ] **PORT-001-W05 — Reach inert execution:** Start, initialize RAM, execute
  the main loop with stub hardware adapters, and exit or halt diagnostically.

## Dependencies and references

- [SETUP-001](SETUP-001.md)
- [ARCH-001](ARCH-001.md)
- [ADR-0001](../decisions/ADR-0001-execution-baseline.md)

## Decisions and assumptions

The port targets agondev and `ADL=0`. The preserved extraction is evidence,
not the file to rewrite in place.

## Unresolved questions

1. Whether to preserve original numeric addresses through bank placement or
   relocate labels and data.
2. Whether original interrupt entry code remains linked for comparison or is
   replaced by explicit scheduler entry points.

## Validation gates

1. Every changed hardware dependency resolves through a documented adapter.
2. Listings contain no unintended ADL-mode instruction widths.
3. Original ROM data and translated code remain traceable by label/address.
