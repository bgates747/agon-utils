# When startup finds an interrupted run

Startup checks recovery state before creating another run or executing a test.
If the previous run is unfinished, or its journal/evidence is damaged, it stops
with **INCOMPLETE**. Rebooting again does not retry the case.

## Inspect without running tests

At the MOS prompt, using a newly prepared recovery-enabled bundle:

```text
LOAD /mos-tests/runner.bin
RUN . inspect
```

Inspection reads retained evidence without allocating a run or changing the
journal. READY means the gate permits another run; it is not a test pass.
INCOMPLETE reports the last established phase/case and confirmed failures.
An interruption does not prove that the test caused a reset.

The usual host command remains:

```sh
./human/mos-tests startup --bundle /path/to/bundle --output /fresh/output
```

It boots the actual autoexec workflow. This command may run tests if recovery
permits them; use the manual inspect command for inspection only. A blocked boot
returns status 2 from the host command (target startup status 41). Its result.json
contains the target recovery_gate decision; journal/allocation bytes and previous
run reports are retrieved alongside SRAM and debugger transcripts. No fresh run
is manufactured to label the restart successful.

## Preserve the stopped installation

Keep the entire image/card and run directories. Do not delete the journal,
reset install.bin, overwrite the card with a new bundle or edit original results
to make the gate proceed. Copy evidence for investigation.

Explicit park/retry/continuation tools are MAIN-05 W03 and are not implemented
yet. An unresolved installation therefore remains stopped. You can prepare a
separate fresh image for independent development; this does not recover or
acknowledge the original run.

Older bundles lack the recovery gate. Newly built runners reject missing journals
instead of silently migrating old installations. W02 supports canonical manifests
from the same synthetic bundle and its three qualified control cases. Equivalent
but differently serialized manifests, different builds, disposition receipts and
parent-linked runs may be valid evidence for the host reporter but remain
unsupported for automatic startup. Limits are in the recovery contract. W02
also caps each hashed artifact at 1 MiB and total hashed bytes at 64 MiB per
inspection; JSON artifacts retain the 16 KiB bound. Exceeding a bound stops.

## Qualify the gate

From the Linux subproject root:

```sh
./human/mos-tests recovery-check --output .emulator/recovery/new-check
```

Run this sequentially with other emulator checks. It exercises independent native
wire/transition controls, clean/repeated boots, interrupted/repeated-blocked boots,
case-entry interruption, retained failures, inspection, and damaged state on raw
images. Wider interrupted-write/disposition qualification remains W04.

Hardware has not been tested. These controlled process stops do not establish
power-loss durability or arbitrary crash recovery. Capture SRAM before resetting
when possible; restart recovery relies on SD evidence.
