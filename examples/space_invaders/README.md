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

No licensing terms were included in the retrieved source file, so none are
inferred here.

## Project status

The runnable Agon port targets agondev and eZ80 `ADL=0`. The build boundary is
established; game translation and hardware adapters remain planned work in the
project’s single authoritative [TODO](TODO.md).
