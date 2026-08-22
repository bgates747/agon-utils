# Original-core correctness proof

This proof answers one narrow question: can the unmodified original 8080
machine code execute correctly as eZ80 ADL=0 code? It deliberately excludes
hardware I/O, video presentation, frame scheduling, and performance.

## Independent reference

The preserved `src/invaders.asm` is assembled with ASMX 2.0b6 from
`apws/230831-asmx` commit
`e59c4027eed490767009940d5c7096eb383486cf`. The result is exactly 8,192 bytes
with SHA-256:

```text
7446e0994117596de5206519e693f8875ff3455e0be121d5cb975c3bcc224c4e
```

`make core-proof ASMX=/path/to/asmx` refuses any other reference bytes. The
agondev linker embeds those bytes at file offset `5000`, and the validator
compares the complete embedded image back to the independent reference.

## ADL=0 execution layout

| Logical address | Purpose |
| ---: | --- |
| `0000-0044` | Disposable MOS launch stub and ADL=0 header |
| `0000-1fff` | Byte-identical original ROM after loader copy |
| `2000-3fff` | Original RAM and packed framebuffer addresses |
| `4000-40e1` | agondev deterministic test harness |
| `5000-6fff` | Embedded source copy of the reference ROM |
| `8000+` | agondev loader and diagnostic text |

The MOSlet already executes within one MBASE bank. Moving only the loader
above the original map lets the core use ordinary 16-bit addresses, calls,
returns, stack operations, and ALU instructions. The proof contains no MBASE
change and no mixed-mode game routine.

Because low memory is replaced with the arcade vectors, the proof disables
interrupts before installing the ROM. The eventual scheduler must enter the
two original phases explicitly rather than letting Agon hardware interrupts
dispatch through those vectors.

## Deterministic tests

The harness calls these routines at their original numeric addresses:

1. `InitAliens` at `01c0`: writes exactly 55 live flags and preserves a guard
   byte.
2. `AddDelta` at `01d9`: performs two wrapping eight-bit coordinate updates.
3. `GetAlienStatPtr` at `1581`: computes `row*11+column-1` in player RAM.
4. `CountAliens` at `15f3`: counts three sparse live flags and leaves the
   one-alien flag clear.
5. `CountAliens` one-alien branch: returns one and sets RAM flag `206b`.

The harness uses short `CALL` and short `RET` throughout. PASS and FAIL are
terminal diagnostics because the proof replaces SPS and the low-memory
MOSlet veneers; it does not attempt to return to MOS.

## Meaning of PASS

PASS proves the exact original bytes exercised by these tests have compatible
instruction, flag, stack, address, and RAM behavior on the emulated eZ80 in
ADL=0 mode. It is not evidence that original `IN`/`OUT` instructions are safe,
that the complete initialization/main loop runs, or that enough real-time CPU
margin exists beside direct GPIO scanout.
