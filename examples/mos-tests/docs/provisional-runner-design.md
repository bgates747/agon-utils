# Provisional design — Selecting and running the suite

> Superseded for implementation planning by [test strategy](test-strategy.md)
> (MAIN-01 W03). Retained as brainstorming provenance; follow the strategy if
> wording differs. Neither document claims the tools are already implemented.


## Summary

Start with a human-editable autoexec.txt workflow: copy a prepared suite bundle
to an emulator SD image or hardware SD card, power on, and wait for saved reports.
Group tests by MOS function so humans can select useful subsets without choosing
among thousands of individual cases. A menu application is a later convenience
layer over the same selection and execution machinery.

These are provisional design ideas recorded at the Author's request, not an
implemented interface or finalized command syntax. The first-interface priority
and helper application language below are explicit Author directions. Detailed
syntax and feasibility belong to MAIN-01 W03 and MAIN-02; this document is not
another task checklist.

## First interface: editable startup script

Provide a ready-made full-suite autoexec.txt with readable groups named for MOS
functions. Conceptually, groups load and run the relevant function's test program;
users remove unwanted groups or comment them out where the verified script syntax
allows. Preserve a simple copy-to-card, power-on, read-reports experience. Do not
require a menu or host-side agent to select or execute the ordinary suite.

MOS 3.0.2 qualification currently relies on populated !boot.obey to avoid the
missing-OBEY cleanup fault. autoexec.txt is the intended human selection file,
not a claim that MOS will automatically execute it after !boot.obey. Verify and
document how the supplied startup files invoke the selection file, what comment
syntax is supported, and the exact LOAD/RUN argument syntax before publishing a
bundle. Do not invent a working boot chain or silently fall back to hostfs.

Package required executables, fixtures and startup files together, with clear
copy destinations and version identity. For emulator qualification, deploy the
bundle into a raw SD image; for hardware, use the physical SD card workflow.
Both should expose the same human selection model and meaningful saved reports.

## Common selection model

MOS function names are the main selection unit. A request such as "run every
case for mos_foo" should select the same cases whether expressed in a startup
script, future menu/configuration file, or agent invocation. Retain room for
named groups and individual-case selection without making them mandatory for a
human running the whole suite or one function. Exact names and syntax remain
provisional; distinguish RST selectors and C-function lookup routes where needed.

The boot script, configuration and agent interface must reuse shared case
selection, fixtures, expectations and result logic. They are entry points into
one suite, not independent implementations with diverging coverage.

## Later convenience application

A future menu-driven on-device application could select functions/groups, run
them and save or load a human-readable configuration that can also be hand edited.
It should add convenience without becoming a prerequisite for the startup-script
workflow. No menu implementation is authorized or required by this design note.

**On-device helper applications, including the future menu application, must be
written in C++ targeting AgonDev.** The Author prefers this because LLMs are more
effective writing these applications in C++ than assembly. This does not replace
assembly used to test exact register/ABI behavior or BBC BASIC fixtures. Existing
host-side Python orchestration can remain Python; it is not an Agon application.

## Agent use

Agent guidance should translate a request such as "mos_foo is behaving strangely;
run all its tests and report findings" into the shared function selection and
reusable execution tools. Agents may add debugger automation, batch orchestration
and structured evidence retrieval. They should invoke human/shared tools where
suitable instead of duplicating them or their instructions.

## Reporting and recovery ideas to evaluate

Save results incrementally so a failure does not erase earlier findings. Provide
a concise summary and a clear completion marker, with counts distinguishing
passes, discrepancies, skips and unfinished work; detailed evidence follows.
Consider recovery or resume after a failing case/group. A target crash may
prevent on-device continuation, so do not promise automatic recovery merely
because tests are sequentially listed in a boot script. Record the last started
case and completed results where feasible. Bound hangs using backend-appropriate
mechanisms; host debugger control is not assumed available on hardware.

Report-writing itself depends on MOS behavior being tested. W03 must consider
separating test mutations from report storage, preserving earlier results, and
what can be recovered if the reporting filesystem path fails. Exact formats,
checkpoint granularity and recovery mechanisms remain design decisions.

## Authority and compatibility

Hardware is authoritative for real-machine behavior. Emulator runs also have
independent value for emulator development; every report identifies its backend,
firmware and suite identities. Never convert an emulator pass into a hardware
claim. Highlight advertised-versus-observed behavior, including register
preservation and defaults. A discrepancy does not authorize changing firmware:
prioritize documentation clarity and preservation of legacy behavior.

## Ownership and next design decisions

[MAIN-01](tasks/MAIN-01.md) W03 owns detailed runner, result and isolation design;
W04 owns sequencing. [MAIN-02](tasks/MAIN-02.md) owns human/agent entry points and
initial front ends. Prioritize the editable startup-script method before a menu
application. When decisions mature, promote them into the maintained test strategy
and human instructions, then mark the affected provisional material superseded
with links rather than leaving competing instructions.

## Result design refinement

See [provisional result design](provisional-result-design.md): binary RAM capture,
early and frequent SD checkpoints, post-run text and best-effort recovery. This
refines the reporting ideas above; do not defer checkpoints to suite completion.
