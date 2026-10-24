# C++ plain-buffer reader

C++ applications can stream an AGNB0.3 container through a caller-owned8KiB
window. Explicit buffer IDs and opaque bytes come from the file; the reader
neither executes them nor creates typed assets. The assembly reader and all
existing writer formats remain unchanged.

## AgonDev use

Add this `api/` directory to the compiler's include path. Supply one workspace
with static or otherwise adequate lifetime; placing8KiB on a small stack is
usually unnecessary.

```cpp
#include <agnb_agondev.hpp>

static agnb::Workspace workspace;

int install_assets() {
    const agnb::Error result=agnb::load_buffers_mos("assets.agnb",workspace);
    return static_cast<int>(result);
}
```

`load_buffers_mos` opens in binary mode, checks the physical file length, streams
and consolidates each record, and closes on success or failure. It submits through
`mos_puts` with an explicit binary length. Success means parser/file processing
and byte submission succeeded; stock VDP supplies no allocation acknowledgement.
The application owns serialization, completion barriers, activation and cleanup.
This reader accepts only plain-buffer0.3; images0.1/audio0.2 still use their
existing assembly APIs and writers.

## Portable layers and callbacks

1. `agnb_buffers.hpp` is the freestanding parser: `agnb::Input` supplies context,
   an exact-read function and physical length as uint32; `agnb::Transport` supplies
   context and an ordered send function. `agnb::load_buffers(input,transport,
   workspace,completed,context)` performs the load. It needs no heap, exceptions,
   SDK headers or runtime ID table.
2. A read function fills exactly its uint16 count and returns `Error::Ok`, or
   returns `Read`/`Eof`. Every read is bounded to the enclosing chunk/file; DATA
   reads are at most8,192bytes. Zero-length reads need not reach the input.
3. A send function consumes/copies every requested byte before returning true.
   It must not retain the supplied pointer. False returns `Transport`; the caller
   must recover a possibly incomplete transport frame before sending other
   commands. There is no automatic rollback or repair.
4. `agnb_stdio.hpp` supplies `load_buffers_file(filename,transport,workspace,
   completed,context)`. It owns fopen/fclose and uses fseek/ftell for exact physical
   size. Its maximum file position is the platform's signed `long` limit, also
   bounded by uint32; on AgonDev this is LONG_MAX=2,147,483,647. A seek/position
   failure rejects rather than narrowing to the target's24-bit `int`. Payload
   memory is the workspace; libc additionally owns FILE state/buffering.
5. Optional `Completed` is `void (*)(void *,const agnb::Record &)`. The record
   contains `buffer_id:uint16` and `data_bytes:uint32`. It fires after transfer,
   consolidation, padding and record-boundary validation. Copy the value if
   retaining metadata; its reference expires after the callback. Do not reenter
   with the same workspace or mutate the input/transport during a callback.
   Completion of one record does not establish successful file close or validity
   of later records.

Example callback with independently initialized state:

```cpp
#include <agnb_agondev.hpp>

struct Progress { uint32_t records; uint32_t payload_bytes; };
static agnb::Workspace workspace;
static Progress progress{0,0};

static void completed(void *context,const agnb::Record &record) {
    Progress &p=*static_cast<Progress *>(context);
    ++p.records;
    p.payload_bytes+=record.data_bytes;
}

int install_with_progress() {
    progress=Progress{0,0};
    return static_cast<int>(agnb::load_buffers_mos(
        "assets.agnb",workspace,completed,&progress));
}
```

## Validation and failure behavior

The parser enforces RIFF/AGNB physical length, exact version, chunk order and
boundaries, metadata shape, zero padding, IDs0..65534 and nonempty DATA up to
0xFFFFFFbytes. It validates record metadata/enclosing bounds before clearing or
uploading that record. Each record becomes one consolidated logical block;
transfer fragments are not application block boundaries. Repeated explicit IDs
replace earlier records in sequence, matching the assembly reader. The writer
still rejects duplicates to catch accidental assignments.

Earlier records survive a later error. The current record may have been cleared,
partially uploaded or consolidated before failure. No readback, checksum or
rollback is performed. Always inspect the final return value before using a
complete application package. A read failure cannot strand a just-announced DATA
window: each window is read successfully before its write header is emitted.
A transport failure can still leave an incomplete frame as described above.

`agnb::Error` values0..13 match the established assembly categories where
applicable: Ok0, Open1, Read2, Seek3, RiffId4, Form5, Version6, Chunk7, Bounds8,
BufferId9, Metadata10, DataSize11, Transport12, Eof13. The C++ stdio adapter adds
Close14. The first parser/read/transport error takes precedence over close errors.
Some malformed files can satisfy several rejection conditions; exact first-error
selection need not match a different reader's implementation order.

## Qualification

AGNB-002 retains sanitizer host checks against writer-generated containers,
byte-exact decoded transfer output, large/multi-window and65535/65536 boundaries,
callbacks, repeated IDs, late errors, malformed framing and injected read/send
failures. Actual AgonDev consumers qualify loading above application RAM, missing,
malformed and truncated files, late partial installation and recovery. Consumer
profile/human acceptance and publication are recorded separately in the task.
No physical hardware or loading-performance acceptance is inferred.
