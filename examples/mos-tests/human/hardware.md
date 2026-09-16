# Hardware route — bundle available, physical validation pending

Hardware remains the authority for real-machine behavior. The editable startup
bundle exists, but this project has not run it on physical hardware. Emulator
qualification does not establish hardware correctness. No tool here flashes
firmware or writes a physical card automatically.

## Prepare a first-install test card

1. Identify the actual target MOS binary/version and map if available. Prepare a
   schema-1 target.json using the fields in docs/result-format-v1.md: backend is
   hardware; declared_by states the operator and how identity was established.
   Use real MOS SHA-256 values. emulator_binary_sha256 is null; unavailable MOS
   map/VDP identities may be null. The builder supplies the current toolchain hash.
   Do not reuse the emulator target declaration as hardware provenance.
2. On Linux, run:

   ```sh
   ./human/mos-tests bundle --backend hardware --target /path/to/target.json \
     --no-image --output /path/to/new-bundle
   ```

3. For a dedicated test card, copy the contents of the generated sdcard/ directory
   to the card root. The files include !boot.obey, autoexec.txt and mos-tests/.
   Preserve any existing card startup intentionally; do not blindly replace a
   working setup. The local !boot.obey workaround remains necessary for the
   parked MOS-01 defect on the pinned baseline.
4. Edit /autoexec.txt as described in [startup instructions](startup.md). Comment
   out or delete both LOAD/RUN lines of unwanted function groups. Keep begin and
   finalize. Boot the machine and wait for the completion/error message.
5. Retrieve the complete /mos-tests/runs/<run-id>/ directory to Linux, then use
   `human/mos-tests report --run RUN_DIRECTORY --output NEW_REPORT_DIRECTORY`.
   A missing completion, error or limited selection cannot be treated as all-pass.

Every installation has its own namespace/counter in install.bin. Preserve that
file when reusing the installation; do not reset its counter or replace it with
an earlier copy. Existing run directories are refused, not overwritten. These
instructions cover a fresh installation, not an automatic upgrade/migration tool.
Card removal/power-loss guarantees, hardware recovery, display/audio rendering
and timing remain unqualified. Report options and evidence limits are in reports.md.
