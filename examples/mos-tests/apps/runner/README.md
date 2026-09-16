# Runner foundation — W02

The AgonDev C++ executable supports catalogue listing and selection only:
--list or --resolve all/function:NAME/group:NAME/case:ID. It does not execute tests.
Selection is compiled natively from the same main.cpp for the host planner.
Catalogue data is generated from ../../catalogue/catalogue.json; do not edit
include/catalogue_generated.h manually. human/mos-tests runner-build regenerates
and validates it before building. Host preparation requires g++ on the Linux bench.

include/lifecycle.h implements bounded sequencing using start/execute/finish/
cleanup hooks. Start and finish must become durable boundaries when W04 integrates
recording. Discrepancies continue; infrastructure/invalid result/cleanup failure
halts the batch. Unsupported cases do not execute or run executor cleanup. Native
controls verify these transitions. No production capture, binary checkpoint or
case body is connected yet, so this executable cannot claim MOS passes.

The root smoke build remains separate. Synthetic descriptors are qualification
plans, not real MOS tests. Descriptor capability requirements are explicit and
are never inferred from a successful build or a declared backend alone.

The lifecycle is bounded by plan size; it cannot preempt an executor that hangs.
Descriptor timeouts will be enforced by the backend/capture integration, not
claimed by this synchronous lifecycle library. A failed persistence boundary
stops immediately without more MOS cleanup calls that might destroy evidence.
