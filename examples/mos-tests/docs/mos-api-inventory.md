# MOS API inventory — MOS 3.0.2 Arthur

## Summary

This is the W01 inventory of the pinned public MOS interface, not a coverage
or execution report. It includes named RST 08 selectors, unsupported slots,
RST services, and the C-function lookup surface. Contracts are owned by upstream and linked by commit below; source findings
are separately labelled. W02 will
turn these entries into cases and observations. No firmware changes are made.

## Baseline and scope

1. MOS source: `v3.0.2`, commit `8336409351ee5314e02801a7b72a4f1bb5282519`; read-only `/home/smith/Agon/agon-mos`.
2. Documentation: commit `f9806bd3cbff6ed5d1c08bef1d51fed11764b86b` in read-only `/home/smith/Agon/agon-docs`. This is a separately pinned living documentation revision, not assumed release-matched.
3. Binary SHA-256: `d564243283972690933a4554296ad6202ca4ef54572279533a942960846bebae`.
   Map SHA-256: `d69e60bbce61a7b4b3eef318ba395f11c4e1a5b585755755113992dc94edcb86`.
   These match SETUP-01. A matching release identity is not a byte-identical local rebuild claim.
4. Scope includes MOS entry points and the data layouts they expose. VDP wire
   protocols, shell-command grammar, BBC BASIC language semantics and AgonDev
   library helpers are dependencies, not extra MOS selectors. `mos_oscli` remains
   in scope as an API; testing every shell command is a separate expansion.
5. ADL with MB=0 is the initial execution baseline. Classic Z80/MB pointer
   promotion is part of the documented interface and is retained for later
   coverage decisions, not silently declared tested. C-function lookup is ADL-only.
6. Historical source/document snapshots are archived, with hashes and a compact
   machine-readable index in
   [W01](tasks/MAIN-01/W01/README.md). Upstream repositories were not changed.

## Entry and ABI rules

1. Documentation and MOSCALL specify `LD A, selector; RST.LIS 08h`. Do not infer
   general compatibility from the RST.LIL output smoke check. Keep call mode and
   MB value explicit in each future fixture.
2. `HL(U)` denotes a pointer whose high byte may be supplied by MB in classic
   mode. ADL callers supply a complete 24-bit pointer with MB=0. Per-function
   conversion matters, especially FIL pointers returned from MOS-managed memory.
3. Only listed outputs/preservation are contract assertions. Unspecified flags
   and registers are observations, not promises. Stack restoration is distinct
   from values legitimately returned in registers. Interrupt/callback lifetimes
   and blocking calls require separate fixture handling in W02/W03.
4. Status is usually A=0 on success, but not universally: character reads,
   predicates, pattern ordering, I2C and raw SD have different result domains.
   FatFS status codes 0–19 are followed by MOS codes 20–26. See the pinned upstream status table linked below. No promise that each call can produce every code.
5. Modern 32-bit values use valid four-byte storage passed by pointer. Legacy
   seek APIs use split registers. C-call arguments are right-to-left, padded to
   multiples of three bytes, and removed by the caller; byte returns use A,
   integer/pointer returns HL. Verify exact prototypes before an AgonDev call.

## RST services

| Entry | Inputs / result | Scope |
| --- | --- | --- |
| 00 | Reset eZ80; no ordinary return contract | Destructive control service; isolated future case |
| 08 | A selects API; other registers below | Dispatcher and all 256 selector values accounted for |
| 10 | A byte to VDP transport | Entry-byte observation differs from rendered output |
| 18 | HL stream; BC 16-bit length, or zero with A delimiter; E receives entry A; HL advances | Two modes; source tests B/C, not BCU; MOS 1.03+ |
| 38 | Crash report; processor/stack state consumed | MOS 2.3+; isolated crash-path observation |
| 20/28/30 | Source contains bare RET | Not advertised public services; excluded from functional inventory |

RST 18 documented A-on-return in length mode conflicts with the source's final
`LD A,B; OR C` (zero at completion). Preserve this as a contract discrepancy.

## Source findings and unresolved contracts

1. LOAD/SAVE comments claim carry-clear for no room, but wrappers execute SCF
   unconditionally. Use returned status for the documented error domain; retain
   carry as a discrepancy, not an inferred success flag.
2. getfunction documentation's final paragraph says out-of-range returns 20;
   source returns 19. Nonzero flags also return 19; MB nonzero returns 20.
   Slots 03/04 return success with NULL. Never call those NULL pointers.
