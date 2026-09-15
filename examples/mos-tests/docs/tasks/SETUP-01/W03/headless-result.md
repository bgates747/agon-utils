# Headless W03 result

The unmodified smoke binary executed with SDL dummy video/audio and software
rendering. Debugger capture verified the exact 42-byte MOS output sequence,
including CR/LF, and HL=0 at crt0's entry after main returned. No desktop unlock
was needed. Both the earlier graphical instance and the headless instance
were closed.

## Method and evidence

1. Launched the canonical profile wrapper from `.emulator` with
   `SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy` and arguments
   `--renderer sw -d -b 0`, using a PTY for the debugger.
2. Installed triggers at 0x401e1 (main), 0x10 (MOS character output entry),
   and 0x400c8 (crt0 immediately after main), derived from this binary's map.
   Removed the reset breakpoint and continued. Commands and CPU states are
   preserved in `headless-debugger.txt`.
3. Decoded register A from each PC=0x10 state; exact comparison against the
   expected text plus CR/LF passed. Bytes are in `captured-mos-output.txt`.
4. Captured HL=000000 at PC=0400c8. Execution subsequently continued into MOS;
   no framebuffer rendering or visible prompt claim is made from this trace.
5. Sent Ctrl-C and debugger `exit`; waited for emulator termination. The first
   batched debugger-command attempt did not execute the test; the successful
   run sent each command separately so readline could process it.
6. This run used hostfs and validates only the C++/libagon/MOS output path and
   main return at the observed boundary. Raw SD image qualification remains W06.
   Physical hardware and human visual validation were not performed, and no
   commit approval is inferred from this automated result.
