# Sprite Affine Transforms Project Handoff

Read `/home/smith/Agon/mystuff/agon-dev-env/codex/AGENTS.md`, then the
repository-level `../../AGENTS.md`, and finally this file.

This directory owns the eZ80 regression fixtures, generated RGBA2222 assets,
expected results, reports, and bespoke emulator profile for sprite affine
transform work. Firmware changes belong in
`/home/smith/Agon/mystuff/agon-vdp-sprite-transforms` on
`feature/sprite-affine-transforms`.

Use `/home/smith/Agon/mystuff/agon-utils/.venv/bin/python` for every Python
command. Image conversion must use the editable `agonutils` installation from
this repository. Before Python asset work, run the repository smoke test:

```bash
../../.venv/bin/python ../../tests/test_agonutils.py
```

Assembly sources live in `src/`; generated binaries live in `build/`; source
images live in `assets/source/`; generated VDP inputs live in
`assets/rgba2222/`; and oracle material lives in `expected/`. Do not commit
generated emulator state or build outputs.

The mutable profile is `emulator/`. Create or repair it with
`scripts/setup_emulator.py`, and launch it with `scripts/run_emulator.sh`.
Both scripts intentionally fail closed if the bespoke native VDP module is
absent. All emulator-related changes remain uncommitted and unpushed until the
Author has tested them and explicitly approves a commit.

`TODO.md` is this project's only authoritative actionable checklist.
