# MAIN-02 — Scaffold human and agent tooling entry points

## Summary

Create clear human and agent entry points over shared suite capabilities. Humans
start in `human/` for emulator and hardware tools and instructions. Agents start
in `agents/`, reuse human tools where suitable, and add automation only where
needed. Hardware remains authoritative for real-machine behavior; emulator
qualification is also a useful independent result.

## State

Reconstructed contract checkpoint. Completed items: none.
Remaining work is frozen and unstarted at this checkpoint. The subproject TODO
owns unfinished task indexing. This is a retrospective grouping, not an exact
previous edit version or a backdated acceptance record.

## Work

- W01 [ ] Audit the existing maintained and task-local helpers and instructions.
  Map each to human entry points, shared implementation, agent-specific tooling
  or historical evidence. Identify reusable operations and promotion candidates,
  including their dependencies and existing validation. Do not treat every
  experimental runner as mature or duplicate it merely to populate a directory.
- W02 [ ] Create the audience entry points and navigation.
  Make the most prominent usage direction in the root README a link telling
  humans to start in human/README.md. Create human/README.md with distinct
  emulator and hardware routes and agents/README.md with agent workflow and
  links to shared human operations. Link AGENTS.md to the agent entry point.
  Clearly distinguish working procedures from planned capabilities; do not
  invent hardware instructions or imply hardware qualification has occurred.
- W03 [ ] Expose the existing qualified operations through human-facing tools.
  Provide runnable front ends under human/ using existing maintained helpers
  and appropriately promoted mature code. Keep fixtures, deployment primitives,
  result semantics and comparison logic in one shared implementation. Preserve
  provenance for promoted task experiments. Use explicit arguments, meaningful
  exit codes and saved results; make interactive requirements explicit so an
  agent can invoke the same operations without duplicating them. Hardware
  support that needs design or equipment verification remains visibly pending.
- W04 [ ] Add agent guidance and validate the scaffold.
  Document prerequisite checks, backend selection, tool invocation, evidence
  interpretation and cleanup. Link to human instructions rather than copying
  them. Add agent-only automation only where it provides a distinct capability.
  Verify navigation and available front ends, using proportionate checks and
  the existing qualified baseline. Record backend and evidence limitations;
  update handoff and document remaining work without claiming suite coverage.


## Interface priority

Follow the accepted [test strategy](../test-strategy.md). W02/W03
should make the editable autoexec.txt workflow the first human interface, before
any menu application. Verify startup chaining and comment/LOAD/RUN syntax; the
current !boot.obey workaround must remain. Planned capabilities are labelled as
such until implemented and validated. On-device helper apps are C++ targeting
AgonDev. Reuse shared function selection and execution; do not build a separate
test engine for a future menu. MAIN-01 W03 owns detailed runner design.

## Structure and ownership

1. `human/`: usable human front door, instructions and runnable front ends for
   emulator and hardware. Initially unsupported routes must say what is missing.
2. `agents/`: agent entry point, training/workflow guidance and any unique
   automation. Reuse human tools and shared primitives.
3. Maintained shared locations such as `scripts/`, source and fixtures: one
   implementation of common behavior. W01 chooses placement based on existing
   structure; avoid premature reorganizations or a second toolchain environment.
4. `docs/tasks/MAIN-02/`: bounded scaffolding trials and promotion notes. Routine
   operation must not depend on this historical task directory.

## Acceptance criteria

1. A human can find the human directory immediately from the root README and
   distinguish emulator and hardware routes, prerequisites and support status.
2. An agent can follow its own entry point and reuse the same human tools,
   with no duplicate implementation or competing instructions for shared work.
3. Existing qualified operations remain reproducible; wrappers correctly expose
   errors and preserve results. Planned hardware capability is not presented as
   implemented or validated.
4. Results identify target firmware and execution backend. Hardware authority
   does not erase the independent value of emulator qualification; neither
   result is silently substituted for the other.
5. Headless emulator use and raw SD images with !boot.obey remain the baseline.
   Finding a discrepancy authorizes documentation clarification, not a firmware
   behavior change. Upstream publication still requires separate authorization.
6. All project work remains on Linux with the existing top-level .venv. Stable
   subtask IDs and supporting evidence survive promotion and task closure.

## References

- [MAIN-01 strategy](MAIN-01.md)
- [Build guide](../build.md)
- [Setup results](../test-results.md)
- [Task conventions](README.md)
