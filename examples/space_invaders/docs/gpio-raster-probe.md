# GPIO Raster Probe

`src/probes/gpio_raster.asm` is the smallest target-side test for the accepted
direct GPIO display path. It is not game code.

Build it with:

```sh
make gpio-probe AGONDEV_PREFIX=/path/to/agondev/release
```

The output is `build/bin/gpio-raster.bin`. It is an ADL=0 MOS executable that:

1. copies Tom's bundled position-fixed static GPIO driver to `0x0b8000`;
2. calls the driver directly without changing a MOS reset vector;
3. clears a 320×240 RGB332 framebuffer at `0x080000`;
4. draws a centered 256×224 aperture with uniquely colored edges and a white
   center cross;
5. selects driver mode 8; and
6. stops video and returns to MOS after a key-down event.

The edge key is red at raw top, blue at raw bottom, green at raw left, and
magenta at raw right. This makes rotation, mirroring, centering, and clipping
unambiguous.

The static library is the upstream project's documented stock-MOS integration
path. Its provenance and SHA-256 are recorded under
`third_party/ez80-framebuffer-agon/`; the build rejects an unexpected library
identity. The probe does not flash or replace MOS or VDP firmware.

## Emulator result

The Author first verified two launches under Fab Agon Emulator with upstream
Rainbow MOS and the resident driver on 2026-08-22. A dedicated fail-closed
profile then exposed that the resident driver requires Rainbow's nonstandard
`mos_api_setresetvector` extension.

The probe was changed to bundle and directly call the static driver. The
Author verified the corrected profile using official MOS v3.0.2 Arthur and
stock VDP v2.16.0 Bistromathics. It displayed the expected centered pattern
without the Rainbow compatibility error. The emulator gate therefore passes
stock-MOS integration, repeatable mode entry, framebuffer addressing, RGB332
edge colors, clipping, and centering. Physical 15 kHz monitor compatibility
and application-cycle measurements remain hardware work.
