# Plain-buffer loader review

A516032-byte container loads through the existing8192-byte transfer window in
a12091-byte MOS test application. Stock Fab/MOS tests pass on Pi and Oryx,
including explicit IDs, payload samples, repeated loading and malformed records.
The Author accepted the Oryx review on2026-10-23. Saved results match all66
expected bytes and runtime identities; scoped publication is authorized.

On Oryx:

```bash
cd ~/Agon/mystuff/agon-utils/examples/agnb/.emulator
./fab-agon-emulator
```

This is **Fab**, running the stock native VDP, not Flexe. The test runs from
MOS startup and returns to the prompt. Follow its single onscreen keyboard
instruction, close the window and tell the agent whether it worked. The agent
retrieves and verifies results.dat; no second terminal or verifier is needed.
The profile is dedicated to this task, generated through the canonical setup
helper, pinned to current MOS3.0.2 and left stopped. No GUI was launched by the
agent. Replay overwrites the result file; staging clears it for a fresh review.

## Automated evidence

1. `target-evidence.json`: Pi stock Fab/MOS,5.738s wall time.
2. `oryx-target-evidence.json`: Oryx stock Fab/MOS,5.594s wall time.
3. Both match66 expected result bytes: eight large-container completed records,
   a consecutive load, invalid-ID/descriptor errors, preserved earlier record
   on late failure, and truncated-file rejection. Each completed record checks
   explicit ID, DATA length and one stock-buffer byte sample. This is sampled
   payload observation, not an assertion of exhaustive byte equality.
4. Aggregate plain DATA is515648 bytes; individual payloads include8191/8192/
   8193,65535/65536 and160000/200000 bytes. Host tests separately validate full
   byte round trips. Timings include file I/O, UART, emulator and qualification
   queries; no physical throughput claim.
5. The callback/observer and queries belong only to `guest.asm`; production
   loading has no post-copy verification, progress UI or implicit program call.

Use `qualify.py --runtime PATH --assembler PATH` for a fresh local headless run.
It prepares only this subproject's owned profile; `--stage-only` leaves it
stopped without running. An already assembled build/probe.bin may be supplied
without --assembler on another host. Build artifacts stay under build/.
The project-local Python venv is required. No stock firmware changes or physical
hardware actions are included.


## Human acceptance

The Author launched the dedicated Oryx profile, followed the review and reported
"worked". The agent ran verify_review.py, retrieved the saved observations and
matched all66 expected bytes. human-review.json preserves the confirmation and
observation hash. Earlier pending-human statements in task history are now
superseded. No physical hardware qualification is implied.
