# Qualify the test foundation

These checks test the tester with known synthetic outcomes. Run them before
relying on modified capture, recording or reporting code. They do not establish
MOS API conformance or physical hardware behavior.

## Run on Linux

From /home/smith/Agon/mystuff/agon-utils/examples/mos-tests, choose a new output
root for each qualification. Run emulator checks sequentially: they share build
outputs and the dedicated profile.

```sh
/home/smith/Agon/mystuff/agon-utils/.venv/bin/python ../../tests/test_agonutils.py
/home/smith/Agon/mystuff/agon-utils/.venv/bin/python tests/runner/check_planner.py
./human/mos-tests runner-build
./human/mos-tests capture-check --output .emulator/review/capture
./human/mos-tests recording-check --output .emulator/review/recording
./human/mos-tests report-check --output .emulator/review/reports
./human/mos-tests startup-check --output .emulator/review/startup
./human/mos-tests smoke --output .emulator/review/smoke
```

Native lifecycle controls are also part of complete qualification:

```sh
mkdir -p .emulator/review
g++ -std=c++14 -Wall -Wextra -Werror -I apps/runner/include \
  tests/runner/lifecycle_test.cpp -o .emulator/review/lifecycle
.emulator/review/lifecycle
```

Inspect each command's exit status and saved result.json, including the nested
startup reports. Qualification succeeds when deliberately bad inputs receive
their expected failure/incomplete verdicts; those injected failures are not
unexpected suite failures. Stop and investigate an unexpected qualification error.

## Fresh-image repeat

Use [startup instructions](startup.md) to create an independent bundle with only
synthetic_preserve and synthetic_clobber selected. Run it into a fresh output
directory. Expect ALL TESTS PASSED, two selected controls, and return to the MOS
prompt. The default three-control bundle instead reports limited coverage because
the UART fixture is unavailable. startup-check also reboots one existing image,
verifying new run identity and preservation of all previous run files.

## Evidence and limits

Keep binary records, manifests, text reports, debugger transcripts, SRAM dumps,
compiler/runtime identities and exact commands together. The MAIN-03 W07 task
archive is a delivery snapshot; maintained commands above are the routine entry
points. Do not copy archived source into production to bypass current guidance.

Controlled debugger retrieval before reset is supported. It does not prove
recovery from arbitrary CPU/VDP crashes or power loss. Hardware, IFF/alternate
register state and timing remain unqualified. Reset may wipe SRAM. Preserve
!boot.obey for the parked MOS-01 workaround.

All reusable helpers are already promoted under human/, scripts/, agents/,
apps/ and tests/. Agents use these same commands; no duplicate test engine.
