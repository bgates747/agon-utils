# agon-utils Project Handoff

Read `/home/smith/Agon/mystuff/agon-dev-env/codex/AGENTS.md` first. This file
contains only agon-utils-specific guidance.

## Canonical checkout and environment

The canonical checkout is:

```text
/home/smith/Agon/mystuff/agon-utils
```

Use its `.venv` explicitly. Before other Python work, verify the compiled
extension, dependencies, ABI, and round trip:

```bash
.venv/bin/python tests/test_agonutils.py
```

Applications consuming `agonutils` require their own compatible editable
installation of this checkout; the shared Python procedure is documented in
the canonical environment guide.

## AGNB

The public application-neutral loader is:

```text
examples/agnb/api/agnb_api.inc
```

Its external dependency reference is `examples/agnb/api/agnb_dependencies.inc`.
Do not introduce application filenames, UI, plotting, playback policy, or
debug presentation into the API. Applications obtain record boundaries through
the generic image and audio callback entry points.

Authoritative and reusable material lives under `examples/agnb`:

- format and API documentation;
- image and audio writers;
- independent validators;
- hardware/emulator harnesses;
- `docs/ez80_hacks.md`; and
- chronological dev logs, including the 2026-07-24 production-integration
  failure modes and resolutions.

Reuse the proven writers and validators rather than independently recreating
RIFF layout, alignment, explicit buffer IDs, or metadata checks.

## Repository workflow

AgonVideo may embed agon-utils as a pinned submodule, but this standalone
checkout is canonical for utility development. Commit utility changes here
first; update a consumer's submodule or editable installation separately.

Inspect generated assets and harness targets before staging. Keep environment
profiles and machine setup scripts in
`/home/smith/Agon/mystuff/agon-dev-env`, not in this repository.
