# Fab emulator debugging reference

Use headless Fab and its debugger to observe the unmodified test binary at
instruction, register, memory, and MOS-call boundaries. Address triggers make
these observations suitable for automated checks. Use raw SD images for the
test baseline; W03 hostfs output capture remains bootstrap evidence only.
This reference describes the installed official Fab 1.2.4 implementation,
not an unverified newer release or a generic GDB interface.

## 1. Authority and evidence

1. Runtime source root: `/home/smith/Agon/mystuff/AgonJukebox/.emulator/runtime/fab-1.2.4`.
2. Read `README.md`, `src/parse_args.rs`, `src/main.rs`, the debugger client's
   `agon-light-emulator-debugger/src/{parser,lib}.rs`, and the machine core's
   `agon-ez80-emulator/src/{debugger,agon_machine}.rs`. Exact source identity
   and submodule revisions are in `tasks/SETUP-01/W08/source-identity.txt`.
3. W03 exercised headless launch, reset break, triggers, state capture,
   continue, Ctrl-C pause, deletion, and exit. Other features below are
   source-confirmed unless explicitly described as an integration proposal.
4. The CLI parser is the authority for accepted commands. The Rust DebugCmd
   interface contains additional internal operations; it is not an exposed
   network or JSON protocol.

## 2. Launch and backend control

From the subproject's `.emulator/` directory, the established headless entry is:

```bash
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
  ./fab-agon-emulator --renderer sw -d -b 0
```

1. This uses SDL dummy drivers, not a dedicated Fab `--headless` flag. Always
   use the profile-local wrapper so MOS hash verification remains active.
2. `-d` enables the debugger; `-b 0` stops at reset so commands can be installed
   before boot. Repeat `-b` for additional startup breakpoints. Remove the
   reset trigger with `delete $0` before continuing.
3. For qualified tests add `--sdcard-img /absolute/path/to/test.img` once W06
   prepares it. Fab accepts full MBR-partitioned or raw FAT32 images. The core's
   `set_sdcard_image` sets `enable_hostfs = file.is_none()`: an opened image
   disables hostfs even when a directory argument is also provided by the
   wrapper. Image open errors abort startup. The image is opened read/write;
   each mutating run should use an isolated copy with recorded before/after hashes.
4. `-z` zeroes initial RAM, useful for repeatable setup but capable of masking
   uninitialized-memory faults. Record its use and include ordinary RAM
   initialization when investigating such faults.
5. `--precise-interrupts` processes interrupts/hardware every cycle according
   to CLI help. Record timing mode; do not equate emulated cycles with hardware
   timing accuracy. `-u` removes CPU throttling. The installed parser accepts
   `--unlimited_cpu`, while help spells `--unlimited-cpu`; prefer `-u`.
6. `--verbose` enables additional VDP logging; `--uart1-device` and
   `--uart1-baud` connect UART1 to a host serial link. These are distinct from
   MOS's VDP output path and must not silently target physical bench devices.
7. `--ram-size` changes memory capacity; record it rather than assuming default
   configuration. Neither this option nor zero RAM is a substitute for boundary tests.

## 3. Debugger command reference

Command names are case-sensitive. Plain numbers are decimal. Hexadecimal
numbers accept `$40000`, `&40000`, `0x40000`, or `40000h`. The debugger does not
resolve linker symbols: derive addresses from the exact binary's map.

| Command | Behavior |
| --- | --- |
| `help` | Print command summary. |
| `break ADDRESS` / `br ADDRESS` | Add a persistent pause-and-state trigger. |
| `delete ADDRESS` | Remove all triggers at that address. |
| `triggers` / `info breakpoints` | List triggers and actions. |
| `c` / `continue` | Resume the CPU. |
| Ctrl-C | Pause from running mode and request state. |
| `pause` | Core pause command, also usable in triggers. |
| `s` / `step` | Execute one instruction and pause. |
| `n` / `next` | Step over CALL/RST using a one-shot next-address trigger; otherwise step. |
| `state` / `.` | CPU state and current instruction; interactive full output includes stack and cycle statistics. |
| `registers` | Full register display; accepted even though absent from help's summary. |
| `mem ADDRESS [LEN]` / `memory ...` | Dump bytes, default 16, with hex and ASCII. |
| `mem hl [LEN]` | Dump at BC/DE/HL/SP/IX/IY; register names are case-insensitive. |
| `dis [START [END]]` / `disassemble ...` | Disassemble using current ADL mode; defaults to PC and 0x20-byte span. |
| `dis16 ...` / `dis24 ...` | Force Z80/ADL disassembly respectively. |
| `trace on` / `trace off` | Toggle per-instruction logging. |
| `trigger ADDRESS ACTION : ACTION ...` | Execute core commands on each visit to an address. |
| `"message"` | Print a marker, especially useful inside triggers. |
| `exit` | Shut down the emulator. |

