"""Build the container-based AGNB test harness.

AGNB 0.1 on-disk format
=======================

All integers are unsigned little-endian. Every RIFF chunk has an 8-byte
header (FourCC plus u32 payload size); its payload is padded with zero bytes to
a four-byte boundary. Chunk sizes exclude the header and padding.

::

    RIFF  u32(file_size - 8)  AGNB
      VERS  size=2
        u8 major=0
        u8 minor=1
      LIST  type=BUFR
        BHDR  size=2
          u16 buffer_id
        IMAG  size=5
          u16 width
          u16 height
          u8  format=1          # RGBA2222
        DATA  size=width*height
          u8 pixels[size]       # row-major, no row padding

There is exactly one VERS chunk before one or more LIST BUFR records. Each
version 0.1 record contains exactly one BHDR, one IMAG, and one DATA chunk in
that order. The LIST payload consists of the four-byte BUFR type followed by
its nested chunks; the LIST size includes both.

The writer supplies every buffer ID. IDs must be unique within the container;
0xFFFF is reserved by the VDP and invalid. Record order does not determine an
ID, and readers never allocate, increment, derive, or remap IDs.

Version 0.1 supports only RGBA2222 (format 1), so DATA size must equal width
times height. Metadata and enclosing RIFF/LIST bounds must validate before any
DATA payload is read or uploaded. Unknown chunks are skipped using
8 + align4(payload_size), where align4(n) = (n + 3) & ~3.

The RIFF size includes AGNB, all chunk headers and payloads, nested LIST
contents, and all alignment padding. Writers emit zero-valued padding and must
reject duplicate IDs, invalid IDs, invalid dimensions, mismatched DATA sizes,
and any size that cannot be represented by the required u32 field.
"""

import argparse
import struct
from dataclasses import dataclass
from pathlib import Path

from PIL import Image


CONTAINER_DIR = Path(__file__).resolve().parents[1]
PROJECT_DIR = CONTAINER_DIR.parent
SHARED_PROCESSED_DIR = PROJECT_DIR / "shared" / "assets" / "processed"
TARGET_DIR = CONTAINER_DIR / "tgt"
CONTAINER_FILE = TARGET_DIR / "images.agnb"

VERSION_MAJOR = 0
VERSION_MINOR = 1
IMAGE_FORMAT_RGBA2222 = 1
FIRST_BUFFER_ID = 256
MAX_U16 = 0xFFFF
MAX_U32 = 0xFFFFFFFF
INVALID_BUFFER_ID = 0xFFFF


@dataclass(frozen=True)
class ImageRecord:
    """Validated inputs for one LIST BUFR image record."""

    name: str
    buffer_id: int
    width: int
    height: int
    rgba_file: Path
    data_size: int


def align4(size: int) -> int:
    return (size + 3) & ~3


def make_chunk(chunk_id: bytes, payload: bytes) -> bytes:
    """Return one aligned RIFF chunk, including its header and zero padding."""
    if len(chunk_id) != 4:
        raise ValueError(f"RIFF chunk ID must contain four bytes: {chunk_id!r}")
    if len(payload) > MAX_U32:
        raise ValueError(f"RIFF payload is too large: {len(payload)} bytes")

    padding = bytes(align4(len(payload)) - len(payload))
    return chunk_id + struct.pack("<I", len(payload)) + payload + padding


def scan_image_records() -> list[ImageRecord]:
    """Validate shared PNG/RGBA2222 pairs and assign explicit buffer IDs."""
    png_files = sorted(SHARED_PROCESSED_DIR.glob("*.png"))
    if not png_files:
        raise RuntimeError(
            f"No shared PNG files found in {SHARED_PROCESSED_DIR}; "
            "run shared/scripts/prepare_images.py first"
        )

    png_stems = {path.stem for path in png_files}
    rgba_files = sorted(SHARED_PROCESSED_DIR.glob("*.rgba2"))
    orphaned_rgba = [path for path in rgba_files if path.stem not in png_stems]
    if orphaned_rgba:
        names = ", ".join(path.name for path in orphaned_rgba[:5])
        raise ValueError(f"RGBA2222 files without matching PNGs: {names}")

    records = []
    used_buffer_ids = set()
    for index, png_file in enumerate(png_files):
        buffer_id = FIRST_BUFFER_ID + index
        if buffer_id >= INVALID_BUFFER_ID:
            raise ValueError(f"Invalid buffer ID for {png_file.name}: {buffer_id}")
        if buffer_id in used_buffer_ids:
            raise ValueError(f"Duplicate buffer ID: {buffer_id}")

        rgba_file = png_file.with_suffix(".rgba2")
        if not rgba_file.is_file():
            raise FileNotFoundError(f"Missing shared RGBA2222 file: {rgba_file}")

        with Image.open(png_file) as image:
            width, height = image.size
        if not 1 <= width <= MAX_U16 or not 1 <= height <= MAX_U16:
            raise ValueError(
                f"Invalid image dimensions for {png_file.name}: {width}x{height}"
            )

        data_size = rgba_file.stat().st_size
        expected_size = width * height
        if data_size != expected_size:
            raise ValueError(
                f"RGBA2222 size mismatch for {rgba_file}: "
                f"expected {expected_size}, found {data_size}"
            )
        if data_size > MAX_U32:
            raise ValueError(f"RGBA2222 payload is too large: {rgba_file}")

        records.append(
            ImageRecord(
                name=png_file.stem,
                buffer_id=buffer_id,
                width=width,
                height=height,
                rgba_file=rgba_file,
                data_size=data_size,
            )
        )
        used_buffer_ids.add(buffer_id)

    return records


def make_buffer_record(record: ImageRecord) -> bytes:
    """Return one aligned LIST BUFR record."""
    pixels = record.rgba_file.read_bytes()
    if len(pixels) != record.data_size:
        raise RuntimeError(
            f"RGBA2222 file changed while building: {record.rgba_file}"
        )

    nested_chunks = b"".join(
        (
            make_chunk(b"BHDR", struct.pack("<H", record.buffer_id)),
            make_chunk(
                b"IMAG",
                struct.pack(
                    "<HHB",
                    record.width,
                    record.height,
                    IMAGE_FORMAT_RGBA2222,
                ),
            ),
            make_chunk(b"DATA", pixels),
        )
    )
    return make_chunk(b"LIST", b"BUFR" + nested_chunks)


def build_container(records: list[ImageRecord]) -> bytes:
    """Compile validated image records into one complete RIFF AGNB file."""
    if not records:
        raise ValueError("An AGNB container requires at least one buffer record")

    body = bytearray(b"AGNB")
    body.extend(make_chunk(b"VERS", bytes((VERSION_MAJOR, VERSION_MINOR))))
    for record in records:
        body.extend(make_buffer_record(record))

    if len(body) > MAX_U32:
        raise ValueError(f"RIFF container is too large: {len(body) + 8} bytes")
    return b"RIFF" + struct.pack("<I", len(body)) + body


def write_container() -> None:
    records = scan_image_records()
    container = build_container(records)
    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    CONTAINER_FILE.write_bytes(container)
    print(
        f"Generated {CONTAINER_FILE} with {len(records)} image records "
        f"({len(container)} bytes)"
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build the container-based AGNB test harness."
    )
    parser.add_argument(
        "-b",
        "--build-container",
        action="store_true",
        help="Compile the shared image assets into images.agnb.",
    )
    parser.parse_args()

    # With only one implemented step, no options and -b intentionally agree.
    write_container()


if __name__ == "__main__":
    main()
