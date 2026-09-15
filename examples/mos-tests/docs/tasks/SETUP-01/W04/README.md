# W04 — Independent assembly comparison

Completed: separate C++ and hand-assembly executables produced the same expected
MOS output sequence, returned the full 24-bit value 0x123456, balanced the stack,
and preserved IX. Both were built and run headlessly. This is a bounded
hostfs-bootstrap check; it does not qualify MOS filesystems, visual rendering,
all C++ code generation, or physical hardware.

## Contract and implementation

1. Both programs emit `W04: MOS ABI 0123456789 AaZz !?` followed by CR/LF.
   The Python observer defines the expected bytes independently and compares
   each run against them, as well as comparing the two runs.
2. `cpp/src/main.cpp` iterates a constant string and calls libagon `putch`.
   `assembly/src/main.src` independently loops over its own string and invokes
   `rst.lil 10h` directly with the character in A, preserving its string pointer
   on the stack. It does not call the compiler-generated loop or libagon putch.
3. Both variants share AgonDev's assembler/linker/crt0 and the same MOS/VDP/Fab
   environment. Independence is specifically the output loop and MOS adapter,
   not every component of the execution stack.
4. The explicit return constant 0x123456 exercises all three bytes of HL.
   Debugger execution stops at `___exithl`, before crt0 passes that deliberate
   nonzero result to MOS. This is not a normal zero-exit smoke program.
5. W04 targets RST 10h character output only. Other MOS calls, high-bit character
   values, stack-argument combinations, buffer side effects, and timing are not
   covered. W06 will supply the raw-image test baseline.

## Observations and machine-code review

1. The runner resolves `_main` and `___exithl` from each freshly built map,
   pauses at reset, installs triggers, then captures MOS RST 10h states and
   pauses at main return. It synchronizes commands with debugger prompts.
2. Each variant's captured A-register bytes exactly matched the independent
   expected sequence. HL was 0x123456 at return; SPL advanced by exactly three
   bytes across main's RET, and IX matched its entry value.
3. C++ disassembly shows zero-extension into HL, a pushed argument, relocation
   to `_putch`, caller stack cleanup, and `21 56 34 12` loading the return value.
   The assembly path uses `5b d7` for `rst.lil 10h` and the same immediate return
   encoding. The different loop implementations reached the same observations.
4. Official local sources consulted: `agon-docs/docs/mos/API.md`, RST 10h
   section (input A), and `agon-docs/docs/mos/Executables.md` (ADL executable
   header). AgonDev's inspected crt0 supplies the stack/return convention;
   W01 and the retained generated code provide its provenance.
5. These checks exercise the target binary, not just matching textual listings.
   The linked map, object disassembly with relocations, and compiler-produced
   assembly are retained to investigate any future discrepancy.

## Reproduction

On Linux:

```bash
cd /home/smith/Agon/mystuff/agon-utils/examples/mos-tests
../../.venv/bin/python docs/tasks/SETUP-01/W04/run_comparison.py
```

1. Run with no other instance using this profile. The runner performs clean
   builds in the two task-local projects, temporarily deploys a unique binary,
   verifies its hash, and restores the original autoexec afterward.
2. It invokes the canonical `.emulator/fab-agon-emulator` wrapper from that
   directory with SDL dummy video/audio, software renderer, debugger, and reset
   breakpoint. The backend is explicitly hostfs bootstrap. It does not alter
   source or launch settings in shared/upstream checkouts.
3. A 30-second prompt timeout bounds a missing debugger response; it is a
   harness failure deadline, not a hardware timing assertion. It closes only
   its child emulator and cleans its temporary deployment in a finally block.
4. Current runs took about one second per variant from deployment through
   execution and shutdown, excluding the preceding build. PTY/debugger overhead
   is included; these are host durations, not calibrated target timings.
5. Re-running currently refreshes `evidence/<variant>/`. Preserve a trial copy
   before a changed experiment whose earlier evidence must remain separately
   reviewable. This task-local harness is not yet a general suite interface.

## Evidence

`evidence/cpp/` and `evidence/assembly/` each contain clean build logs, candidate
binaries and maps, object disassembly, raw and ANSI-cleaned debugger transcripts,
captured output bytes, and a JSON result with hashes, addresses, checks, and
elapsed time. The C++ directory also includes `compiler-main.s`.
`runtime-identity.json` records runtime/MOS/configuration identity for this run.

The existing W03 subproject source/binary is unchanged. Both W04 emulator
processes exited with status zero and temporary startup changes were restored.
No human visual check or hardware execution occurred; changes remain uncommitted.
Mature reusable observation infrastructure can be promoted from this task silo
when its interface is established; W07 can build on these evidence conventions.