1. Empty input repeats the previous command: automation must not send accidental
   blank lines, especially after step/continue.
2. Trigger execution occurs before the instruction at its address. Multiple
   triggers at one address can coexist; delete removes all of them.
3. CLI triggers are persistent. Step-over creates internal one-shot triggers;
   there is no user-facing `once` switch in this parser. Step-over is not a
   general finish-until-return command and can wait indefinitely if a call
   never reaches the next instruction.
4. Register-relative memory uses 24-bit addressing in ADL mode and MB-based
   16-bit addressing otherwise. State contains a 16-byte stack sample.
5. Interactive full state reports cycle deltas and CPI. Deltas are relative
   to prior state processing, so extra observations affect the baseline.
   Automatic trigger output can be compact depending on client display state.
6. No CLI register/memory setters, arbitrary expressions, conditional
   breakpoints, data watchpoints, save-state commands, or source-level C++
   stepping were found in the installed parser. Do not invent GDB syntax.

## 4. Triggers as test observations

```text
trigger $40000 "ENTRY" : state
trigger $10 state
trigger $400c8 "MAIN RETURN" : state
```

The last address is specific to W03's recorded build, not a stable runtime ABI.

1. MOS output capture: at RST 10h entry, register A holds the output byte.
   W03 captured the high byte of AF and compared all bytes, including CR/LF,
   against the expected message. It also checked HL=0 at crt0 after main.
2. MOS-call ABI checks: trigger at a call site, wrapper entry, MOS vector, and
   post-call instruction to distinguish compiler argument setup, libagon
   translation, and MOS return behavior. Derive all non-vector addresses anew.
3. Buffer checks: use `mem hl LENGTH` or a resolved buffer address at a defined
   checkpoint. Compare bytes/canaries externally; pause if several observations
   must describe one stable state. Bounds traps do not detect writes to the
   wrong address when that address is valid RAM.
4. Targeted trace: `trigger ADDRESS "TRACE START" : trace on` and a separate
   end trigger with `trace off : state` limit volume around a suspect routine.
   Preserve the executed bytes and disassembly with the compiler listing.
5. Assembly comparisons: apply the same input and observation contract to
   separately built C++ and hand-written routines. Do not accept matching results
   from two routines sharing the same faulty wrapper as an independent oracle.
6. These are integration patterns, not implemented new tests or additional
   task commitments. W04 and W07 can adopt them where appropriate.

## 5. Emulator debug I/O and fault stops

1. README documents writes to I/O port 0x00 terminating the emulator with the
   written value as its exit code; this is an emulator-specific fixture feature.
2. Debugger I/O 0x10–0x1f requests a breakpoint; 0x20–0x2f dumps CPU state.
   The low eight port bits select the operation. The core handles marked
   unhandled I/O accesses; use the documented write pattern rather than
   depending on incidental read behavior.
3. These I/O hooks require deliberate emulator-only assembly fixtures and
   should not be emitted by hardware test builds. Our current smoke program
   uses external address triggers instead and contains no such instrumentation.
4. The core debugger pauses on recorded out-of-bounds accesses and reports
   address, disassembly and state. This is useful fault evidence, not full
   memory safety or a substitute for buffer guards.
5. Graphical shortcuts include RightCtrl-M for VDP memory statistics and
   RightCtrl-R for soft reset. They do not justify a graphical launch when
   headless evidence is sufficient; no equivalent typed reset command exists
   in this debugger parser. A fresh process is the straightforward clean run.

## 6. Reliable automation and evidence

1. Drive this terminal debugger through a PTY. W03's batched multiline input
   lost commands through readline; send one command at a time and synchronize
   with a new prompt or expected response. Fixed delays were adequate for that
   bootstrap experiment but are not a robust suite protocol.
2. Preserve raw terminal bytes and create a separate ANSI-cleaned interpretation.
   Exclude command echoes when searching for markers: an echoed trigger command
   is not evidence that its address was executed.
3. Scope observations between actual entry/exit events. Assert expected byte
   count, exact values, required checkpoints, and absence of unexpected pauses.
   A live process, printed marker, or zero process exit alone is insufficient.
4. Poll for completion with a documented failure timeout, retain partial logs
   on failure, and clean up only processes owned by the run. Close the debugger
   using Ctrl-C then `exit`, with bounded termination fallback and exit recording.
5. Record Fab/MOS/VDP identities, executable/map hashes, image identity/backend,
   RAM initialization, interrupt/throttling settings, commands, expected and
   observed results, and whether execution was instrumented or paused.
6. RST capture proves bytes reached the MOS entry point, not that pixels were
   rendered or a prompt became visible. Cycle counters are emulator evidence;
   host durations also include debugger/PTY overhead. Keep hardware, visual,
   filesystem, and CPU-interface claims separate.
7. Headless testing is the default. Human visual confirmation is needed only
   for behavior that cannot be sufficiently established by these observations.
   Commit authorization remains separate.
