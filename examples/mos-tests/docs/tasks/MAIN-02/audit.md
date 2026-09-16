# Tool ownership audit

Existing scripts/prepare_sd_image.py and run_emulator.py remain shared primitives.
Root Makefile remains the build owner. W04 source fixtures and W06 observer were
promoted into fixtures/smoke and scripts/run_smoke.py for routine operation.
W05 BASIC qualification stays historical pending deliberate general-runner
integration; its pinned interpreter and evidence are not silently duplicated.
Human front end dispatches shared operations; agent guidance reuses it. No
hardware runner or full-suite reporting is claimed. Historical logs and source
reference archives remain evidence rather than operational dependencies.
