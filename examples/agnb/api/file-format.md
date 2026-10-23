# Implemented AGNB layouts

All integers are unsigned little-endian. RIFF chunks contain a FourCC, a u32
payload size, the payload, and zero padding to a four-byte boundary. Sizes
exclude chunk headers and padding.

## Common envelope

```text
RIFF u32(file size - 8) AGNB
  VERS
  LIST BUFR
    BHDR
    descriptor
    DATA
```

`BHDR` contains one explicit u16 `bufferId`. `0xFFFF` is invalid. Metadata and
all enclosing bounds must validate before any `DATA` byte is read or uploaded.

## Image records — version 0.1

```text
VERS: u8 0, u8 1
BHDR: u16 bufferId
IMAG: u16 width, u16 height, u8 format
DATA: width * height bytes for implemented format 1 (RGBA2222)
```

The loader streams and consolidates `DATA`, selects the same buffer ID, and
creates the bitmap using the retained `IMAG` metadata.

## Audio records — provisional version 0.2

```text
VERS: u8 0, u8 2
BHDR: u16 bufferId
AUDI: u8 format=0x09, u16 sampleRate
DATA: nonempty unsigned 8-bit mono PCM bytes
```

Format `0x09` records VDP base format 1 (unsigned 8-bit mono) plus modifier bit
3 indicating that the sample rate is explicit. The loader streams and
consolidates `DATA`, masks the modifier before calling the established
`vdu_buffer_to_sound` helper, and creates the sample at the retained rate.

## Plain buffer records — provisional version 0.3

```text
VERS: u8 0, u8 3
BHDR: u16 bufferId
RAWD: u8 layout=0
DATA: 1..0xFFFFFF opaque bytes
```

Each record is `LIST BUFR` containing exactly `BHDR`, `RAWD`, `DATA`, in that
order. Layout0 means consolidate transfer fragments into one VDP block. It is
not an image/audio descriptor and never requests payload execution, bitmap or
sample creation. Unsupported descriptor values reject. Every padding byte is
zero. Versions0.1 and0.2 and their writer output remain unchanged.

IDs0..65534 are explicit;65535 rejects. The host writer rejects duplicate IDs;
the wire layout itself permits ordered replacement of a repeated ID, as the
bounded runtime loader does not keep a global ID table. DATA and aggregate
container sizes differ: each DATA fits the current24-bit transfer count; a
container may be larger than eZ80 application RAM. Available VDP memory remains
an independent limit. The8KiB read window does not define logical block layout.

The dependency-free host API is `api/buffers.py`; generic framing shared by
image/audio/plain writers is `api/riff.py`. `build_container(records)` accepts
explicit `BufferRecord(buffer_id,data)` values. `read_container(bytes)` validates
exact framing and contents; it is a host reader, not the bounded eZ80 loader.
`write_manifest(manifest_path,output_path)` resolves build-time paths relative
to its manifest. Filenames are not stored in the container:

```json
{"records":[{"buffer_id":42,"path":"payload.bin"}]}
```

```bash
.venv/bin/python examples/agnb/api/buffers.py manifest.json buffers.agnb
.venv/bin/python examples/agnb/api/tests/test_buffers.py
```

Host validation finishes before output-file mutation. File write failures are
not transactional. Plain-buffer runtime qualification is tracked by AGNB-001;
format/host-tool tests do not establish actual target acceptance.
