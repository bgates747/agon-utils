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


## AGNB plain-buffer ownership and status — 2026-10-23

The Author assigned generic AGNB format/writer/validator/eZ80 loader ownership
and scoped commit/push duties to the Golem agent. Active register:
examples/agnb/TODO.md; completed AGNB-001 and evidence under its docs/tasks silo.
Provisional0.3 BHDR/RAWD/DATA and agnb_load_buffers/callback use the existing
8KiB window without application setup or implicit execution. Pi/Oryx stock
qualification and Author review pass; earlier image/audio interfaces and bytes
are preserved. Golem-specific allocation, package setup/activation and host
integration remain owned in the Golem repository, GOLEM-046.

Publish only scoped AGNB changes. The canonical agon-utils branch has unrelated
divergent history; codex/agnb-plain-buffers is an isolated current-upstream branch
used to publish cherry-picked AGNB work without altering unrelated history.


## AGNB C++ continuation — 2026-10-23

AGNB-002 implements application-neutral0.3 C++ reader/stdio/AgonDev headers under
examples/agnb/api, with caller-owned8KiB workspace and completed-record callbacks.
Existing formats/writers/assembly entries are unchanged. Host sanitizer/legacy
checks and real stock/native consumer qualification pass. The Author accepted
the C++ review on2026-10-23 ("works."); all95 saved result bytes and the completed
application log verify, runtime pins match and the emulator is stopped. Explicit
publication was authorized on2026-10-23 and is scoped to the isolated
codex/agnb-plain-buffers branch. Keep future generic changes here, with
Golem-specific hooks and application policy in Golem GOLEM-046. Preserve the
accepted AGNB-001 history and unrelated utility work; publish only scoped owned
changes after their gate is satisfied.
