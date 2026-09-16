# Prepare a selection — not a test run

From the Linux project root:

```sh
./human/mos-tests plan --list
./human/mos-tests plan --output .emulator/plans/first --backend emulator group:controls
./human/mos-tests runner-build
```

Use a fresh directory. The plan command saves the catalogue, exact selection,
declared backend/capabilities and a planning receipt. It does not run cases or
claim passes. Function and exact-case selectors use function:NAME and case:ID;
all selects the current catalogue. Unknown names/empty selections fail before
creating output. Overlapping selectors form a stable union in catalogue order.

Only synthetic controls are registered at this stage. Without proven capabilities,
omit --capability; missing capabilities are listed rather than guessed. Hardware
selection is a plan declaration, not deployment or hardware qualification. An
optional --script records script identity only: script parsing/execution arrives
in W06. Do not describe this command as the future editable boot workflow.

Production capture, SD checkpointing, real case execution and reports remain
pending. Current executable smoke testing is [documented separately](emulator.md).
