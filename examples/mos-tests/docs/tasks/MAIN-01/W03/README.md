# W03 — Execution and evidence design

Maintained output: [test strategy](../../../test-strategy.md).

Reviewed existing prepare_sd_image.py/run_emulator.py, SETUP-01 BASIC startup,
local debugger reference, pinned MOS EXEC/OBEY implementation and command docs.
Key source finding: EXEC stops on nonzero status and keeps a script file open.
The design therefore separates persisted discrepancies from infrastructure exit
failure and separates remount/raw/control cases from normal scripted batches.
No runtime validation was performed. Format payload schemas and precise capture
instructions are implementation artifacts requiring golden tests/disassembly;
the architecture, envelope, memory budget and failure policies are specified.
