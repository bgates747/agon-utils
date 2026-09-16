# Provisional design — Result capture, checkpoints and recovery

> Superseded for implementation planning by [test strategy](test-strategy.md)
> (MAIN-01 W03). Retained as brainstorming provenance; follow the strategy if
> wording differs. Neither document claims the tools are already implemented.


## Summary

Capture compact binary evidence in a known RAM area before calling reporting
code. Write it to the SD card early and often, rather than buffering a whole
suite. Generate readable reports from the same evidence after capture. RAM
recovery is a supplementary route when a fault prevents normal file reporting.
This is design guidance, not an implemented format or proven recovery mechanism.

## Capture and record model

Use a simple versioned format with explicit byte order and field widths, not a
dump of compiler-dependent C++ structures. Proposed record fields are run/case
identity, record type, sequence number, payload length and raw observations.
Record case-start before entering a test, observations as available, and case-end
separately from pass/fail interpretation. A final validity marker and integrity
check should identify partial or damaged records. Exact encoding remains W03 work.

Capture registers/flags immediately, before MOS output, file operations or C++
formatting can change them. The low-level capture routine may need assembly even
though helper applications use C++/AgonDev. Independently validate the capture
mechanism. Commit record validity last; do not assume a multi-byte write is atomic.
Retain advertised expectations separately from observed state so post-processing
can highlight contradictions and omissions without altering the evidence.

## Frequent SD checkpoints

The Author's priority is to write to card early and often. Persist the run header
and case-start before entering the case, then persist completed observations and
case-end promptly. Batch only where measurement constraints justify it, making
that exposure visible. Keep formatting and checkpoint I/O outside measured code.
Do not wait for a whole group or suite by default.

Distinguish a RAM record, a successful file write and a successful filesystem
sync/close. Decide and verify the sync policy; a write return alone is not a
power-loss durability guarantee. Preserve earlier records, detect short writes
and checkpoint errors, and report incomplete runs instead of manufacturing a pass.
SD checkpointing itself invokes MOS/FatFS and changes state: capture test results
first, and establish required case preconditions after any pre-case checkpoint.
Filesystem/raw-block tests need explicit separation from report storage and
must not assume that a failing filesystem can successfully save its own evidence.
A report failure is a reporting failure, distinct from the target observation.

## SRAM address verified for the pinned baseline

The eZ80F92 has 8192 bytes of internal SRAM. For the pinned MOS 3.0.2 Arthur
baseline it is mapped at **$B7E000–$B7FFFF**, not $BE7000.

1. The deployed MOS map defines `__RAM_ADDR_U_INIT_PARAM = $B7` and
   `__RAM_CTL_INIT_PARAM = $80` (lines 103–104). Its SHA-256 is
   `d69e60bbce61a7b4b3eef318ba395f11c4e1a5b585755755113992dc94edcb86`.
2. [Pinned MOS startup](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src_startup/init_params_f92.asm#L149)
   writes these registers. Its cold-start path clears $B7E000–$B7FFFF to $FF.
3. [Pinned platform memory map](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/MOS.md#L160)
   independently identifies that range as internal RAM.
4. [Zilog eZ80F92/F93 specification](https://www.zilog.com/docs/ez80acclaim/ps0153.pdf),
   Random Access Memory section, printed page 190, specifies the F92 window as
   RAM_ADDR_U:E000 through RAM_ADDR_U:FFFF. The mapping is configurable, not an
   invariant of every firmware image.

## SRAM ownership contract

The Author confirms a hard platform contract: onboard SRAM is always user-
allocated space. System code does not use it for runtime storage. MOS clearing
it during reset is the exception; the Author explicitly includes soft resets.
Treat this as guaranteed user-owned memory, not a suspected free area requiring
an audit of system use.

Use $B7E000–$B7FFFF as the planned capture region for the pinned mapping.
Establish a bounded suite-owned layout and a discoverable versioned header;
coordinate allocations with other user code and keep test buffers and stacks
outside the reserved capture portion. Verify the mapping for the selected target,
not system ownership. Tests deliberately altering mapping require an explicit
exception. No physical hardware recovery test has been performed.

## Recovery and capacity

Stop and retrieve RAM before reset/reboot when possible. MOS can wipe this SRAM on reset, including soft resets per the Author's
platform contract; it is volatile and not reset-persistent or power-loss storage. A wild write can corrupt
it, and emulator or host process failure can remove the opportunity to recover.
Verify Fab's ability to read this specific internal SRAM mapping after relevant
faults before advertising recovery. Do not assume ordinary memory commands or
an external-RAM dump include internal SRAM.

Prefer a bounded staging buffer with sequence numbers and checkpoint progress.
Keep the last started case visible, retain unflushed records, and define behavior
when the buffer fills. Never silently overwrite uncheckpointed evidence. Reserve
room for incomplete-case diagnosis; assess a small emergency record if normal
reporting fails. Decoder validation must reject impossible lengths/versions and
handle truncation, missing completion, corruption and duplicate recovered/file
records using run and sequence identities. These are requirements to design and
verify, not existing capabilities.

## Human and agent reports

Binary SD files and recovered memory should decode into the same evidence model.
Humans need a readable summary, detailed discrepancies and explicit completion
status. An on-device decoder/helper is C++ targeting AgonDev. A host-side decoder
may serve agents; both use one format specification and common known-answer
fixtures. Optional concise live progress must not be needed for correctness.

Record firmware, suite, format, configuration and backend identities. Hardware
is authoritative for real-machine behavior; emulator results are independently
useful. Discrepancies lead to documentation clarification, not permission to
change firmware behavior. Formatting is outside the measured operation; measure
rather than assume the final binary implementation's performance advantage.

## Ownership

[MAIN-01](tasks/MAIN-01.md) W03 owns the encoding, capture/checkpoint semantics
and recovery design; W04 sequences implementation. [MAIN-02](tasks/MAIN-02.md)
exposes supported workflows through human and agent entry points. The
[runner design](provisional-runner-design.md) supplies selection/startup context.
Promote resolved decisions into the maintained strategy and human instructions;
mark superseded provisional sections so they do not compete with current guidance.

### SRAM contract violation exception

Any stock MOS or VDP routine writing onboard user SRAM, apart from the allowed
MOS reset wipe, violates the platform ownership contract. Flag such a finding
prominently for immediate rectification, with writer attribution, address range,
target identity and reproducible evidence. This is an explicit exception to the
usual policy of retaining legacy discrepancies and clarifying documentation:
system writes to this user-owned space are not acceptable legacy behavior.
Flagging and prioritizing rectification does not itself authorize implementing
or publishing a firmware patch; obtain separate explicit direction for that work.
