# MOS function coverage matrix

## Summary

W02 proposes coverage for all 100 named RST 08 selectors, the other 156
selector values, 18 C-function lookup slots and public RST services. Nothing
in this matrix has been executed. Each row defines a bounded case family;
W03 will define concrete fixture bytes, runner encoding and capture mechanics.

The [inventory](mos-api-inventory.md) owns pinned identities and upstream links.
This matrix owns original test proposals, not a second API manual. The MOS
3.0.2 and documentation checkouts were rechecked against W01 and were clean.
A target or documentation change requires contract review before reuse.

## Reading and using the matrix

1. Every row combines its explicit scenarios with the common axes below and
   its fixture profile. E means headless raw-image emulator; H means hardware.
   E+H is a proposed capability, not evidence of a pass or backend equivalence.
   Conditional E requires proving stimulus/observation support; otherwise mark
   unsupported, not passed. Hardware remains authoritative for machine behavior.
2. “Planned” means not implemented/executed. Future records distinguish pass,
   discrepancy, skip with reason, unsupported backend, blocked prerequisite,
   harness/reporting failure, and incomplete/hung/faulted execution. A source
   suspicion is not a runtime result. A completed case is not necessarily a pass.
3. Each semicolon-delimited scenario becomes one or more independently named
   cases during implementation. Function selection includes all applicable paths;
   large-image, destructive-control and peripheral cases must remain visible
   even if skipped in ordinary batches. No test-count claim is made here.
4. Each normal/error/boundary path gets preservation checks using at least two
   distinct valid seed patterns. Capture full 24-bit registers including upper
   bytes and IX/IY, promised flag bits, and stack balance at comparable call
   boundaries. Respect inputs, outputs, read/write argument lifetimes and mode.
   Missing preservation promises produce observations/omission reports, not
   fabricated conformance failures. RST and C ABI expectations are separate.
5. For defaults, compare advertised zero/null/omitted choices with the explicit
   equivalent where documented. A register argument cannot simply be “omitted”:
   initialize it. Record process initial state separately from API defaults.
   Unspecified defaults and contradictory prose/source require a clarification
   finding, not a guessed expected value. Specific defaults are named in rows.
6. Use explicit expected bytes, pointer offsets, status and side effects. A second
   MOS call is useful corroboration, not the sole oracle for a filesystem write:
   inspect the raw image or card independently after releasing handles. Do not
   require directory order, exact unstable time, or expanded-file contents when
   the contract does not define them. Guard buffers at valid minimum sizes.
7. Capture to suite-reserved user SRAM before reporting; checkpoint early/often,
   including before entering cases and after results. Do not checkpoint inside
   a register observation or timing window. All onboard SRAM is user-owned;
   unexplained stock MOS/VDP writes outside allowed reset wiping are contract
   violations for immediate rectification. Detect with guarded unused regions
   and writer attribution where supported, excluding intentional fixture writes.
8. No discrepancy authorizes a firmware patch. Preserve evidence and draft clear
   documentation findings, especially preservation/default omissions. SRAM
   ownership violations have higher priority under the explicit policy exception.
9. ADL/MB=0 is the initial route. Add separate classic-mode fixture coverage for
   documented MB pointer promotion; defer execution until a qualified mixed-mode
   harness exists. Legacy split seeks have mode restrictions; do not manufacture
   an invalid classic call as a normal case. No historical MOS version sweep yet.
10. Arbitrary pointers, unterminated/unbounded buffers, illegal flags and invalid
    object lifetimes are excluded from ordinary conformance unless explicitly
    documented as valid failure inputs. Future robustness probes run isolated
    and are labelled characterization. Reporting errors cannot erase test evidence.

## Fixture and backend profiles