3. ffs_setlabel calls f_setlabel, then falls through to ffs_setcp's unsupported
   handler (A=HL=23). This is a source-observed defect candidate, not a new
   runtime-confirmed bug or authorization to fix firmware.
4. ffs_feof source comment names FILINFO; the helper consumes FIL. Treat FIL
   as the required object; do not allocate FILINFO based on that comment.
5. C-function SD_readBlocks prose calls count bytes; source advances a sector
   and a 512-byte buffer per count. Count is blocks. Raw access must use a
   disposable image, separate from active filesystem tests.
6. The general documentation says old MOS versions "do support" unknown-call
   detection while immediately warning of unexpected results. Do not extrapolate
   this pinned release's A=23 behavior to old firmware from that sentence.
7. Named symbols do not imply implementation. Stub entries below return
   A=HL=23 through the pinned unsupported handler. Version claims must be read in the pinned upstream documentation; they are
   not verified historical release tests.
8. Structure layouts, buffer lifetimes, callback constraints and unspecified
   register effects must remain explicit in case design. Source inspection is
   not exhaustive path verification; resolve any remaining ambiguity before
   selecting an assertion. MOS-01 is parked; !boot.obey stays populated.

## Authority and freshness

This document owns project scope and findings, not upstream API contracts.
Before designing an assertion, identify the actual MOS binary/map and source
revision, then read the linked upstream contract and its implementation. The
pinned documentation revision is independently versioned and may disagree.
Do not substitute current upstream HEAD for the pinned target without review.
A target-version or documentation-baseline change requires reviewing this index
and its discrepancy notes before reusing expectations. Unspecified behavior
remains unspecified. Archive contents are historical evidence only; do not use
them as current guidance or unpack them into maintained project directories.

## Upstream contract map

- [API entry rules, selectors, status codes and sysvars](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md)
- [C-function prototypes and calling convention](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/C-Functions.md)
- [Named system variables](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/System-Variables.md)

## Named RST 08 inventory

100 named selectors, including 10 stubs. “Implemented” means a non-stub source
entry, not proven correctness. See the setlabel finding above.

