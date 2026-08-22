# INPUT-001 — Adapt cabinet controls, coin handling, and tilt input

## State

- Status: Not started
- Started: --
- Finished: --

## Intent

Map Agon keyboard input onto the original cabinet input ports without changing
the game’s debounce, credit, player-selection, or movement logic.

## Scope

Implement keyboard polling/events and synthesized 8080 input-port values for
coin, start, left, right, fire, tilt, and cabinet configuration switches.

## Work

- [ ] **INPUT-001-W01 — Map ports:** Document every original input bit,
  polarity, DIP switch, and consumer.
- [ ] **INPUT-001-W02 — Select keys:** Define stable keyboard mappings for
  coin, one/two player start, movement, fire, tilt, and exit.
- [ ] **INPUT-001-W03 — Integrate input source:** Use the selected display
  path’s MOS or GPIO-driver keyboard contract without competing ownership.
- [ ] **INPUT-001-W04 — Emulate port reads:** Return correct active levels and
  preserve the original game’s own debounce behavior.
- [ ] **INPUT-001-W05 — Validate:** Exercise held keys, simultaneous keys,
  coin limits, both players, focus loss, and clean exit.

## Dependencies and references

- [PORT-001](PORT-001.md)
- [ARCH-001](ARCH-001.md)
- GPIO video `pollkeyboardevent` API when that backend is selected

## Unresolved questions

1. Whether physical GPIO controls are a later optional profile.
2. Which DIP-switch defaults best represent the intended cabinet configuration.

## Validation gates

All original input-port consumers receive deterministic values and the attract
mode remains functional with no input.