| Profile | Proposed backend | Setup / observation / isolation |
| --- | --- | --- |
| M: Memory | E+H | Guarded user buffers, seeded registers; capture values/pointers/bytes; no mutable filesystem fixture. |
| F: Filesystem | E+H | Fresh raw FAT image/physical test card with manifest of empty, patterned, long-name, attributed files and directories; inspect bytes/metadata independently; reset cwd and file ownership per case. |
| S: Strings/variables | E+H | Guarded mutable strings and task-prefixed variables; explicit lengths/types; finish translation contexts and remove variables; compare literal expected bytes/pointer offsets. |
| K: Keyboard | H; E conditional | Known input sequence from human/device; emulator automation requires verified key injection; capture character/bitmap/editor buffer, not merely screen appearance. |
| V: VDP/RTC | E+H conditional | Controlled native VDP and RTC state/packet sequence; capture returned bytes/flags; asynchronous transitions need bounded observations; real display/time behavior needs hardware. |
| I: Interrupts/callbacks | H; E conditional | Safe minimal handler and controlled stimulus; save/restore original vector; external timeout/reboot recovery; emulator interrupt fidelity must be established. |
| U: UART | H; E conditional | Loopback or controlled serial peer and optional analyzer; explicit port setup; emulator must demonstrate UART/flow-control support before claiming these cases. |
| Q: I2C | H; E conditional | Known responder/NACK/error fixture and logic analyzer; bus reset after each scenario; no assumed emulator I2C support. |
| R: Raw media/remount | E+H isolated | Disposable image/card with known sectors; separate capture/checkpoint phase from raw operations, no open filesystem objects; dump SRAM before reset if reporting unavailable. |

All E filesystem qualification uses --sdcard-img and populated !boot.obey.
Hardware copying/startup selection follows the same bundle design; exact commands
remain pending verification. No graphical emulator launch is required merely to
run this matrix. Reset clears SRAM, so recovery precedes reset. Human-readable
and binary results share one schema; on-device helper applications use AgonDev C++.

## Named RST 08 function families

Every entry is **planned**, including stub detection. Preservation cells are
short extracts of the advertised claim, linked to pinned upstream documentation;
only those register widths/bits actually promised become assertions. Pinned
implementation conflicts remain visible in the inventory and scenario notes.

