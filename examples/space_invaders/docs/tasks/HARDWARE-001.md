# HARDWARE-001 — Build and qualify the GPIO video adapter

## State

- Status: Not started
- Started: --
- Finished: --

## Intent

Build a reversible GPIO-to-VGA resistor adapter and qualify the upstream
framebuffer project independently of the Space Invaders port.

## Scope

This task owns component inventory, schematic transcription, safe assembly,
continuity checks, upstream example execution, display compatibility, signal
stability, and recovery. It does not wire or power hardware automatically.

## Implementation gate

Record the exact Agon model, connector pinout, monitor/scaler capability,
component values, unpowered test procedure, and recovery path in the ignored
`HARDWARE.local.md`. Obtain Author approval before flashing firmware or
powering newly assembled wiring.

## Work

- [ ] **HARDWARE-001-W01 — Inventory:** Confirm the target is an Agon Light
  1/2-compatible GPIO layout and identify the VGA display or scaler.
- [ ] **HARDWARE-001-W02 — Source components:** Verify two 75 Ω, three 510 Ω,
  three 1 kΩ, and two 2 kΩ resistors, connector, ground, and insulated wiring.
- [ ] **HARDWARE-001-W03 — Assemble unpowered:** Build the RGB332 ladder and
  HSYNC/VSYNC paths from the authoritative upstream wiring.
- [ ] **HARDWARE-001-W04 — Inspect electrically:** Check resistor values,
  continuity, shorts, GPIO-to-ground resistance, and connector orientation.
- [ ] **HARDWARE-001-W05 — Choose firmware path:** Prefer the static driver on
  current stock MOS for initial qualification unless evidence requires a
  custom MOS.
- [ ] **HARDWARE-001-W06 — Run upstream examples:** Establish stable sync,
  colour ordering, 320×240 at 60 Hz, frame progression, and clean recovery.
- [ ] **HARDWARE-001-W07 — Record evidence:** Capture adapter revision,
  schematic, component measurements, mode results, and observed limitations.

## Dependencies and references

- [vga-ez80 wiring and timing](https://github.com/tomm/vga-ez80#what-about-the-wiring-to-a-vga-port)
- [EZ80 Framebuffer Agon](https://github.com/tomm/ez80-framebuffer-agon)
- [ARCH-001](ARCH-001.md)

## Decisions and assumptions

The adapter is a candidate experiment, not yet the accepted project display
backend. The upstream project explicitly targets Agon Light 1/2 hardware.

## Unresolved questions

1. Does the available display accept the 15 kHz 320×240 signal reliably?
2. Can it be safely and practically operated in the cabinet-style rotated
   orientation?
3. Is GPIO audio desired on the first adapter revision?

## Validation gates

1. Unpowered checks pass before connection.
2. The upstream test image is stable for a sustained run.
3. RGB channels, sync polarity, refresh rate, and recovery are documented.
4. No firmware identity is changed without a recoverable backup and approval.
