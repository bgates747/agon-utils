# Space Invaders original source

This subproject is the start of an Agon port of David Levy's ASMX
reconstruction of the original 1978 Space Invaders Intel 8080 ROM image.

The source was retrieved unchanged on 2026-08-22 from:

<https://computerarcheology.com/Arcade/SpaceInvaders/invaders.asm>

The surrounding analysis and hardware notes are at:

<https://computerarcheology.com/Arcade/SpaceInvaders/>

## Build

Install agondev 1.0 and make `agondev-config` available on `PATH`, then run:

```sh
make
```

Alternatively, name an installed agondev release tree explicitly:

```sh
make AGONDEV_PREFIX=/path/to/agondev/release
```

The build emits `build/bin/invaders.bin`, an intentionally minimal MOS
execution probe. It establishes the Agon `ADL=0` image and clean-return
contract; it does not contain the game yet. The build also emits an assembler
listing and linker map, verifies their important addresses and bytes, and
checks the preserved source checksum. See [agondev Build Baseline](docs/agondev.md).

The preserved `src/invaders.asm` uses ASMX/Intel syntax and is not an agondev
input. Runnable sources live separately under `src/agon/`.

The direct-GPIO architecture probe is built separately with `make gpio-probe`.
It bundles Tom's stock-MOS static GPIO-video driver and requires a 15
kHz-capable display. See [GPIO Raster Probe](docs/gpio-raster-probe.md) before
running it.

An emulator-only proof of the untouched game core is built with:

```sh
make core-proof ASMX=/path/to/asmx
```

ASMX independently assembles the preserved Intel source to the expected
8,192-byte ROM; agondev assembles the ADL=0 loader and deterministic harness.
See [Original-core correctness proof](docs/core-correctness-proof.md).

The next emulator milestone adds address-preserving hardware traps and runs
original initialization through main-loop entry:

```sh
make adapter-proof ASMX=/path/to/asmx
```

See [Original I/O adapter contract](docs/io-adapter-contract.md).
This proof does not present the original packed framebuffer, so its expected
visible output is only the MOS PASS/FAIL diagnostic.

Incremental GNU Z80 syntax translation is checked independently with:

```sh
make translation-proof ASMX=/path/to/asmx
```

See [Opcode-traceable agondev translation](docs/translation-strategy.md).

No licensing terms were included in the retrieved source file, so none are
inferred here.

## Project status

The runnable Agon port targets agondev and eZ80 `ADL=0`. The build boundary and
first original-code execution proof are established; hardware adapters and
the complete game loop remain in the project’s single authoritative
[TODO](TODO.md).
