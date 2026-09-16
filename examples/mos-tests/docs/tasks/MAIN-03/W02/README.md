# MAIN-03 W02 — Catalogue and lifecycle

Maintained implementation: catalogue/catalogue.json, apps/runner C++ selector and
lifecycle, scripts/plan_run.py and human/mos-tests plan/runner-build. Operational
guidance lives in human/planning.md. No dependency on this task silo at runtime.

The same selection code builds for host planning and Agon. Plans are durable
configuration artifacts, explicitly NOT EXECUTED; binary run.json/records and
runtime identity recording connect in later work. Lifecycle hooks are tested
natively; production case executors and durable hooks are not installed yet.

See validation.txt and artifacts.json. Synthetic inputs/expectations are hashed
and verified during catalogue preparation. Timeouts are descriptor requirements,
not a claim that the synchronous core can preempt a hung executor.
