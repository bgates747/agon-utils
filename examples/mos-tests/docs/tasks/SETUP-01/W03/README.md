# W03 — C++ MOS smoke test

The clean C++ build and MOS-header checks passed. The binary was copied and
hash-verified in the dedicated profile, which is running for human review.
W03 remains unfinished pending observed output and return to the MOS prompt.

## Expected behavior

1. The program calls libagon `putch` for each character of exactly
   `MOS-TESTS W03: C++ -> MOS output reached`, followed by CR/LF.
2. `main` returns zero; with the optional exit handler disabled, MOS should
   resume at its prompt without an error. The marker means execution reached
   the output loop; it is not a claim of comprehensive MOS or compiler correctness.
3. The Author checks the full line, absence of corrupted characters, and return
   to the MOS prompt. A live emulator process alone does not establish these.

## Reproduce on Linux

From `/home/smith/Agon/mystuff/agon-utils/examples/mos-tests`:

```bash
make clean
make V=
cp bin/mos-tests.bin .emulator/sdcard/mystuff/mos-tests.bin
sha256sum bin/mos-tests.bin .emulator/sdcard/mystuff/mos-tests.bin
cd .emulator
./fab-agon-emulator
```

The prepared CRLF autoexec sets keyboard 1, changes to `/mystuff`, loads
`mos-tests.bin`, and runs it. At the MOS prompt, repeat with `load mos-tests.bin`
then `run`. Close the existing profile window before launching another instance
against the same SD state. The Linux graphical session used WAYLAND_DISPLAY
`wayland-1` and XDG_RUNTIME_DIR `/run/user/1000` for the SSH launch.

## Evidence and limits

1. `build.txt` records successful clean/build commands; `binary-identity.txt`
   records size, SHA256 and verified MOS header bytes at offset 0x40.
2. `mos-tests.bin` and `mos-tests.map` preserve the built candidate;
   `main-disassembly.txt` records the compiled main object and its putch call.
3. `launch.txt` records the hash-verified deployment and live process check.
   `.emulator/w03-launch.log` reports Wayland startup. No visual result has
   been observed by the agent; the Author's confirmation remains required.
4. `autoexec-before.txt` preserves the previous profile startup text.
5. Consulted official local `agon-docs/docs/mos/Executables.md` for the header
   and entry conventions, and `agon-docs/docs/mos/API.md` for character output.
6. No physical hardware was flashed or tested. All changes remain uncommitted
   pending the canonical emulator human-validation gate. The Author is present,
   so no repeated attention cue was played.

## Headless verification update

W03 is complete using headless debugger evidence: exact output bytes at MOS
RST 10h and HL=0 after main returned. See
`headless-result.md`.
The graphical and headless processes are closed. Earlier pending visual-review
notes describe the initial attempt; no visible-prompt or hardware claim is
made. Hostfs was used for this bootstrap check; W06 owns raw SD image migration.
All changes remain uncommitted.
