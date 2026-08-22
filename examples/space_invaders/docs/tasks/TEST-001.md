# TEST-001 — Qualify gameplay fidelity, timing, and hardware operation

## State

- Status: Not started
- Started: --
- Finished: --

## Intent

Establish repeatable evidence that the port builds, boots, displays, controls,
sounds, and plays like the original within explicitly accepted differences.

## Scope

Define static, emulator, electrical, visual, timing, gameplay, soak, and
physical-hardware validation. Preserve exact artifact and fixture identities
for accepted runs without storing private bench details in tracked files.

## Implementation gate

Do not claim physical qualification from emulator output. Emulator-related
changes require the canonical Author validation gate before commit.

## Work

- [ ] **TEST-001-W01 — Static checks:** Validate source provenance, agondev
  output, memory layout, forbidden direct hardware operations, and adapter
  coverage.
- [ ] **TEST-001-W02 — Deterministic fixtures:** Establish known framebuffer,
  input, timing, score, collision, and sound-trigger scenarios.
- [ ] **TEST-001-W03 — Emulator checks:** Use the approved profile only for
  behavior it actually models and retain human visual evidence.
- [ ] **TEST-001-W04 — Hardware checks:** Qualify sync, orientation, controls,
  frame cadence, CPU margin, audio, and recovery on the physical target.
- [ ] **TEST-001-W05 — Gameplay and soak:** Complete attract mode, one-player,
  two-player, rack transition, game-over, tilt, high activity, and extended
  runtime tests.
- [ ] **TEST-001-W06 — Acceptance record:** Document accepted deviations,
  artifact hashes, procedure identity, results, and Author approval.

## Dependencies and references

All preceding TODO items.

## Validation gates

1. Clean checkout builds reproducibly.
2. Original gameplay cadence and collision behavior pass defined fixtures.
3. Physical hardware supplies final video and timing evidence.
4. The Author explicitly accepts the qualified result and deviations.
