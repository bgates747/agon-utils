# When startup finds an interrupted run

Startup checks recovery state before allocating another run or executing a test.
Unfinished execution or damaged evidence stops with **INCOMPLETE**. Rebooting
does not retry a case. Keep the entire image/card and saved run directories.
Never clear the journal or reset install.bin to bypass the gate.

## Inspect first

At the MOS prompt, with the runner from that installation:

```text
LOAD /mos-tests/runner.bin
RUN . inspect
```

This reads evidence without changing the journal or allocating a run. READY
means another run is permitted; it is not a test pass. An interruption does not
establish what caused it. Capture SRAM before resetting when possible.

On Linux, from the subproject root:

```sh
./human/mos-tests startup --bundle /path/to/bundle --output /fresh/inspection
```

This boots the actual autoexec workflow and **can execute tests** if the gate
permits them. Use the MOS inspect command for read-only inspection. A blocked
boot returns host status 2 (target 41). The output contains journals, allocation
state, retained runs, recovery receipts, reports, SRAM and debugger transcripts.
Read result.json: recovery_gate.run_id identifies the subject and
recovery_gate.journal_generation supplies the expected generation for a request.
A null generation requires investigation; do not guess or reset it.

## Choose an explicit disposition

- **park** acknowledges and preserves the subject but keeps startup stopped.
- **retry** authorizes an explicit selection from the original plan, including
  previously completed cases.
- **continue** authorizes an explicit selection of cases without a valid CASE_END.
  A completed failed case must be retried explicitly; continuation cannot select it.

There is no default selection or automatic retry. Confirm fixture prerequisites
before retry/continue. These commands currently support the synthetic controls;
they do not establish real MOS or hardware coverage.

Example emulator request (replace the values with those from your stopped image):

```sh
./human/mos-tests recover \
  --bundle /path/to/stopped-bundle --output /fresh/park-request \
  --action park --run-id YOUR_32_DIGIT_RUN_ID --generation CURRENT_GENERATION \
  --actor "your name" --reason "Preserve this interruption for investigation"
```

After parking, use the **new** generation in
applied/execution/result.json for any subsequent request. To authorize one
remaining synthetic case:

```sh
./human/mos-tests recover \
  --bundle /path/to/stopped-bundle --output /fresh/continue-request \
  --action continue --run-id YOUR_32_DIGIT_RUN_ID --generation CURRENT_GENERATION \
  --case control.ix-upper.001 --prerequisites-confirmed \
  --actor "your name" --reason "Prerequisites checked; run the remaining case"
```

Repeat --case for explicit selections in catalogue order. Use --action retry
when deliberately re-running a completed case. The helper writes request.json
and, for execution, the selected autoexec.txt. It temporarily boots RUN . recover,
collects its evidence and restores the original !boot.obey. It leaves the selected
autoexec.txt deployed. **ARMED** means authorization was accepted, not that the
selected tests ran. Start the normal startup command separately to consume it.

A rejected request returns host status 2 (target 44). Preserve the output and
inspect the reason; never assume preparation or a receipt file alone means
acceptance. A stale request cannot be replayed. If the host itself is killed
before restoration, recover the original !boot.obey from the action output;
the stale generation prevents silently repeating a completed disposition.

## Manual card/emulator use

Omit --bundle to prepare files only. PREPARED performs no target action.
Copy request.json to /mos-tests/request.json and, if present, autoexec.txt to the
card root. Keep the existing installation and original run directories. Then:

```text
LOAD /mos-tests/runner.bin
RUN . recover
```

Observe PARKED or ARMED before any normal boot/run. For a manual-only inspection,
the validated journal generation is the little-endian 64-bit field at offset16
in the newer valid 256-byte recovery-a.bin/recovery-b.bin slot; retain both files
for host inspection. Raw bytes are not permission to repair a corrupt pair.
Hardware deployment/recovery is documented for future use and remains unqualified.

## What is retained

The original run is immutable. Recovery saves both journal snapshots, a JSON
receipt with actor/reason/selection and evidence hashes, and a separate acceptance
certificate. An authorized child receives a new run ID, parent link and its own
bound disposition.json. Child pass counts exclude parent outcomes: an incomplete
or failed parent remains incomplete or failed.

An interruption during disposition stays stopped. For a valid identified subject
with readable evidence, a fresh explicit request at the current generation may
acknowledge preserved orphan disposition files. Interrupted child allocation
consumes authorization and stays stopped; it is not silently retried. Corrupt
journal pairs, malformed/truncated record tails, allocation gaps, ambiguous identity and legacy installations
have no repair/migration tool in this implementation.

The supported profile uses canonical manifests from the same runner bundle and
three synthetic controls. Limits include 16 KiB JSON, 1 MiB per hashed artifact,
64 MiB aggregate hashing, 64 accepted receipts, 256 recovery files and 200 evidence
entries per receipt. Combined limits may stop earlier than any individual maximum.
Do not delete older evidence to get around a limit. JSON actor/reason accepts UTF-8;
bounded target parsing supports ASCII Unicode escapes, so use literal UTF-8 for
non-ASCII text.

## Qualification

Run emulator checks sequentially:

```sh
./human/mos-tests recovery-check --output .emulator/recovery/new-check
./human/mos-tests disposition-check --output .emulator/disposition/new-check
```

The second covers explicit park/retry/continuation, rejected requests, receipt
tampering, child linkage and controlled interruption during disposition and child
allocation. MAIN-05 W04 owns the broader individual write/sync/close boundary sweep.
Controlled debugger stops and next boots do not establish CPU-reset causation,
physical card power-loss atomicity or hardware behavior.
