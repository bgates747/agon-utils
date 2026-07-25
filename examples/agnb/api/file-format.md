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
