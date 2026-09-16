# MOS tests

**If you are a human who wants to use these tools, start in [human/](human/README.md) and follow its emulator or hardware instructions.**

Agents: start with [agents/](agents/README.md).

A MOS test suite within `agon-utils/examples/mos-tests`, intended to exercise
Agon MOS behavior and help isolate AgonDev code-generation or MOS-call faults.
The scaffold, dedicated emulator, and standard AgonDev build configuration
are complete and accepted. C++, independent assembly, and BBC BASIC smoke checks
passed headlessly. See [build configuration](docs/build.md),
[test results](docs/test-results.md), and [SETUP-01](docs/tasks/SETUP-01.md).

## Test direction

1. C++ is the primary test implementation language.
2. BBC BASIC is an important complementary test route, including interpreter
   behavior and MOS interaction where appropriate.
3. Assembly routines can exercise exact register/ABI behavior and provide
   independent comparisons against compiler-generated code. Preserve compiler
   listings/disassembly and observed results when investigating discrepancies.
4. Record firmware, compiler, runtime, test inputs, expected behavior, and
   execution environment with results. Emulator evidence and hardware evidence
   are separate claims.

See [HANDOFF.md](HANDOFF.md) for current operation and [TODO.md](TODO.md) for
unfinished work. No MOS test coverage or compiler correctness is claimed yet.
