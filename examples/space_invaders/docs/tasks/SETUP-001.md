# SETUP-001 — Establish the agondev build baseline

## State

- Status: Completed
- Started: 2026-08-22 03:14 EDT
- Finished: 2026-08-22 03:24 EDT

## Intent

Replace the extraction-only ASMX build with a reproducible `agondev` build
that can assemble a minimal MOS application in `ADL=0`, while retaining the
downloaded source and checksum as an immutable comparison baseline.

## Scope

This task owns assembler discovery, syntax probes, build entry points, output
layout, listings, and byte-level comparison tooling. It does not port game
logic or choose a display backend.

## Implementation gate

Document the installed `agondev` command, supported source dialect, binary
format, and invocation before rewriting the extracted assembly.

## Work

- [x] **SETUP-001-W01 — Inventory agondev:** Record its executable, version,
  syntax, include handling, listing support, and raw/MOS binary output.
- [x] **SETUP-001-W02 — Build a probe:** Assemble and inspect a minimal
  `ADL=0` MOS application with a valid header, entry, and clean return.
- [x] **SETUP-001-W03 — Define source layers:** Keep the downloaded ASMX file
  unchanged and establish a separate agondev port source tree or a
  deterministic conversion stage.
- [x] **SETUP-001-W04 — Replace the build:** Make the normal target use
  `agondev`, emit a listing/map where available, and reject unexpected output
  size or placement.
- [x] **SETUP-001-W05 — Add build validation:** Check deterministic output,
  MOS header fields, execution mode, entry address, and source provenance.

## Dependencies and references

- [ADR-0001](../decisions/ADR-0001-execution-baseline.md)
- Preserved source: `../../src/invaders.asm`
- Implemented build: `../../Makefile`

## Decisions and assumptions

`agondev` and `ADL=0` are accepted. Runnable code is a checked-in GNU
Z80/eZ80-syntax source layer under `src/agon/`; the ASMX reconstruction remains
an immutable reference.

## Unresolved questions

None. The probes established that agondev cannot assemble the ASMX/Intel
source directly, so a checked-in Z80-syntax translation is required. The
accepted image links at logical zero, reserves the MOS name/header prefix, and
starts runnable code at `0x0045`.

## Affected implementation

`Makefile`, the port source tree, build checks, and README build
instructions.

## Validation gates

1. Clean build succeeds using only documented project dependencies.
2. A listing proves `ADL=0` code generation and intended addresses.
3. The extracted source checksum remains unchanged.

## Outcome

The agondev 1.0 build produces a validated 77-byte `ADL=0` MOS probe, listing,
and map. Two clean builds produced identical binary, object, listing, and map
hashes. The probe initializes the Z80-mode stack, returns success in `HL`, and
uses `RET.LIS` to cross back to the MOS caller. Full evidence and invocation
details are recorded in [the build baseline](../agondev.md) and the
[2026-08-22 development log](../development/2026-08-22.md).
