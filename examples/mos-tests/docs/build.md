# AgonDev build configuration

The standard AgonDev layout now builds the W03 C++ MOS smoke program from
`src/main.cpp`. A clean build passed; emulator output and prompt return await
human confirmation. See [W03 procedure](tasks/SETUP-01/W03/README.md).

## Layout and commands

1. Run commands from `agon-utils/examples/mos-tests` on Linux.
2. Put C/C++ and GNU-AS sources in `src/`, optional project headers in
   `include/`, and optional libraries in `lib/`. Keep source basenames unique
   across extensions. `obj/` and `bin/` are generated and ignored.
3. `make` uses the installed AgonDev makefile. `make clean` removes only the
   standard subproject `obj/` and `bin/` outputs. `make V=` shows tool commands.
4. The default toolchain prefix is `/home/smith/Agon/agondev/release`.
   Override with `make AGONDEV_TOOLCHAIN=/absolute/installation/prefix`.
   No shell PATH configuration or upstream edits are required for the build.
5. The target name is `mos-tests`, with C++14 and the toolchain's default `-Oz`
   target flags. RAM starts at `0x40000`, spans `0x70000`, and both optional
   extended argument processing and exit-handler switches are zero. Basic
   runtime argument parsing remains active.
6. `PYTHON` resolves to the existing repository-root `.venv/bin/python`.
   No Python helper or second environment is introduced by this configuration.
7. The upstream configuration owns compilation, assembly, linkage, map output,
   naming, and clean rules. Project configuration only selects identity,
   installation, dialect, memory/runtime options, and the empty-source guard.

## Current validation boundary

W02 validation covers Makefile loading, standard rule expansion, installation
override, and the missing-source diagnostic. The W03 clean smoke build has also passed;
W04 owns assembly comparisons and W06 owns deployment configuration. The W03 procedure documents the prepared manual smoke deployment; reusable
deployment integration remains W06 work.

See `tasks/SETUP-01/W02/validation.txt` for recorded command results.

## Headless verification update

W03 is complete using headless debugger evidence: exact output bytes at MOS
RST 10h and HL=0 after main returned. See
`docs/tasks/SETUP-01/W03/headless-result.md`.
The graphical and headless processes are closed. Earlier pending visual-review
notes describe the initial attempt; no visible-prompt or hardware claim is
made. Hostfs was used for this bootstrap check; W06 owns raw SD image migration.
All changes remain uncommitted.

## Raw-image workflow (W06 qualified)

`make sd-image` creates a new verified image; it refuses an existing image.
`make headless` delegates through `scripts/run_emulator.py`, which requires the
image and passes it to the canonical profile wrapper. Raw-image boot uses !boot.obey and passes the comparison checks; see `tasks/SETUP-01/W06/README.md`. Avoid upstream hostfs
`make em`/`copy` targets for qualified tests.