| A | Name | Source disposition | Pinned contract | Pinned implementation |
| --- | --- | --- | --- | --- |
| 00 | `mos_getkey` | implemented | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L164) | [source](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L356) |
| 01 | `mos_load` | implemented | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L176) | [source](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L376) |
| 02 | `mos_save` | implemented | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L193) | [source](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L406) |
| 03 | `mos_cd` | implemented | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L210) | [source](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L433) |
| 04 | `mos_dir` | implemented | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L224) | [source](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L453) |
| 05 | `mos_del` | implemented | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L240) | [source](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L473) |
| 06 | `mos_ren` | implemented | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L254) | [source](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L494) |
| 07 | `mos_mkdir` | implemented | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L271) | [source](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L543) |
| 08 | `mos_sysvars` | implemented | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L285) | [source](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L562) |
| 09 | `mos_editline` | implemented | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L297) | [source](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L572) |
| 0A | `mos_fopen` | implemented | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L325) | [source](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L596) |
| 0B | `mos_fclose` | implemented | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L360) | [source](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L631) |
| 0C | `mos_fgetc` | implemented | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L374) | [source](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L658) |
| 0D | `mos_fputc` | implemented | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L389) | [source](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L683) |
| 0E | `mos_feof` | implemented | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L404) | [source](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L712) |
| 0F | `mos_getError` | implemented | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L418) | [source](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L736) |
| 10 | `mos_oscli` | implemented | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L434) | [source](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L758) |
| 11 | `mos_copy` | implemented | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L450) | [source](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L519) |
| 12 | `mos_getrtc` | implemented | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L471) | [source](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L775) |
| 13 | `mos_setrtc` | implemented | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L485) | [source](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L803) |
| 14 | `mos_setintvector` | implemented | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L508) | [source](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L820) |
| 15 | `mos_uopen` | implemented | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L523) | [source](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L962) |
| 16 | `mos_uclose` | implemented | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L557) | [source](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L973) |
| 17 | `mos_ugetc` | implemented | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L561) | [source](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#LNone) |
| 18 | `mos_uputc` | implemented | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L572) | [source](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L989) |
| 19 | `mos_getfil` | implemented | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L584) | [source](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L997) |
| 1A | `mos_fread` | implemented | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L600) | [source](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L1009) |
| 1B | `mos_fwrite` | implemented | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L616) | [source](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L1030) |
| 1C | `mos_flseek` | implemented | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L632) | [source](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L1051) |
| 1D | `mos_setkbvector` | implemented | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L654) | [source](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L834) |
| 1E | `mos_getkbmap` | implemented | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L670) | [source](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L851) |
| 1F | `mos_i2c_open` | implemented | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L682) | [source](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L857) |
| 20 | `mos_i2c_close` | implemented | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L694) | [source](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L878) |
| 21 | `mos_i2c_write` | implemented | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L704) | [source](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L898) |
| 22 | `mos_i2c_read` | implemented | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L725) | [source](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L927) |
| 23 | `mos_unpackrtc` | implemented | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L746) | [source](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L790) |
| 24 | `mos_flseek_p` | implemented | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L785) | [source](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L1066) |
| 28 | `mos_pmatch` | implemented | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L812) | [source](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L1084) |
| 29 | `mos_getargument` | implemented | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L844) | [source](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L1108) |
| 2A | `mos_extractstring` | implemented | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L860) | [source](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L1136) |
| 2B | `mos_extractnumber` | implemented | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L889) | [source](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L1176) |
| 2C | `mos_escapestring` | implemented | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L917) | [source](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L1221) |
| 30 | `mos_setvarval` | implemented | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L944) | [source](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L1256) |
| 31 | `mos_readvarval` | implemented | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L983) | [source](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L1300) |
| 32 | `mos_gsinit` | implemented | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1008) | [source](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L1346) |
| 33 | `mos_gsread` | implemented | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1044) | [source](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L1369) |
| 34 | `mos_gstrans` | implemented | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1059) | [source](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L1396) |
| 35 | `mos_substituteargs` | implemented | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1081) | [source](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L1434) |
| 36 | `mos_evaluateexpression` | stub | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1101) | [source](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L347) |
| 38 | `mos_resolvepath` | implemented | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1113) | [source](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L1475) |
| 39 | `mos_getdirforpath` | implemented | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1175) | [source](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L1534) |
| 3A | `mos_getleafname` | implemented | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1197) | [source](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L1566) |
| 3B | `mos_isdirectory` | implemented | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1213) | [source](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L1582) |
| 3C | `mos_getabsolutepath` | implemented | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1228) | [source](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L1607) |
| 40 | `mos_clearvdpflags` | implemented | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1256) | [source](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L1630) |
| 41 | `mos_waitforvdpflags` | implemented | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1272) | [source](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L1644) |
| 50 | `mos_getfunction` | implemented | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1290) | [source](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L2306) |
| 70 | `sd_getunlockcode` | implemented | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1324) | [source](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L2224) |
| 71 | `sd_init` | implemented | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1336) | [source](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L2234) |
| 72 | `sd_readblocks` | implemented | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1351) | [source](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L2247) |
| 73 | `sd_writeblocks` | implemented | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1367) | [source](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L2268) |
| 80 | `ffs_fopen` | implemented | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1400) | [source](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L1657) |
| 81 | `ffs_fclose` | implemented | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1439) | [source](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L1677) |
| 82 | `ffs_fread` | implemented | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1457) | [source](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L1692) |
| 83 | `ffs_fwrite` | implemented | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1476) | [source](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L1720) |
| 84 | `ffs_flseek` | implemented | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1512) | [source](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L1747) |
| 85 | `ffs_ftruncate` | implemented | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1532) | [source](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L1763) |
| 86 | `ffs_fsync` | implemented | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1548) | [source](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L1775) |
| 87 | `ffs_fforward` | stub | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1564) | [source](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L1783) |
| 88 | `ffs_fexpand` | stub | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1574) | [source](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L1785) |
| 89 | `ffs_fgets` | implemented | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1584) | [source](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L1795) |
| 8A | `ffs_fputc` | implemented | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1604) | [source](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L1816) |
| 8B | `ffs_fputs` | implemented | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1621) | [source](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L1831) |
| 8C | `ffs_fprintf` | stub | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1638) | [source](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L1844) |
| 8D | `ffs_ftell` | implemented | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1644) | [source](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L1854) |
| 8E | `ffs_feof` | implemented | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1659) | [source](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L1871) |
| 8F | `ffs_fsize` | implemented | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1675) | [source](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L1884) |
| 90 | `ffs_ferror` | implemented | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1690) | [source](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L1901) |
| 91 | `ffs_dopen` | implemented | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1706) | [source](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L1912) |
| 92 | `ffs_dclose` | implemented | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1721) | [source](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L1930) |
| 93 | `ffs_dread` | implemented | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1735) | [source](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L1946) |
| 94 | `ffs_dfindfirst` | implemented | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1750) | [source](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L1968) |
| 95 | `ffs_dfindnext` | implemented | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1773) | [source](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L1993) |
| 96 | `ffs_stat` | implemented | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1792) | [source](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L2011) |
| 97 | `ffs_unlink` | implemented | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1820) | [source](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L2029) |
| 98 | `ffs_rename` | implemented | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1834) | [source](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L2044) |
| 99 | `ffs_chmod` | stub | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1851) | [source](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L2058) |
| 9A | `ffs_utime` | stub | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1861) | [source](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L2060) |
| 9B | `ffs_mkdir` | implemented | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1871) | [source](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L2068) |
| 9C | `ffs_chdir` | implemented | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1883) | [source](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L2082) |
| 9D | `ffs_chdrive` | stub | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1897) | [source](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L2091) |
| 9E | `ffs_getcwd` | implemented | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1901) | [source](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L2099) |
| 9F | `ffs_mount` | implemented | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1916) | [source](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L2120) |
| A0 | `ffs_mkfs` | stub | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1932) | [source](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L2123) |
| A1 | `ffs_fdisk` | stub | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1940) | [source](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L2125) |
| A2 | `ffs_getfree` | implemented | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1948) | [source](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L2137) |
| A3 | `ffs_getlabel` | implemented | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1966) | [source](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L2164) |
| A4 | `ffs_setlabel` | implemented | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1982) | [source](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L2190) |
| A5 | `ffs_setcp` | stub | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1998) | [source](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L2196) |
| A6 | `ffs_flseek_p` | implemented | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L2008) | [source](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.asm#L2205) |

The other 156 selector values reach the unsupported handler: explicit unused
slots in 00–A6, or the A7–FF range check. The compact W01 register preserves
all 167 explicit dispatch slots; unnamed values are dispatcher cases, not
invented API functions.

## C-function lookup inventory

The B selector of mos_getfunction is a separate namespace from A/RST 08.
Slots 03/04 return success with NULL. Do not call those pointers. All other
entries require the upstream prototype and Zilog ABI; source presence does not
prove an AgonDev call site is correct.

| B | Source target | Pinned contract |
| --- | --- | --- |
| 00 | `_SD_init` | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/C-Functions.md#L104) |
| 01 | `_SD_readBlocks` | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/C-Functions.md#L108) |
| 02 | `_SD_writeBlocks` | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/C-Functions.md#L114) |
| 03 | `0` | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/C-Functions.md#L120) |
| 04 | `0` | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/C-Functions.md#L126) |
| 05 | `_f_printf` | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/C-Functions.md#L132) |
| 06 | `_f_findfirst` | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/C-Functions.md#L136) |
| 07 | `_f_findnext` | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/C-Functions.md#L142) |
| 08 | `_open_UART1` | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/C-Functions.md#L148) |
| 09 | `_setVarVal` | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/C-Functions.md#L152) |
| 0A | `_readVarVal` | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/C-Functions.md#L166) |
| 0B | `_gsTrans` | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/C-Functions.md#L178) |
| 0C | `_substituteArgs` | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/C-Functions.md#L198) |
| 0D | `_resolvePath` | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/C-Functions.md#L206) |
| 0E | `_getDirectoryForPath` | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/C-Functions.md#L223) |
| 0F | `_resolveRelativePath` | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/C-Functions.md#L240) |
| 10 | `func_getsysvars` | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/C-Functions.md#L250) |
| 11 | `func_getkbmap` | [docs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/C-Functions.md#L256) |

## Layout dependencies

- [System-state storage](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src_startup/globals.asm)
- [Assembly offsets and structures](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src/mos_api.inc)
- [Configured FatFS object layouts](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src_fatfs/ff.h)
- [FatFS build configuration](https://github.com/AgonPlatform/agon-mos/blob/8336409351ee5314e02801a7b72a4f1bb5282519/src_fatfs/ffconf.h)

Use target layouts, never host C structures. Named MOS variables and system-state
sysvars are different interfaces. Cases must explicitly identify buffer ownership,
size, lifetime and callback requirements from the linked contracts.
