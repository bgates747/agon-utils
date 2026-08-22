# agondev Build Baseline

## Verified toolchain

SETUP-001 was exercised with:

- `agondev-config` version 1.0;
- agondev checkout `b67ab2444a63267a42193f204889d466765d8dd2`
  (`nightly` at the time of verification); and
- GNU assembler, linker, objcopy, and objdump 2.45 for
  `ez80-none-elf`.

`agondev-config --prefix` supplies the installation prefix. The project
Makefile accepts either an `agondev-config` available on `PATH` or an explicit
`AGONDEV_PREFIX` pointing at an installed agondev release tree.

## Assembler contract

agondev uses GNU `as`, configured here with `-march=ez80+full`. It accepts GNU
sections, `.include`, `.assume adl=...`, eZ80 instruction suffixes, assembler
listings through `-a`, and ELF object output.

It does not accept the preserved source’s ASMX `CPU 8080` directive or Intel
8080 mnemonics such as `JMP`, `MVI`, `MOV`, `LXI`, `LDA`, and `STA`. A direct
probe reported 1,346 assembly errors. The port therefore requires a separate,
checked-in Z80/eZ80-syntax translation; `src/invaders.asm` must not be rewritten
or passed directly to agondev.

## Link and binary contract

The standard agondev linker configuration and `libagon` CRT target ADL=1 and
write mode byte 1 in the MOS header. They are not suitable for this project’s
accepted ADL=0 baseline.

The project instead uses agondev’s assembler, linker, and `agondev-setname`
with `linker/adl0.ld` and the following raw binary layout:

| Offset | Size | Meaning |
| ---: | ---: | --- |
| `0x00` | 3 | ADL=0 `JP 0x0045` |
| `0x03` | 1 | Padding so the executable name begins at `0x04` |
| `0x04` | 60 | Executable-name field written by `agondev-setname` |
| `0x40` | 3 | `MOS` signature |
| `0x43` | 1 | Header version 0 |
| `0x44` | 1 | Execution mode 0 (`ADL=0`) |
| `0x45` | variable | Program entry and code |

Logical linked addresses begin at zero. MOS loads the file into an eZ80 memory
bank and uses the header’s mode byte to enter it in Z80-compatible mode. Calls
back to ADL-mode MOS code require explicit mixed-mode instruction suffixes.
MOS does not initialize the short-mode stack pointer for an `ADL=0` program,
so the entry probe sets `SPS` to logical address `0xfffe`. It returns through
`RET.LIS`, matching MOS's long return frame, and reports success in `HL`.

These details were checked against the installed Agon documentation at
`agon-docs/docs/mos/Executables.md`, `agon-docs/docs/MOS.md`, and
`agon-docs/docs/mos/API.md`, plus MOS's `_exec16` implementation. The
`ez80-framebuffer-agon` Z80 example independently uses the same header mode,
zero-based layout, and `RET.LIS` return boundary.

## Generated evidence

`make` produces ignored artifacts under `build/`:

- `build/obj/main.o` — ELF object;
- `build/listings/main.lst` — assembler listing;
- `build/invaders.map` — linker map; and
- `build/bin/invaders.bin` — MOS executable.

The normal build verifies the preserved source checksum, exact setup-probe
size and bytes, MOS header, ADL=0 entry encoding, executable name, and linker
symbol addresses.
