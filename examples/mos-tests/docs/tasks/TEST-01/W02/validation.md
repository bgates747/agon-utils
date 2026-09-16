# TEST-01 W02 — capture boundary qualification

Completed: 52 controls passed against explicit mutation expectations and independent
Fab debugger state on a fresh raw SD image. Both seeds, full-width primary register
bytes, flags, stack normalization, deliberate later clobbering and SRAM guards
were checked. See [shared evidence](../../MAIN-03/W03/validation.md) and its
result.json, disassembly and debugger transcript. Qualification limits are retained
there and in [the maintained capture contract](../../../register-capture.md).
Hardware, IFF, alternate registers and alternate CPU modes are not qualified.
