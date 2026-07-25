# AGNB loader API

`agnb_api.inc` is the only include file published by the API. It contains the
application-neutral loader implementations proven by the image and audio test
harnesses.

## Public entry points

```asm
    ld de,image_filename
    call agnb_load_images

    ld de,image_filename
    ld hl,image_complete_callback
    call agnb_load_images_with_callback

    ld de,audio_filename
    call agnb_load_audio
```

Both routines accept a zero-terminated filename in `DE`. They return `A=0`
with Z set after every record has been loaded and finalized, or an
`agnb_error_*` value with NZ set. The same result remains in
`agnb_last_error`.

The image loader accepts AGNB 0.1 `BHDR/IMAG/DATA` records and creates VDP
bitmaps. The audio loader accepts provisional AGNB 0.2 `BHDR/AUDI/DATA`
records and creates VDP samples. Neither routine plots, plays, waits for input,
prints diagnostics, or owns application filenames.

`agnb_load_images_with_callback` has the same result contract as
`agnb_load_images` and invokes the routine in `HL` once after each bitmap is
finalized. The callback may update application progress UI or emit a loading
breadcrumb; its return value is ignored. The original `agnb_load_images`
entry point selects an internal no-op callback and remains source-compatible
with existing consumers.

## External dependencies

`agnb_api.inc` deliberately does not embed common MOS, math, or VDP libraries;
doing so would collide with equivalent labels in real applications. The
consumer must provide:

- `FFSCALL`, `ffs_fopen`, `ffs_fclose`, `ffs_fread`, and `fa_read`;
- `ffobjid_objsize`, `fil_obj`, and `fil_dir_ptr`;
- `umul24`;
- `vdu_load_buffer`, `vdu_clear_buffer`, and `vdu_consolidate_buffer`;
- `vdu_buff_select` and `vdu_bmp_create` for images; and
- `vdu_buffer_to_sound` for audio.

`agnb_dependencies.inc` contains the exact known-good definitions used by the
test harnesses. It is a reference and convenience source, not a second public
API include. Do not include it wholesale if the application already defines
any of those symbols; copy or retain only missing dependencies.

## Memory and lifetime

The implementation owns one FatFS `FIL`, parser state, normalized metadata,
and an API-owned 8 KiB transfer window in the assembled image. The API does
not reserve a fixed SRAM address because consuming applications may already
use that memory for persistent state. Calls are synchronous and non-reentrant.
Every `agnb_open` resets logical reader state, so consecutive container loads
are supported.

The writer supplies all buffer IDs. The loader rejects `0xFFFF` and never
allocates, increments, derives, or remaps IDs.
