# MAIN-05 W02 evidence

Implementation and headless qualification of the startup recovery gate.
The durable contract remains docs/restart-recovery.md. Reusable code is under
apps/startup-runner/, scripts/, agents/, tests/recovery/ and human/.

compiler-failure.tar.gz retains a genuine AgonDev LLVM backend crash encountered during
implementation, before target execution. A transition table avoids the failing
boolean expression; native checks independently exercise all 121 table entries.
No toolchain patch or upstream publication is authorized or performed.

W03 explicit dispositions and W04 broad interruption qualification remain separate.
