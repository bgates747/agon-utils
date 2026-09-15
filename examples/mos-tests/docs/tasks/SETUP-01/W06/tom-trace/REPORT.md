# MOS 3.0.2 / Fab 1.2.4: missing boot file leads to invalid FIL close

## Summary

With an SD image containing `autoexec.txt` but no `!boot.obey`, stock MOS 3.0.2
Arthur faults before the test program starts. The observed stack is
`main → mos_cmdOBEY → f_close → f_sync → validate`; the stack-local FIL was
not opened and contains a stale filesystem pointer, 0xA26300. This reproduces
on Linux and macOS with Fab 1.2.4. Adding a populated `!boot.obey` to a copy of
the same image allows the C++ test to complete its headless assertions.

The evidence strongly points to the unconditional `f_close(&fil)` in MOS's
missing-file/error path. This is a source-correlated diagnosis, not a claim
that a MOS fix has been built or hardware-qualified. Hostfs previously masked
the symptom. No emulator/MOS code was changed for these experiments.

## 1. Reproduction inputs

1. Fab 1.2.4 on Linux and macOS x86_64; stock MOS v3.0.2 Arthur with matching map.
2. MOS binary SHA256:
   `d564243283972690933a4554296ad6202ca4ef54572279533a942960846bebae`.
   MOS map SHA256:
   `d69e60bbce61a7b4b3eef318ba395f11c4e1a5b585755755113992dc94edcb86`.
3. Failing image SHA256:
   `8dbbd0c4644f73eb17b39b805f989219d5d378cf18f4ed564d27672ae27ddb46`.
   It is a 65 MiB MBR disk, FAT32 partition at LBA 2048, 131072 sectors.
   Files are `/autoexec.txt` and `/mystuff/test.bin`; no optional OBEY boot files.
4. Autoexec bytes are CRLF lines:

```text
SET KEYBOARD 1
cd /mystuff
load test.bin
run
```

5. The image and deployed bytes were verified through mtools readback before
   and after MBR assembly. An earlier unpartitioned FAT32 trial passed fsck.fat.
   Unpartitioned FAT32, zeroed RAM, and precise interrupts reproduced the same
   invalid access. Neither partition choice nor RAM initialization removed it.
6. Our launch delegates to a profile wrapper which verifies MOS hashes, selects
   platform firmware and the explicit image. Equivalent Fab arguments for a
   maintainer reproduction, with the matching local platform VDP available:

```bash
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy ./fab-agon-emulator \
  --renderer sw --firmware platform --mos /path/to/mos_platform.bin \
  --sdcard-img /path/to/failing.img -d -b 0
```

The test binary is irrelevant to the failing path: `_main` at 0x0401E1 is never
reached. Its hash is `1fea5d9c1ffdcf5b533841e8f80f52974d655d0bec5c2b4c57d476894d8cdbd0`.

## 2. Observed call chain

Addresses are from the verified MOS map and live disassembly. `validate` is
static and absent from the public symbol list; its identification at 0x00E556
comes from disassembly plus the matching FatFS source, not a symbol-map entry.

| Frame | Entry | Calling instruction | Return address | IX at fault unwind |
| --- | --- | --- | --- | --- |
| MOS `main` | 0x001CC5 | 0x001D94 CALL 0x00387B | 0x001D98 | 0x0BFFF7 |
| `mos_cmdOBEY` | 0x00387B | 0x003BE5 CALL 0x00F4FD | 0x003BE9 | 0x0BFFDF |
| `f_close` | 0x00F4FD | 0x00F509 CALL 0x00F3EC | 0x00F50D | 0x0BFF93 |
| `f_sync` | 0x00F3EC | 0x00F3FD CALL 0x00E556 | 0x00F401 | 0x0BFF84 |
| `validate` | 0x00E556 | faulting load at 0x00E589 | paused PC 0x00E58C | 0x0BFF68 |

This is a manual unwind from the captured IX frame links and verified CALL
instructions, not an automatic debugger backtrace. Each saved IX is at IX+0;
each return address is at IX+3, three-byte little endian.

## 3. Stack evidence at the fault

| Address | Bytes | Interpretation |
| --- | --- | --- |
| 0x0BFF65 | `00 63 A2` | validate local fs pointer = 0xA26300 |
| 0x0BFF68 | `84 FF 0B` | saved IX = f_sync frame 0x0BFF84 |
| 0x0BFF6B | `01 F4 00` | return to 0x00F401 |
| 0x0BFF6E | `9C FF 0B` | validate obj argument = 0x0BFF9C |
| 0x0BFF71 | `7B FF 0B` | rfs output pointer = 0x0BFF7B |
| 0x0BFF84 | `93 FF 0B` | saved IX = f_close frame 0x0BFF93 |
| 0x0BFF87 | `0D F5 00` | return to 0x00F50D |
| 0x0BFF8A | `9C FF 0B` | f_sync fp argument |
| 0x0BFF93 | `DF FF 0B` | saved IX = OBEY frame 0x0BFFDF |
| 0x0BFF96 | `E9 3B 00` | return to 0x003BE9 |
| 0x0BFF99 | `9C FF 0B` | f_close fp argument |
| 0x0BFF9C | `00 63 A2` | first three bytes of stack-local FIL: invalid obj.fs |
| 0x0BFFDC | `04 00 00` | OBEY local fr = 4 (FR_NO_FILE) |
| 0x0BFFDF | `F7 FF 0B` | saved IX = MOS main frame |
| 0x0BFFE2 | `98 1D 00` | return to MOS main at 0x001D98 |

