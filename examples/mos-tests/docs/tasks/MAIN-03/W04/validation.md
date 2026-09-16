# MAIN-03 W04 — recording/checkpoint qualification

PASSED: the encoder matched all six frozen record types and the control slot;
22 injected failures stopped safely; 1,064 interrupted SRAM stores retained
bounded valid evidence. Two captured target cases produced eight records on a
raw SD image, and reboot refused to overwrite that file. Hardware is untested.

## Reproduction and artifacts

Run on Linux from /home/smith/Agon/mystuff/agon-utils/examples/mos-tests:

```sh
./human/mos-tests recording-check --output .emulator/runs/recording-review
./human/mos-tests runner-build
```

Use a fresh directory. Final evidence is from recording-04. The 65 MiB raw image
and native test executable remain in ignored .emulator/runs/recording-04; relevant
results, firmware/compiler/source identities, target binary/map, disassembly,
transcript, SRAM and independent SD readbacks are retained here. evidence-sha256.json
covers these copied artifacts. The post-collision file matches the original bytes.
Both emulator processes exited normally. AgonDev runner build also passed.

## Independent checks

1. Frozen typed bytes, maximum payload, exact staging capacity, disposition/UTF-8
   rules, nonzero identity and terminal-state guards passed with ASan/UBSan.
2. Short/error writes and sync faults at every start/observation/end boundary of
   two cases stopped execution without advancing confirmed progress or retrying.
   Close/capacity/sequence/generation failure controls also passed.
3. 873 byte-store interruptions cover staging and dual-control publication;
   191 cover emergency publication. Independent CRC checks validate surviving
   committed evidence. No arbitrary crash or power-failure guarantee follows.
4. Qualification parser rejected 684 truncated prefixes and 690 single-bit
   mutations across all six record fixtures. W05 production decoder and full
   TEST-01 W03 identity/order/recovery checks remain pending.
5. Eight raw-card records have expected types, serial sequences, run ID, case
   results and captured register pairs. SRAM confirmed sequence is eight, ended
   state is present, and untouched capture/stack/guard regions retain C7.
6. Same-image reboot returns FR_EXIST, publishes an allocation emergency record,
   stops, and preserves the existing card result byte for byte.

## Trials and scope

recording-01 passed with the initial adapter. recording-02 passed with direct
write-status capture, emergency interruption checks and collision refusal.
recording-03 completed native checks/build but stopped before emulator launch
because provenance code used a nonexistent clang++ path. Corrected to the actual
AgonDev ez80-none-elf-clang compiler; recording-04 passed the final implementation.
All trial directories remain on Linux. No firmware patch, hardware execution,
commit or upstream publication. Synthetic manifest hashes are illustrative;
this is recording qualification, not an authenticated general-suite run.

See ../../../../docs/binary-recording.md for maintained contracts and limits.
