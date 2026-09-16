# Hardware route — pending implementation

Hardware is the final authority for real-machine behavior. No physical hardware
qualification has been performed for this project, and no full-suite card bundle,
unattended reporting or on-device report decoder is available yet.

The emulator smoke tool must not be presented as a hardware runner. The hardware
command currently returns status 2 with this limitation. Do not flash firmware or
write a physical device as a side effect of scaffolding.

The planned human workflow is to copy a prepared bundle onto the test SD card,
edit autoexec.txt by function group, boot, and read saved reports. Implementation
must first verify the !boot.obey chain, card paths, target versions, report
retrieval and safe use of a dedicated test card. See [strategy](../docs/test-strategy.md).
Existing setup evidence remains emulator-only. Hardware capabilities will be
linked here as they are implemented and actually exercised.
