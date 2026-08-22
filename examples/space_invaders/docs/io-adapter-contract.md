# Original I/O adapter contract

The original ROM contains 42 executable two-byte port instructions: 19 `IN`
and 23 `OUT`. Several are preserved as raw `DB` opcode blocks, so source-level
mnemonic searches alone are not a complete inventory.

## Address-preserving trap ABI

The loader copies the byte-identical reference ROM to `0000-1fff`, then
changes each executable I/O pair in place:

```text
DB pp  (IN A,(pp))  -> C7 pp
D3 pp  (OUT (pp),A) -> C7 (pp | 80)
```

`C7` is `RST 0`. The original reset entry is no longer needed after the
loader enters `init`, so logical vector `0000` becomes a jump to the adapter
at `4000`. The stacked return address points to the descriptor byte. The
adapter advances it once before returning, preserving the original two-byte
instruction footprint and every later ROM address.

Descriptor bit 7 distinguishes output from input. Descriptor `7f` is reserved
for terminal proof control and is not an arcade port.

The trap preserves original `BC`, `DE`, `HL`, and flags. Output also preserves
`A`; input replaces only `A`, matching the original instruction contract.
Alternate AF and general register banks provide scratch state so no original
stack-frame layout or register convention changes.

## Port behavior

| Port | Direction | Adapter behavior |
| ---: | --- | --- |
| `1` | input | Player 1, coin, start, and cabinet input byte |
| `2` | input | Player 2 and DIP-switch byte |
| `2` | output | Store shift amount masked to `0-7` |
| `3` | input | Return shifted eight-bit window from retained 16-bit state |
| `3` | output | Store sound-bank-1 latch |
| `4` | output | Shift previous high byte down and load new high byte from `A` |
| `5` | output | Store sound-bank-2 latch |
| `6` | output | Count watchdog writes; no reset action in the emulator proof |

The shift read implements:

```text
(shift_register >> (8 - shift_amount)) & 0xff
```

This retains the adjacent byte loaded by the previous port-4 write; it is not
equivalent to an isolated rotate of the current sprite byte.

## Inert defaults

The adapter proof asserts no coin, start, fire, or movement inputs. Input port
2 is `08`, selecting the three-ship DIP setting while leaving the remaining
cabinet and display bits clear. Sound ports are latches only and watchdog
writes are counted.

## Interrupt boundary

The original five `EI` opcodes are changed to `DI` in the proof. Agon hardware
interrupts must never dispatch through the copied arcade vectors. The port's
scheduler will invoke the two original phases explicitly and keep GPIO Timer
1 ownership separate.

## Validation

`make adapter-proof ASMX=/path/to/asmx` checks all 42 original opcode/port
pairs against the independent reference ROM, confirms all five interrupt
sites, embeds the untouched 8 KiB image, and assembles the loader/adapter with
agondev. Runtime PASS additionally requires original initialization and status
rendering to exercise both shift-register directions, clear both sound
latches, produce non-empty packed VRAM, and reach the splash main loop.

The Author visually accepted a stable PASS in the pinned stock MOS/VDP Fab
profile on 2026-08-22. No game graphics appear on the stock VDP during this
proof: original drawing targets only the private packed framebuffer, while
the VDP displays the MOS diagnostic text and cursor.
