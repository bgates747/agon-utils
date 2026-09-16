# Build and baseline validation

Human operation is documented in [human/emulator.md](../human/emulator.md).
Use that entry point for builds, raw-image preparation and automated smoke runs.

The root Makefile uses standard AgonDev integration from
/home/smith/Agon/agondev/release, C++14, -Oz, load address 0x40000, RAM size
0x70000, and the existing repository .venv. make and make clean manage root
obj/ and bin/ outputs; AGONDEV_TOOLCHAIN can override the installation prefix.
The promoted comparison fixtures have their own ignored build outputs.

SETUP-01 qualified the bootstrap C++, assembly and BBC BASIC routes. MAIN-02
promoted C++/assembly fixtures and observer into maintained locations and reran
them through the human front end successfully. Historical BASIC evidence remains
under SETUP-01/W05 pending general-runner integration. No hardware qualification
is claimed. Use raw SD images and !boot.obey; do not use inherited hostfs targets
for qualification. The startup runner now executes the three synthetic controls with the same
AgonDev toolchain; human/mos-tests bundle builds it and supplies its generated
catalogue/hash table. See human/startup.md for the editable startup workflow.
