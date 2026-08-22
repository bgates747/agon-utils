# AUDIO-001 — Adapt the original sound-port behavior

## State

- Status: Not started
- Started: --
- Finished: --

## Intent

Translate writes to the original discrete-sound control ports into an Agon
audio implementation while preserving trigger edges and gameplay timing.

## Scope

Inventory sound bits, define edge/level behavior, select GPIO 1-bit audio or
VDP audio, prepare legally usable/generated samples or synthesis, and connect
the adapter to original output instructions.

## Implementation gate

Do not choose the audio backend until ARCH-001 establishes whether the stock
VDP remains available and whether the GPIO adapter includes audio output.

## Work

- [ ] **AUDIO-001-W01 — Map outputs:** Record every original sound-port bit,
  transition behavior, and game event.
- [ ] **AUDIO-001-W02 — Select backend:** Compare GPIO 1-bit ring-buffer audio,
  stock VDP audio, and deliberately deferred sound.
- [ ] **AUDIO-001-W03 — Create assets/voices:** Generate or source compliant
  sound representations with explicit provenance.
- [ ] **AUDIO-001-W04 — Implement adapter:** Preserve rising/falling edge,
  looping, stop, and overlap behavior.
- [ ] **AUDIO-001-W05 — Validate:** Check all effects, fleet rhythm, saucer
  tone, overlap, latency, and long-run buffer stability.

## Dependencies and references

- [ARCH-001](ARCH-001.md)
- [PORT-001](PORT-001.md)
- GPIO video audio ring-buffer API when applicable

## Validation gates

Sound does not perturb the 60 Hz scheduler or corrupt GPIO video timing.
