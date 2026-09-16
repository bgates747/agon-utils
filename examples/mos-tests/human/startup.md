# Run the editable startup bundle

The startup bundle now runs the three synthetic foundation controls through a
real `!boot.obey` → `EXEC /autoexec.txt` chain. Edit function groups in autoexec.txt;
the Agon runner derives the selected plan before execution, saves results early
and often, and retains every run separately. Real MOS function cases come later.

## Prepare and run on the Linux emulator

From /home/smith/Agon/mystuff/agon-utils/examples/mos-tests:

```sh
./human/mos-tests bundle --output .emulator/my-bundle
./human/mos-tests startup --bundle .emulator/my-bundle --output .emulator/my-run
```

Both output directories must be new. `bundle` builds the C++ AgonDev helper and
prepares a copyable sdcard/ tree plus a verified raw sd.img. `startup` launches
headlessly through the profile wrapper, waits for return to the MOS prompt,
retrieves card results and SRAM, runs the shared reporter, and closes the emulator.
The qualification observer uses unlimited CPU (`-u`); it makes no timing claim.

Default coverage is two passed synthetic controls plus one unsupported UART
fixture control, so the correct report is **NO FAILURES OBSERVED — coverage
limited**. To get an all-pass run of the available controls, disable the UART
function group. A test expecting the IX upper-bit change passes when that exact
change is observed; this is not an undetected preservation failure.

The `startup` command returns the current report's status: 0 all-pass, 1 test
failures, 2 incomplete/infrastructure error, 3 limited coverage. Earlier runs
retrieved from the same image remain separately reported. Inspect the named
report-<run-id>/summary.txt and report.json. Execution failure is never inferred
as success merely because the emulator exited normally.

## Edit selections

Prepare your own autoexec.txt from a generated example, then build a new image:

```sh
./human/mos-tests bundle --script /path/to/edited-autoexec.txt \
  --output .emulator/selected-bundle
```

On a copied physical card you can edit /autoexec.txt directly before boot. Keep
the begin and finalize pairs. Comment out or delete **both** lines of an unwanted
function group, for example:

```text
LOAD /mos-tests/runner.bin
RUN . begin

LOAD /mos-tests/runner.bin
RUN . function synthetic_preserve

LOAD /mos-tests/runner.bin
RUN . function synthetic_clobber

# LOAD /mos-tests/runner.bin
# RUN . function synthetic_capability

LOAD /mos-tests/runner.bin
RUN . finalize
```

This first parser accepts exactly these uppercase LOAD/RUN forms, blank lines,
full-line # comments, LF/CRLF, and leading/trailing spaces or tabs. Function groups
must retain catalogue order. Duplicate/unknown groups, unmatched LOAD/RUN pairs,
missing scaffolding, empty selection, embedded NULs, overlong lines and other MOS
commands are rejected. This deliberately small language is not a general MOS
script interpreter. Current limits: 8 KiB script, 255 characters per line and the
three implemented synthetic functions. Future catalogue growth needs an explicit
extension; the seven compact plan templates are for these controls only.

`begin` reads the actual card script, derives its active groups, hashes its exact
bytes and persists plan.json and selection-script.txt. Every later invocation
checks that same script hash and the next expected group. Editing a script during
a run stops it. An interrupted/missing group or finalization cannot produce a
complete pass. Begin may reject an obviously missing finalize before any test;
a run interrupted after begin remains incomplete.

## Results and repeated boots

Card results live under /mos-tests/runs/<run-id>/. Every run carries the catalogue,
plan, target, bundle and run manifests, their referenced artifacts, selection
script and results.bin. A host-prepared installation namespace plus a persisted
64-bit counter allocates run IDs before tests execute. Existing run directories
are never overwritten. After a verified complete run, reboot starts a new run. An interrupted or
ambiguous run blocks startup; see [recovery instructions](recovery.md). It never
resumes an uncertain file tail. Never reset or replace install.bin while reusing the same installation
namespace. A malformed allocation file stops execution.

For an emulator, edit the source script and prepare a fresh bundle/image, or reuse
an existing image without changing its installation state to test repeated boots.
Editing sdcard/ after image creation does not edit the already-built sd.img.
For hardware, retrieve the entire run directory before using `human/mos-tests report`.
Hardware preparation and identity declarations are described in hardware.md;
no physical-machine qualification has been performed.

## Workaround and failure behavior

!boot.obey contains the local startup workaround, including EXEC /autoexec.txt.
MOS firmware is unchanged and MOS-01 remains parked. Removing that file can
re-expose the known missing-OBEY cleanup defect.

A test discrepancy is recorded and returns normally so later groups execute.
Infrastructure failure returns nonzero and MOS EXEC stops. No destructive media
or remount tests run inside this open script. SRAM continuation is same-boot only:
reset wipes it. Both the saved evidence and any retrieved SRAM faults must be
considered by the reporter; file completion alone does not prove power-loss safety.

## Qualification

```sh
./human/mos-tests startup-check --output .emulator/startup/review
```

The command checks native SHA/script boundaries and fresh raw-image trials for
full/single/commented selections, intentional discrepancy continuation,
infrastructure stopping, script changes, unknown functions, missing group/end
execution, and repeat-boot identity/preservation. Qualification fault modes are
explicit artifacts in test bundles; ordinary bundles use fault.bin=0.

New bundles provision two recovery journal files outside immutable artifact
hashes. Old bundles do not gain recovery merely by using a newer host observer.
Run recovery-check after changing the journal/gate; the host observer retrieves
its decision and preserves prior reports.