The file object begins at OBEY IX-0x43 = 0x0BFF9C. The pointer is already bad
before `f_close`, as shown by the breakpoint at 0x003BE5. No `F_OPEN` event
appeared despite an installed entry trigger at 0x00E674.

## 4. Faulting instruction and registers

```text
00E571  DD 31 06   LD IY,(IX+6)    ; obj = 0x0BFF9C
00E574  FD 07 00   LD BC,(IY+0)    ; obj->fs = 0xA26300
00E577  DD 0F FD   LD (IX-3),BC
...
00E586  DD 31 FD   LD IY,(IX-3)    ; IY = 0xA26300
00E589  FD 7E 00   LD A,(IY+0)     ; invalid read of fs_type
00E58C  B7         OR A,A          ; PC when debugger reports the fault
```

```text
PC=00E58C AF=F5A2 BC=000000 DE=0BFF5F HL=A26300
SPL=0BFF5F SPS=0000 IX=0BFF68 IY=A26300
MB=00 ADL=1 MADL=1 IFF1=1
```

Fab reports `CPU paused (memory 0xa26300 out of bounds)`. The core returns
0xF5 for invalid reads, explaining A=F5; 0x00E58C is the next instruction,
not the address of the offending load.

A prior visit to the same validation load had IY=0x0BC537 and read fs_type=3
successfully. The instruction itself is not invariably failing; this later
call receives a different object/pointer.

## 5. Source correlation

Inspected the clean local MOS checkout at tag v3.0.2:

1. `main.c:228–234`: tries `mos_cmdOBEY("!boot.obey")`, then
   `autoexec.obey` on FR_NO_FILE, then `mos_EXEC("autoexec.txt")` on FR_NO_FILE.
   At OBEY entry the stack argument is 0x0180F5; the ROM bytes there are
   `!boot.obey` followed by the other startup filenames.
2. `src/mos.c`, `mos_cmdOBEY` (starts at line 1035 in this checkout): declares
   uninitialized `FIL fil`; calls getResolvedPath; only calls f_open when
   resolution succeeds. Cleanup at line 1117 calls `f_close(&fil)` unconditionally.
3. `src_fatfs/ff.c:4152` (`f_close`) calls f_sync, which calls validate at line
   4083. `validate` begins at line 3561 and evaluates
   `obj && obj->fs && obj->fs->fs_type && obj->id == obj->fs->id`.
4. Observations agree with missing-file path resolution returning 4, skipping
   f_open, and closing an uninitialized stack FIL. The source-level cleanup is
   the leading suspect. A candidate fix would guard close by successful open;
   no patch or fix validation is included in this report.

Line numbers are navigation aids; function names, live bytes, map and hashes
are the stronger authorities. No claim is made that every aspect of Fab's
hostfs behavior is correct or that this is the only raw-image problem.

## 6. Controlled comparison

Copied the failing disk and added OBEY boot files. An empty !boot.obey bypassed
the missing-file cleanup but intentionally did not run the autoexec.txt test:
main treats successful OBEY as the selected startup script. That run timed out
waiting for the test checkpoint and is not counted as a test pass.

Then placed the actual startup commands in !boot.obey in that copy. With the
same Fab, MOS, test binary and FAT32 partition, raw-image execution passed:

1. Exact bytes `W04: MOS ABI 0123456789 AaZz !?` plus CR/LF reached MOS RST 10h.
2. Main returned HL=0x123456, with balanced stack and preserved IX.
3. The debugger stopped before propagating the deliberate nonzero return to MOS.
4. The headless process exited zero. Result and transcripts are in
   `boot-files-present/cpp/`.

This comparison strongly supports a missing-optional-file cleanup issue rather
than a general inability to boot raw SD images. Firmware was not modified.

## 7. Suggested debugger sequence

```text
trigger $387b "OBEY ENTRY" : state : mem sp 24
trigger $e674 "F_OPEN" : state : mem sp 24
break $3be5
delete $0
c
state
mem $bff99 72
dis24 $3be2 $3c04
delete $3be5
c
state
mem $bff5f 144
dis24 $e556 $e5e4
exit
```

Use the numeric addresses only with the specified MOS image/map. Inspect
`capture.py` for the fuller capture procedure; its paths are project-specific.
The ZIP/tar bundle is for sharing manually; nothing has been sent to Tom.
