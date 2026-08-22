# Opcode-traceable agondev translation

The preserved ASMX/Intel source is the readable authority and the independent
8 KiB ASMX ROM is the byte authority. The agondev port translates bounded
routines to GNU Z80 syntax at their original logical addresses and compares
every emitted byte before accepting a slice.

## First accepted slice

`make translation-proof ASMX=/path/to/asmx` assembles these routines with
agondev in ADL=0 mode:

| Routine | Address | Bytes |
| --- | ---: | ---: |
| `InitRack` | `00b1` | 38 |
| `InitAliens` | `01c0` | 13 |
| `AddDelta` | `01d9` | 11 |
| `Cnt16s` | `1554` | 14 |
| `GetAlienStatPtr` | `1581` | 15 |
| `BlockCopy` | `1a32` | 9 |
| `ConvToScr` | `1a47` | 21 |

All 121 bytes match the corresponding ASMX reference ranges. This slice
covers calls, conditional calls/returns/jumps, stack operations, direct and
indirect memory, 8-bit arithmetic, 16-bit pointers, rotates, and loops.

## Syntax mapping

The translation uses explicit instructions so agondev cannot silently choose
a shorter or different control-flow encoding. Representative mappings are:

| Intel 8080 | GNU Z80/eZ80 |
| --- | --- |
| `MOV A,M` | `ld a,(hl)` |
| `MVI M,n` | `ld (hl),n` |
| `LXI H,nn` | `ld hl,nn` |
| `LDA nn` / `STA nn` | `ld a,(nn)` / `ld (nn),a` |
| `LHLD nn` / `SHLD nn` | `ld hl,(nn)` / `ld (nn),hl` |
| `INX H` / `DCX H` | `inc hl` / `dec hl` |
| `DAD D` | `add hl,de` |
| `RLC` / `RRC` / `RAR` | `rlca` / `rrca` / `rra` |
| `JNZ nn` | `jp nz,nn` |
| `RNZ` / `RNC` | `ret nz` / `ret nc` |

`JP` remains explicit even where `JR` could reach; matching the original
three-byte opcode is part of traceability. Original `IN`/`OUT` sites remain
separately owned by the address-preserving adapter contract.

## Acceptance rule

A translated routine is accepted only when its complete address-bounded byte
range matches the reference. Intentional adapter or scheduler changes must be
applied after that comparison and documented as patches, rather than hidden
inside an otherwise claimed exact translation.
