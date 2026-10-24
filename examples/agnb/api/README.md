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

    ld de,audio_filename
    ld hl,audio_complete_callback
    call agnb_load_audio_with_callback
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

`agnb_load_audio_with_callback` likewise invokes the routine in `HL` once
after each VDP sample is finalized. `agnb_load_audio` selects an internal
no-op callback, preserving its original calling convention. Applications can
use the callback boundary for loading animation or progress reporting without
placing application behavior in the container API.

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

## Plain buffers — provisional 0.3

```asm
    ld de,buffer_filename
    call agnb_load_buffers

    ld de,buffer_filename
    ld hl,record_complete_callback
    call agnb_load_buffers_with_callback
```

These additive entries accept only0.3 `BHDR/RAWD/DATA` records. `RAWD` byte0
means opaque bytes consolidated into one VDP block. Each DATA contains
1..0xFFFFFF bytes; the complete container can exceed eZ80 application RAM.
The same existing8KiB transfer window, FIL and parser state are reused. No
image/sample conversion or command execution occurs. Block layout is explicit:
file transfer fragments are consolidated, not exposed as logical blocks.

Return is A=0/Z after the full file closes, or the existing error code/NZ.
The callback runs only after successful DATA transfer, consolidation and record
padding/end validation. The current ID and length remain in `agnb_metadata`
at `agnb_meta_bufferId` and `agnb_meta_data_size`; the latter is u32 with its
high byte checked zero. Callback results are ignored. The callback may destroy AF, BC, DE, HL and IX; it must preserve IY, SP
and the API's parser/stream state. Never recursively invoke another AGNB load
from a callback: state and the transfer window are shared/non-reentrant.

As with existing loaders, earlier records remain installed after a later error;
the current target may have been cleared or partly uploaded. This is not a
transactional installer and performs no rollback/readback/checksum. Do not call
loaded programs until the entire load succeeds. Caller owns cleanup/activation
and dynamic native-module loading. Explicit repeated IDs replace earlier data
in order; the host writer rejects duplicates to catch accidental assignments,
but the small runtime loader does not maintain a global ID set.

The independent stock-MOS qualification is recorded under
[AGNB-001](../docs/tasks/AGNB-001.md). The Author accepted the Oryx review on2026-10-23; saved results and runtime
identities match. The additive0.3 runtime is released for scoped publication
under the earlier explicit ownership/commit instruction. Physical hardware
qualification is not claimed.
