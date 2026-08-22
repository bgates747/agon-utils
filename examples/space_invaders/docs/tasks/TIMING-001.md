# TIMING-001 — Reproduce the original 60 Hz split-interrupt timing

## State

- Status: Not started
- Started: --
- Finished: --

## Intent

Preserve gameplay speed and task ordering derived from the original mid-screen
and end-screen interrupts while coexisting with MOS and the selected display
driver.

## Scope

This task owns the two 60 Hz phases, interrupt or callback integration, main
loop coordination, frame counters, dropped-frame policy, and timing
instrumentation. It does not own rendering algorithms.

## Implementation gate

The selected video driver’s interrupt ownership and callback contract must be
verified from documentation and source before installing any handler.

## Work

- [ ] **TIMING-001-W01 — Inventory original phases:** Map every task and game
  object to the original mid-screen or end-screen entry.
- [ ] **TIMING-001-W02 — Define scheduler contract:** Specify phase timing,
  reentrancy, register preservation, interrupt enable rules, and overruns.
- [ ] **TIMING-001-W03 — Integrate safely:** Implement the accepted callback,
  polling, or driver-hook mechanism without competing for Timer 1.
- [ ] **TIMING-001-W04 — Instrument cadence:** Measure both phase frequencies,
  execution time, jitter, frame completion, and missed deadlines.
- [ ] **TIMING-001-W05 — Tune against behavior:** Verify player shot speed,
  alien cadence, shot reloads, saucer timing, and attract-mode delays.

## Dependencies and references

- [ARCH-001](ARCH-001.md)
- [VIDEO-001](VIDEO-001.md)
- Computer Archeology game-timing analysis

## Decisions and assumptions

The original display refresh is 60 Hz. Each of its two interrupt handlers runs
60 times per second; they are not alternating handlers at 30 Hz each.

## Validation gates

1. Measured phase cadence is 60 Hz within the selected hardware tolerance.
2. No display-driver interrupt or MOS-owned vector is corrupted.
3. Timing remains stable under worst-case active gameplay.
