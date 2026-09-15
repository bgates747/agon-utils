# W01 — Installed AgonDev inspection

W01 is complete: the installed toolchain and its local documentation were
inspected without modifying upstream or building a test program. Standard
AgonDev integration supports C++ and GNU assembly; W02 must explicitly resolve
the toolchain path in noninteractive SSH shells. Runtime behavior and compiler
correctness remain untested.

## Identity and evidence

1. Installation: `/home/smith/Agon/agondev/release`; `agondev-config --version`
   reports `1.0`. Checkout HEAD is
   `b67ab2444a63267a42193f204889d466765d8dd2` (STDIO EOF fixes), described as
   `nightly`; its Git status was clean. This identifies the installed local
   baseline, not a claim about the newest upstream release.
2. Clang reports 15.0.7, target `ez80-none-unknown-elf`, LLVM revision
   `c76386c0083e6a6236ff774275227e2389f85538`, matching the local LLVM checkout.
3. GNU assembler and linker report Binutils 2.45. The assembler's configure
   target is `z80-none-elf`, despite the `ez80-none-elf-as` executable name;
   the supplied Makefile selects eZ80 with `-march=ez80+full`.
4. [inspection.txt](inspection.txt) retains command outputs, exit statuses,
   and relevant installed configuration/runtime source. [installed-inputs.sha256](installed-inputs.sha256)
   fingerprints installed compiler, assembler, linker, library and build configs.
   Source revision alone does not prove an installed archive was built from it.
5. [cxx-predefined-macros.txt](cxx-predefined-macros.txt) records a read-only
   compiler preprocessing query. No test binary was compiled or executed.

## Standard build conventions

1. The documented minimum Makefile sets `NAME` and includes the path returned
   by `agondev-config --makefile`, currently `release/config/makefile.inc`.
   The include internally queries `agondev-config --prefix` unless
   `AGONDEV_TOOLCHAIN` is supplied. `command -v agondev-config` failed in this
   noninteractive SSH shell. W02 should use explicit tool paths/prefix or a
   documented PATH setting; merely including an absolute makefile is insufficient.
2. `src/` is searched recursively for `.c`, `.cpp`, `.s`, `.asm`, and `.src`.
   Optional project headers and libraries live in `include/` and `lib/`.
   Generated objects go to `obj/`; `bin/` receives `.noname.bin`, final `.bin`,
   and `.map`. Avoid same-stem sources with differing extensions: they map to
   the same object name. There is no header dependency generation in these rules.
3. C and C++ use the same Clang executable. Flags include target
   `ez80-none-elf`, `-Oz`, GNU-style eZ80 assembly emission, explicit header
   directories with `-nostdinc`, and `-fno-threadsafe-statics`. C++ adds the
   installed `include/c++` directory. No language-standard flag is set.
4. The compiler's default C++ macro is `201402L` (C++14). Its target macros
   report little endian, 3-byte int/pointer/size_t/ptrdiff_t, 2-byte short,
   4-byte long/float/double, and 8-byte long long/long double. Tests must not
   assume the host's integer or pointer widths.
5. Exception and RTTI macros are enabled by the frontend; this does not prove
   that the installed embedded runtime can link or execute every such feature.
   Neither full C++ standard-library support nor exceptions/RTTI was qualified.
6. Assembly extensions all invoke GNU AS directly, without C preprocessing.
   Consult `.assume adl=1`, `.section`, `.global`, `.include`, `d24`, and
   `rst.lil` examples in the installed runtime. ez80asm source syntax is not
   automatically interchangeable. C-linkage entry points use underscore symbols
   in inspected wrappers; C++ assembly interfaces should use `extern "C"`.
7. GNU LD links objects with `libagon.a`, emits a raw binary and map, then
   `agondev-setname` updates the final binary name. The installed library folder
   contains `libagon.a`; README language about separate libc/fp/crt libraries
   is less precise than the installed Makefile. Object disassembly can be
   obtained with the installed `ez80-none-elf-objdump`; a linked ELF is not a
   standard output of this configuration.

## Runtime and MOS boundary

1. Defaults are RAM_START `0x40000`, RAM_SIZE `0x70000`; linker stack top is
   their sum (`0xB0000`). Heap lower bound is BSS end and upper bound is stack
   top. These are configuration facts, not measured available stack/heap space.
2. crt0 emits the MOS header with ADL mode, saves registers and the MOS stack,
   sets the application stack, clears BSS, resets heap/stdio state, processes
   arguments, runs initialization functions, obtains MOS sysvars, and calls
   `_main`. It handles finalizers and restores the original stack/registers.
   Main arguments are placed on the stack and its return code is in HL.
3. `LDHAS_ARG_PROCESSING=1` selects the extended argument/redirection parser.
   Setting it to zero does not remove basic parsing: crt0 defaults to
   `_parse_params`. `LDHAS_EXIT_HANDLER=1` enables a status message handler
   that resets HL to zero; leave its effect explicit when testing return codes.
4. Prefer `<agon/mos.h>`; `<mos_api.h>` warns that it is deprecated and includes
   the former. The current header supplies C linkage for C++ callers.
5. `mos_fopen.src` saves IX, fetches filename at IX+6 and mode at IX+9,
   invokes `rst.lil 08h`, and returns the handle in A. `mos_fread.src` fetches
   arguments at IX+6/+9/+12, makes the MOS call, and moves DE into HL for the
   byte-count return. These concrete adapters illustrate stack-to-MOS-register
   translation; they do not establish a complete ABI for every type/function.
6. Independent hand-assembly comparisons should distinguish compiler call-site
   code, linked wrapper behavior, and raw MOS behavior. Two tests sharing a
   faulty wrapper could agree. W04 owns implementing that comparison path.

## Emulator and BASIC integration implications

1. Standard `make emulator` changes to FAE_HOME and runs `./fab-agon-emulator`;
   it can use our canonical profile wrapper. The copy target writes to
   `FAE_HOME/sdcard` plus FAE_DEST, default `/bin`. Use the project-owned profile
   and a unique output filename; do not overwrite shared standard-utility links.
2. BBC BASIC files are not among the Makefile's compiled source extensions.
   They need a separate fixture/invocation path under W05. Interpreter selection
   and runtime execution were not performed in W01.
3. No emulator profile changes, graphical boot, firmware flashing, or physical
   hardware tests were part of this inspection. Hardware confirmation remains
   outstanding for future executable tests, not for this documentation inspection.

## Local sources consulted

Paths below are relative to `/home/smith/Agon/agondev`:

1. `README.md` — project structure, commands, options, components, known limits.
2. `docs/install-linux.md` — release installation and PATH setup.
3. `release/config/makefile.inc` — actual compiler/assembler/linker commands.
4. `release/config/linker.conf` — memory, sections, stack and initialization tables.
5. `src/lib/libcrt0/crt0.src` — entry, arguments, initialization and exit behavior.
6. `release/include/agon/mos.h` and `release/include/mos_api.h` — public MOS header.
7. `src/lib/libmos/mos_fopen.src` and `mos_fread.src` — representative MOS wrappers.

This is an installed-toolchain précis. Claims about MOS correctness must later
be checked against official platform documentation and execution evidence.