| A / function | Fixture | Proposed paths and expectations | Advertised preservation to audit |
| --- | --- | --- | --- |
| 00 `mos_getkey` | K | Press/release A then Enter: expected character sequence; no key: remains blocked until controlled input; modifier/non-ASCII keys: record delivered code against fixture mapping. | [No explicit preservation list; observe clobbers without inventing a promise.](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L164) |
| 01 `mos_load` | F | Load known 0/1/511/512/513-byte files into guarded RAM: exact bytes; exact capacity succeeds, undersized capacity reports failure without guard damage; missing file/path distinguish status 4/5. Capture carry discrepancy separately. | [`HL(U)`, `DE(U)`, `BC(U)`](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L176) |
| 02 `mos_save` | F | Save 0/1/511/512/513 known bytes: image contains exact data; existing destination behavior checked against contract; missing parent fails; no buffer guard mutation. Capture carry separately. | [`HL(U)`, `DE(U)`, `BC(U)`](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L193) |
| 03 `mos_cd` | F | Change to existing directory: subsequent relative lookup resolves there; missing directory fails; root and parent traversal; verify no unexpected cwd change on failure. | [`HL(U)`](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L210) |
| 04 `mos_dir` | F | List empty and populated directories: expected entry set at output boundary; missing path errors; ordering and formatting without promises remain observations. | [`HL(U)`](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L224) |
| 05 `mos_del` | F | Delete existing file: disappears; missing file fails; directory/read-only cases use documented permitted behavior and preserve unrelated files. | [`HL(U)`](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L240) |
| 06 `mos_ren` | F | Rename/move known file: bytes unchanged, old path absent; missing source and occupied destination: status and image changes; case-only name handling characterized. | [`HL(U)`, `DE(U)`](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L254) |
| 07 `mos_mkdir` | F | Create directory: exists and empty; existing name and missing parent errors; root-relative versus cwd-relative path. | [`HL(U)`](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L271) |
| 08 `mos_sysvars` | M | Returned pointer identifies pinned sysvars; read known stable fields and changing counters; do not assert equality of asynchronous fields between captures. | [No explicit preservation list; observe clobbers without inventing a promise.](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L285) |
| 09 `mos_editline` | K | Enter and Escape yield 13/27; supplied text retained with flags zero and cleared with bit0; capacity-edge editing preserves guards; exercise tab/history/hotkey flags individually with scripted input. | [`HL(U)`, `BC(U)`, `DE(U)`](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L297) |
| 0A `mos_fopen` | F | Each supported open mode on existing/missing files: handle or zero plus create/truncate/append effects; exhaust handle pool in isolated run; release all acquired handles. | [`HL(U)`, `BC(U)`, `DE(U)`, `IX(U)`, `IY(U)`](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L325) |
| 0B `mos_fclose` | F | Close one open handle then reuse slot; handle zero closes all per contract; already-closed handle characterized without dereferencing arbitrary objects. | [`HL(U)`, `BC(U)`, `DE(U)`, `IX(U)`, `IY(U)`](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L360) |
| 0C `mos_fgetc` | F | Read empty/one/two-byte files: bytes and carry before/at last byte and after EOF; distinguish byte zero from EOF; invalid handle result characterized separately. | [`HL(U)`, `BC(U)`, `DE(U)`, `IX(U)`, `IY(U)`](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L374) |
| 0D `mos_fputc` | F | Write 00/7F/80/FF bytes through writable handle: exact bytes after checkpoint; read-only/closed handle observations with no invented returned status. | [`HL(U)`, `BC(U)`, `DE(U)`, `IX(U)`, `IY(U)`](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L389) |
| 0E `mos_feof` | F | Empty file true; nonempty before end false, at end true; seek backward clears EOF; invalid handle classified separately. | [`HL(U)`, `BC(U)`, `DE(U)`, `IX(U)`, `IY(U)`](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L404) |
| 0F `mos_getError` | M | Codes 0–26: expected pinned message bytes; exact/short/zero buffer capacity with guards; out-of-range code observation, no invented error return. | [`DE(U)`, `HL(U)`, `BC(U)`](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L418) |
| 10 `mos_oscli` | F | Controlled benign command and small known-return program: returned status and effect; unknown command returns 20; vary unused BC/DE to audit stale documented parameters; no exhaustive shell grammar scope. | [`HL(U)`](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L434) |
| 11 `mos_copy` | F | Copy empty/multisector file: exact destination and intact source; missing source; wildcard source into directory yields expected set; invalid wildcard destination/error behavior recorded. | [`HL(U)`, `BC(U)`, `DE(U)`, `IX(U)`, `IY(U)`](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L450) |
| 12 `mos_getrtc` | V | Known RTC setting produces corresponding string and length in >=32-byte guarded buffer; rollover uses bounded interval comparison, not exact host-clock equality. | [`HL(U)`](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L471) |
| 13 `mos_setrtc` | V | Set valid date/time then read back within elapsed tolerance; leap-day and year transition; malformed date values are characterization unless validation is promised; restore baseline time. | [`HL(U)`](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L485) |
| 14 `mos_setintvector` | I | Install safe handler on permitted vector, check returned old handler and invocation then restore; invalid vector returns documented rejection; callbacks capture minimal state without MOS reporting. | [`HLU`, `DEU`](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L508) |
| 15 `mos_uopen` | U | Open with explicit supported baud/data/parity/flow settings: A=0 and loopback behavior; capture configuration variation; unsupported settings characterized, not presumed rejected. | [`HL(U)`](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L523) |
| 16 `mos_uclose` | U | Close initialized UART and reopen: no stale transfer state; repeated close characterization; no invented success status. | [No explicit preservation list; observe clobbers without inventing a promise.](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L557) |
| 17 `mos_ugetc` | U | Peer supplies 00/7F/80/FF: exact receive values; absent data exposes documented blocking behavior under external timeout. | [No explicit preservation list; observe clobbers without inventing a promise.](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L561) |
| 18 `mos_uputc` | U | Transmit 00/7F/80/FF: external peer receives exact bytes; flow-control stall/release; record status per pinned contract. | [No explicit preservation list; observe clobbers without inventing a promise.](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L572) |
| 19 `mos_getfil` | F | Open handle maps to valid FIL with expected size/offset; zero/closed/out-of-range handles return documented null behavior; never pass invalid pointer onward. | [`BC(U)`](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L584) |
| 1A `mos_fread` | F | Read lengths 0/1/511/512/513 and beyond EOF: exact bytes and returned count; buffer guards intact; read-only valid handle normal, invalid handle separate. | [`HL(U)`, `BC(U)`](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L600) |
| 1B `mos_fwrite` | F | Write lengths 0/1/511/512/513: returned count and exact file contents; read-only handle/disk-full checkpoint failures distinguished from test writes. | [`HL(U)`, `BC(U)`](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L616) |
| 1C `mos_flseek` | F | Split-register seeks to zero/middle/end and >24-bit offset on suitable image; verify offset and next byte; read-only past-end versus writable expansion; expanded bytes unspecified. | [`HL(U)`, `BC(U)`, `DE(U)`](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L632) |
| 1D `mos_setkbvector` | I | Install keyboard callback, deliver key events, record callback and returned old pointer as contracted; restore; null/reset behavior only as documented. | [No explicit preservation list; observe clobbers without inventing a promise.](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L654) |
| 1E `mos_getkbmap` | K | Returned bitmap changes for controlled press/release and multiple keys; guard read bounds; correlate key identifiers with pinned keyboard definitions. | [No explicit preservation list; observe clobbers without inventing a promise.](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L670) |
| 1F `mos_i2c_open` | Q | Each documented frequency ID: verify actual bus clock with peer/analyzer; zero/out-of-range IDs characterized; preserve promised registers. | [`HL(U)`, `BC(U)`, `DE(U)`, `IX(U)`, `IY(U)`](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L682) |
| 20 `mos_i2c_close` | Q | Close initialized bus: observe disabled behavior then reopen; repeat-close observation without invented return status. | [`HL(U)`, `BC(U)`, `DE(U)`, `IX(U)`, `IY(U)`](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L694) |
| 21 `mos_i2c_write` | Q | Acking peer receives exact 1/32-byte data; address NACK/data NACK scenarios produce documented status; zero/>32 count needs contract decision before execution. | [`HL(U)`, `DE(U)`, `IX(U)`, `IY(U)`](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L704) |
| 22 `mos_i2c_read` | Q | Peer returns exact 1/32 bytes and guards stay intact; absent peer/NACK; bus arbitration/error cases only with controlled equipment. | [`HL(U)`, `DE(U)`, `IX(U)`, `IY(U)`](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L725) |
| 23 `mos_unpackrtc` | V | Flags zero unpacks a known cached RTC; before-refresh uses fresh time, after-refresh returns cached data then updates asynchronously; flags combination and 10-byte guards. | [`HL(U)`, `BC(U)`](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L746) |
| 24 `mos_flseek_p` | F | Pointer-based 32-bit seek zero/middle/end/>24-bit; exact offset/next byte; read-only clipping and writable expansion; no expectations for newly expanded byte contents. | [`HL(U)`, `BC(U)`](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L785) |
| 28 `mos_pmatch` | M | Literal equal/unequal and empty strings; one case per flag and meaningful interactions for case/star/hash/dot/prefix/space; assert match or ordering sign, not arbitrary mismatch magnitude. | [`HL(U)`, `DE(U)` and `BC(U)`](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L812) |
| 29 `mos_getargument` | M | Known argument sequence: exact start/end pointer offsets; first/last/missing index; spaces and quoted arguments; index origin follows pinned contract/source, ambiguity recorded before concrete fixture. | [`BC(U)`](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L844) |
| 2A `mos_extractstring` | M | Null divider versus explicit space; custom divider; each defined flag and quoting interactions; unmatched quote returns 25, no result 19; verify source mutation/returned offsets and guards. | [`BC(U)`](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L860) |
| 2B `mos_extractnumber` | M | Zero/positive/negative and supported bases: numeric value/end pointer; flags for decimal/positive/h suffix; invalid syntax returns 19; 24-bit limits and overflow classified by contract. | [`BC(U)`](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L889) |
| 2C `mos_escapestring` | M | Printable/control/pipe inputs: literal expected escaped bytes; null destination measures length; exact and short buffer, short returns 22 with expected prefix and intact guards. | [No explicit preservation list; observe clobbers without inventing a promise.](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L917) |
| 30 `mos_setvarval` | S | Set/read string, number, macro, literal and supported expanded forms; wildcard iteration; delete with type255; returned actual type/name; protected code-variable deletion and missing names. | [Other registers preserved (interpret against listed outputs).](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L944) |
| 31 `mos_readvarval` | S | Read each type, numeric 3-byte buffer, expansion flag3; null buffer length query; short buffer returns 22 with full required length; missing variable and wildcard iteration. | [No explicit preservation list; observe clobbers without inventing a promise.](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L983) |
| 32 `mos_gsinit` | S | Initialize literal/variable/control-code translation; flags zero and each valid bit; finish every translation; tracked reinit versus explicitly completed no-tracking contexts, no deliberate leaked context in normal batch. | [No explicit preservation list; observe clobbers without inventing a promise.](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1008) |
| 33 `mos_gsread` | S | Read initialized translation to final C=0: exact byte sequence and A status; malformed source propagates error; do not use freed/completed context again. | [No explicit preservation list; observe clobbers without inventing a promise.](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1044) |
| 34 `mos_gstrans` | S | Literal/variable translation: exact expected bytes and total length; null destination measures; short destination succeeds with truncation per advertised contract; no-tracking bit ignored. | [No explicit preservation list; observe clobbers without inventing a promise.](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1059) |
| 35 `mos_substituteargs` | S | Template with referenced and unused args: default appends rest, bit0 omits rest; null destination length; exact/short buffers, resulting prefix and full calculated length. | [No explicit preservation list; observe clobbers without inventing a promise.](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1081) |
| 36 `mos_evaluateexpression` | M | Call named unsupported selector: advertised A=23; record HL=23 as source observation, not invented preservation; no underlying filesystem operation expected. | [No explicit preservation list; observe clobbers without inventing a promise.](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1101) |
| 38 `mos_resolvepath` | F | Resolve explicit/prefixed/variable paths; wildcard iteration as a set, not alphabetical order; flags zero includes all attributes; missing file=4, missing directory=5, short buffer=22; count-only and prefix index iteration. | [No explicit preservation list; observe clobbers without inventing a promise.](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1113) |
| 39 `mos_getdirforpath` | S | Resolve directory part using prefix indices; no filesystem existence check; null count-only and short buffer; missing prefix/index rejection, trailing leaf omitted. | [No explicit preservation list; observe clobbers without inventing a promise.](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1175) |
| 3A `mos_getleafname` | M | Plain/absolute/prefixed path: returned pointer to leaf; empty and trailing slash/colon point to terminator; nonexistent path still purely lexical. | [No explicit preservation list; observe clobbers without inventing a promise.](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1197) |
| 3B `mos_isdirectory` | F | Existing directory=0; file/missing path=5; only fully resolved input in conformance cases. | [No explicit preservation list; observe clobbers without inventing a promise.](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1213) |
| 3C `mos_getabsolutepath` | F | Relative dot/parent path yields expected absolute path; short buffer=22; null destination in ADL=19; missing path/file outcomes; classic null-pointer crash probe excluded from normal batch. | [No explicit preservation list; observe clobbers without inventing a promise.](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1228) |
| 40 `mos_clearvdpflags` | V | Known flags then clear mask: A equals remaining bits; zero mask leaves flags; account for asynchronous packet arrival rather than assuming no concurrent events. | [No explicit preservation list; observe clobbers without inventing a promise.](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1256) |
| 41 `mos_waitforvdpflags` | V | Requested response yields A=0; deliberately absent response yields 15 near documented timeout; already-set flags and zero/multi-bit mask semantics characterized; no strict emulator wall-time equivalence. | [No explicit preservation list; observe clobbers without inventing a promise.](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1272) |
| 50 `mos_getfunction` | M | All B=00–11 with C=0; 03/04 succeed with null; flags nonzero return19; B>=12 source19 versus prose20 discrepancy; classic caller rejection20 via isolated fixture. | [No explicit preservation list; observe clobbers without inventing a promise.](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1290) |
| 70 `sd_getunlockcode` | R | Fetch unlock token into guarded three-byte area; use it in paired raw requests; token numeric value is opaque and not fixed expectation. | [No explicit preservation list; observe clobbers without inventing a promise.](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1324) |
| 71 `sd_init` | R | Valid token init succeeds; wrong token returns2; absent/bad media error requires controlled backend; initialization changes filesystem state, no active report file. | [No explicit preservation list; observe clobbers without inventing a promise.](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1336) |
| 72 `sd_readblocks` | R | Read 1/2 blocks from known LBA: exact 512-byte blocks and guard bytes; wrong unlock=2; zero count characterize; invalid media/bounds use disposable controlled image. | [No explicit preservation list; observe clobbers without inventing a promise.](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1351) |
| 73 `sd_writeblocks` | R | Write 1/2 known blocks then inspect raw image: only intended sectors changed; wrong unlock=2 with unchanged data; no writes to active report or boot volume regions. | [No explicit preservation list; observe clobbers without inventing a promise.](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1367) |
| 80 `ffs_fopen` | F | Open each supported mode with caller-owned empty FIL: status, contents and lifecycle; missing path/file, existing create-new; keep MOS handle and direct FIL ownership separate. | [`HL(U)`, `DE(U)`, `C`](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1400) |
| 81 `ffs_fclose` | F | Close directly opened FIL and verify persisted writes; invalid/closed initialized object only where FatFS documents behavior; never close a MOS-managed handle's FIL directly. | [`HL(U)`](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1439) |
| 82 `ffs_fread` | F | Read direct FIL with 0/1/511/512/513 bytes and past EOF: exact bytes, status and returned count; guarded output; no arbitrary invalid FIL pointers. | [`HL(U)`, `DE(U)`](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1457) |
| 83 `ffs_fwrite` | F | Write direct FIL with boundary lengths: exact bytes/count/status; read-only and full-image cases; preserve separate reporting route. | [`HL(U)`, `DE(U)`](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1476) |
| 84 `ffs_flseek` | F | Legacy split offset seek zero/middle/end/>24-bit: position and next byte; writable expansion versus read-only constraints; mark mode limitations. | [`HL(U)`, `DE(U)`, `BC(U)`](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1512) |
| 85 `ffs_ftruncate` | F | Truncate at middle/zero/end: size and prefix exact; read-only error; observe persistence after close. | [`HL(U)`](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1532) |
| 86 `ffs_fsync` | F | Write then sync: verify image after orderly release; repeated sync and read-only valid file; no power-loss durability claim from a successful return alone. | [No explicit preservation list; observe clobbers without inventing a promise.](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1548) |
| 87 `ffs_fforward` | M | Call named unsupported selector: advertised A=23; record HL=23 as source observation, not invented preservation; no underlying filesystem operation expected. | [No explicit preservation list; observe clobbers without inventing a promise.](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1564) |
| 88 `ffs_fexpand` | M | Call named unsupported selector: advertised A=23; record HL=23 as source observation, not invented preservation; no underlying filesystem operation expected. | [No explicit preservation list; observe clobbers without inventing a promise.](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1574) |
| 89 `ffs_fgets` | F | Read lines including LF/CRLF, empty file and final unterminated line; length1/exact/short buffer; returned pointer/null and guarded bytes against configured FatFS string rules. | [`HL(U)`, `BC(U)`](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1584) |
| 8A `ffs_fputc` | F | Write character using direct FIL: bytes and signed count/error result; read-only/full media cases, don't confuse negative result with large unsigned count. | [`HL(U)`](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1604) |
| 8B `ffs_fputs` | F | Write empty/plain/newline string: exact configured byte behavior and count; read-only/full image result. | [`HL(U)`, `DE(U)`](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1621) |
| 8C `ffs_fprintf` | M | Call named unsupported selector: advertised A=23; record HL=23 as source observation, not invented preservation; no underlying filesystem operation expected. | [No explicit preservation list; observe clobbers without inventing a promise.](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1638) |
| 8D `ffs_ftell` | F | After open/read/seek: four-byte offset matches known position; documented null argument rejection19 in supported mode; guards and preservation. | [`HL(U)`, `DE(U)`](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1644) |
| 8E `ffs_feof` | F | Empty/start/end/seek-back: 1/0 EOF predicate; compare documented behavior without depending on L input; valid FIL required. | [`HL(U)`](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1659) |
| 8F `ffs_fsize` | F | Known sizes including >24-bit on suitable image: exact four-byte size; null argument rejection19; buffer guards. | [`HL(U)`](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1675) |
| 90 `ffs_ferror` | F | Clean FIL error zero; controlled disk fault then inspect latched error; later result after recovery characterized; injection capability required for hard-error branch. | [`HL(U)`](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1690) |
| 91 `ffs_dopen` | F | Open empty/populated directory with blank DIR: success; missing directory failure; object guards and subsequent enumeration. | [`HL(U)`, `DE(U)`](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1706) |
| 92 `ffs_dclose` | F | Close directly opened DIR: success and reusable resources; lifecycle misuse only where documented. | [`HL(U)`](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1721) |
| 93 `ffs_dread` | F | Enumerate known entry set and end marker; empty directory; long names/attributes; order unspecified; validate bounded FILINFO layout. | [`HL(U)`, `DE(U)`](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1735) |
| 94 `ffs_dfindfirst` | F | Find first literal/wildcard match: membership of known set or empty end marker; empty/missing directory; persist DIR for next. | [`HL(U)`, `DE(U)`, `BC(U)`, `IX(U)`](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1750) |
| 95 `ffs_dfindnext` | F | Continue find-first sequence: each expected match once until empty name; no required alphabetical order; valid live DIR only. | [`HL(U)`, `DE(U)`](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1773) |
| 96 `ffs_stat` | F | Known file/directory metadata and size; missing file/path status; guarded FILINFO; timestamps interpreted against configured RTC/time resolution. | [`HL(U)`, `DE(U)`](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1792) |
| 97 `ffs_unlink` | F | Unlink file/empty directory: removed; nonempty directory and read-only rejection; unrelated content survives. | [`HL(U)`](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1820) |
| 98 `ffs_rename` | F | Rename/move direct resolved paths: contents intact; missing source/colliding destination errors; paths with MOS prefixes excluded from native FatFS conformance. | [`HL(U)`, `DE(U)`](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1834) |
| 99 `ffs_chmod` | M | Call named unsupported selector: advertised A=23; record HL=23 as source observation, not invented preservation; no underlying filesystem operation expected. | [No explicit preservation list; observe clobbers without inventing a promise.](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1851) |
| 9A `ffs_utime` | M | Call named unsupported selector: advertised A=23; record HL=23 as source observation, not invented preservation; no underlying filesystem operation expected. | [No explicit preservation list; observe clobbers without inventing a promise.](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1861) |
| 9B `ffs_mkdir` | F | Create resolved directory: empty entry; existing name/missing parent rejection; metadata check. | [No explicit preservation list; observe clobbers without inventing a promise.](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1871) |
| 9C `ffs_chdir` | F | Change resolved cwd and use relative lookup; missing directory failure; restore cwd. | [No explicit preservation list; observe clobbers without inventing a promise.](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1883) |
| 9D `ffs_chdrive` | M | Call named unsupported selector: advertised A=23; record HL=23 as source observation, not invented preservation; no underlying filesystem operation expected. | [No explicit preservation list; observe clobbers without inventing a promise.](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1897) |
| 9E `ffs_getcwd` | F | Get known cwd into exact/short/large buffer: content/status/guard; boundary including terminator; initial cwd is established by boot script, not universal firmware default. | [`HL(U)`, `BC(U)`](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1901) |
| 9F `ffs_mount` | R | All-zero arguments remount prepared volume; zero versus valid nonzero ignored parameters; malformed/no-FAT image errors in isolated boot; no open handles or active checkpoint file. | [No explicit preservation list; observe clobbers without inventing a promise.](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1916) |
| A0 `ffs_mkfs` | M | Call named unsupported selector: advertised A=23; record HL=23 as source observation, not invented preservation; no underlying filesystem operation expected. | [No explicit preservation list; observe clobbers without inventing a promise.](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1932) |
| A1 `ffs_fdisk` | M | Call named unsupported selector: advertised A=23; record HL=23 as source observation, not invented preservation; no underlying filesystem operation expected. | [No explicit preservation list; observe clobbers without inventing a promise.](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1940) |
| A2 `ffs_getfree` | F | NULL and empty path query known image: free clusters and cluster-size units checked against BPB/FAT; before/after allocation change; other path behavior recorded as restricted input. | [No explicit preservation list; observe clobbers without inventing a promise.](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1948) |
| A3 `ffs_getlabel` | F | NULL and empty path yield known label/serial; empty/max11-character label; 23-byte guarded buffer; no undersized buffer conformance probe. | [No explicit preservation list; observe clobbers without inventing a promise.](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1966) |
| A4 `ffs_setlabel` | F | Set/remove/max-length label: independently inspect volume changes and returned status; source fallthrough23 highlighted separately from intended FRESULT; invalid label rejection; preserve legacy behavior. | [No explicit preservation list; observe clobbers without inventing a promise.](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1982) |
| A5 `ffs_setcp` | M | Call named unsupported selector: advertised A=23; record HL=23 as source observation, not invented preservation; no underlying filesystem operation expected. | [No explicit preservation list; observe clobbers without inventing a promise.](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L1998) |
| A6 `ffs_flseek_p` | F | Pointer-based 32-bit direct FIL seek: zero/middle/end/>24-bit; exact position, read-only limit and writable expansion; no content expectation for expansion. | [`HL(U)`, `BC(U)`](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#L2008) |

## C-function route coverage

All slots are planned. Use documented Zilog prototypes and caller stack cleanup,
not RST preservation lists. Compile AgonDev C++ call sites and compare with a
hand-assembly caller against independent expected outcomes. Sharing the callee
is deliberate; agreement alone does not prove the callee. Fixed and variadic
arguments, byte/int/pointer returns and three-byte stack slots need distinct
capture checks. Reserved NULL slots are lookup-only, never indirect-call targets.

| B | Target / cases inherited plus route-specific checks | Profile |
| --- | --- | --- |
| 00 `_SD_init` | raw init without unlock wrapper; compare device result, not unlock rejection | R |
| 01 `_SD_readBlocks` | raw read without unlock: 1/2 sectors, exact bytes; 32-bit sector stack argument and 16-bit block count | R |
| 02 `_SD_writeBlocks` | raw write without unlock: intended sectors only; wide arguments and byte return | R |
| 03 `0` | reserved: successful lookup with NULL; do not call | M |
| 04 `0` | reserved: successful lookup with NULL; do not call | M |
| 05 `_f_printf` | f_printf: literals, supported integer/string formats, empty output, read-only failure; variadic ABI and exact bytes/count; unsupported float/long-long formats excluded | F |
| 06 `_f_findfirst` | inherit 94 directory search; four pointer arguments and full-width FRESULT | F |
| 07 `_f_findnext` | inherit 95 iteration; full-width FRESULT | F |
| 08 `_open_UART1` | inherit 15 UART config; structure pointer stack argument and byte return | U |
| 09 `_setVarVal` | inherit 30; optional actualName pointer, mutable type pointer, numeric-value-as-argument distinction | S |
| 0A `_readVarVal` | inherit 31; in/out length and type pointers, short buffers and NULL value | S |
| 0B `_gsTrans` | inherit 34; required read-count pointer, optional destination and flags; exact lengths | S |
| 0C `_substituteArgs` | inherit 35; five stack arguments, optional destination, full calculated-length return | S |
| 0D `_resolvePath` | inherit 38; optional index/DIR pointers and in/out length; iteration lifecycle | F |
| 0E `_getDirectoryForPath` | inherit 39; length pointer and explicit prefix index; pure string result | S |
| 0F `_resolveRelativePath` | inherit 3C; pointer-based length argument, required destination in pinned version | F |
| 10 `func_getsysvars` | same sysvars base as 08; no-argument pointer return, stable fields only | M |
| 11 `func_getkbmap` | same bitmap base as 1E; no-argument pointer return and controlled key updates | K |

## Dispatcher and RST families

| Entry | Planned cases / expected evidence | Capability and isolation |
| --- | --- | --- |
| RST08 unnamed selectors | Sweep all 156 unnamed A values; advertised A=23, source HL=23 separately observed; named stub cases already listed | E+H; seed valid state, no invented preserved set |
| RST08 call mode | Correct RST.LIS route, ADL MB=0; separate supported classic MB promotion checks | E+H; classic harness pending; baseline smoke is not proof for all call encodings |
| RST10 | 00/printable/7F/80/FF output bytes at transport boundary; target capture independent of report printing | E+H; display interpretation is separately conditional |
| RST18 | Length 1/2/255/256/65535; delimiter first/middle/end; exact bytes and HL/E/BC effects; A length-return discrepancy retained | E+H; valid bounded strings and sufficient buffers; 16-bit count, no implicit 24-bit size |
| RST00 | Start record then reset; observe fresh boot/termination of prior case, SRAM wiping allowed | Isolated E+H; SD checkpoint before reset; never require ordinary return |
| RST38 | Deliberately invoke report with known CPU/stack state; compare captured report/state then recover | Isolated E+H; backend-specific recovery required |
| RST20/28/30 | Excluded: not advertised public services | Inventory records bare RET source behavior only |

## Deferred or conditional branches, without hidden omissions

Peripheral electrical timing, arbitration loss, physical media faults and power-
loss durability need hardware/fixtures or verified fault injection; unavailable
branches are explicitly unsupported or blocked. Large files above 16 MiB need
suitable disposable images and space. Memory exhaustion, interrupt races and
classic-mode robustness need isolated runners. Menu convenience work is later;
editable per-function startup scripts remain the first human selection route.

W03 must resolve each ambiguous input/result before implementing that concrete
case; retain the uncertainty in the report contract until resolved. It must also
specify known-preserving/known-clobbering harness checks, decoder corruption tests,
checkpoint isolation, and recovery from hangs without relying on MOS itself.
These are future TEST-* validation requirements, not executed tests of the suite.

## Validation of this planning artifact

W02 checks uniqueness and completeness against W01, source/document revision
continuity, every named entry's scenario/fixture/backend/preservation fields,
all 18 C slots and the reserved/out-of-range accounting. This verifies the
planning inventory, not the behavior of any MOS function. See
[W02 evidence](tasks/MAIN-01/W02/README.md). No firmware edits or runtime tests.
