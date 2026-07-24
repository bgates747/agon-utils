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
          u16 bufferId
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
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

CONTAINER_DIR = Path(__file__).resolve().parents[1]
PROJECT_DIR = CONTAINER_DIR.parent
SHARED_PROCESSED_DIR = PROJECT_DIR / "shared" / "assets" / "processed"
SHARED_SCRIPTS_DIR = PROJECT_DIR / "shared" / "scripts"
sys.path.insert(0, str(SHARED_SCRIPTS_DIR))

from image_manifest import (  # noqa: E402
    MANIFEST_FILENAME,
    included_entries,
    load_manifest,
    validate_asset_files,
)

MANIFEST_FILE = SHARED_PROCESSED_DIR / MANIFEST_FILENAME
TARGET_DIR = CONTAINER_DIR / "tgt"
CONTAINER_FILE = TARGET_DIR / "images.agnb"
ASM_IMAGES_FILE = CONTAINER_DIR / "src" / "asm" / "images.inc"
ASM_DIR = CONTAINER_DIR / "src" / "asm"
ASM_APP_FILE = ASM_DIR / "app.asm"
APP_BINARY_FILE = TARGET_DIR / "app.bin"
APP_BINARY_ASM_PATH = Path("../../tgt/app.bin")

VERSION_MAJOR = 0
VERSION_MINOR = 1
IMAGE_FORMAT_RGBA2222 = 1
MAX_U32 = 0xFFFFFFFF


@dataclass(frozen=True)
class ImageRecord:
    """Validated inputs for one LIST BUFR image record."""

    source: str
    name: str
    bufferId: int
    width: int
    height: int
    rgbaFile: Path
    dataSize: int


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


def load_image_records() -> list[ImageRecord]:
    """Load the selected, ordered image catalog from the shared manifest."""
    entries = included_entries(load_manifest(MANIFEST_FILE))
    validate_asset_files(entries, SHARED_PROCESSED_DIR)
    return [
        ImageRecord(
            source=entry.source,
            name=entry.name,
            bufferId=entry.bufferId,
            width=entry.width,
            height=entry.height,
            rgbaFile=SHARED_PROCESSED_DIR / entry.rgba2,
            dataSize=entry.dataSize,
        )
        for entry in entries
    ]


def make_buffer_record(record: ImageRecord) -> bytes:
    """Return one aligned LIST BUFR record."""
    pixels = record.rgbaFile.read_bytes()
    if len(pixels) != record.dataSize:
        raise RuntimeError(
            f"RGBA2222 file changed while building: {record.rgbaFile}"
        )

    nested_chunks = b"".join(
        (
            make_chunk(b"BHDR", struct.pack("<H", record.bufferId)),
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
    records = load_image_records()
    container = build_container(records)
    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    CONTAINER_FILE.write_bytes(container)
    write_images_include(records)
    print(
        f"Generated {CONTAINER_FILE} with {len(records)} image records "
        f"({len(container)} bytes)"
    )


def write_images_include(records: list[ImageRecord]) -> None:
    lines = [
        "; Generated by container/scripts/do_assembly.py\n\n",
        "image_type: equ 0\n",
        "image_width: equ image_type+3\n",
        "image_height: equ image_width+3\n",
        "image_filesize: equ image_height+3\n",
        "image_ex_filename: equ image_filesize+3 ; former filename pointer\n",
        "image_record_size: equ image_ex_filename+3\n\n",
        f"num_images: equ {len(records)}\n\n",
        "; bufferIds:\n",
    ]
    for record in records:
        lines.append(f"buf_{record.name}: equ {record.bufferId}\n")

    lines.append("\nimage_bufferIds:\n")
    for record in records:
        lines.append(f"\tdw {record.bufferId}\n")

    lines.append(
        "\nimage_list: ; type; width; height; filesize; ex filename pointer:\n"
    )
    for record in records:
        lines.append(
            f"\tdl {IMAGE_FORMAT_RGBA2222}, {record.width}, "
            f"{record.height}, {record.dataSize}, 0xFFFFFF\n"
        )

    ASM_IMAGES_FILE.parent.mkdir(parents=True, exist_ok=True)
    ASM_IMAGES_FILE.write_text("".join(lines))
    print(f"Generated {ASM_IMAGES_FILE} from {len(records)} manifest entries")


def run_ez80asm() -> None:
    """Generate application metadata and assemble the container test app."""
    records = load_image_records()
    write_images_include(records)
    TARGET_DIR.mkdir(parents=True, exist_ok=True)

    try:
        result = subprocess.run(
            ["ez80asm", "-l", ASM_APP_FILE.name, str(APP_BINARY_ASM_PATH)],
            cwd=ASM_DIR,
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as error:
        if error.stdout:
            print(error.stdout, end="")
        if error.stderr:
            print(error.stderr, end="", file=sys.stderr)
        raise SystemExit(error.returncode) from error

    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, end="", file=sys.stderr)
    print(f"Generated {APP_BINARY_FILE}")


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
    parser.add_argument(
        "-a",
        "--assemble",
        action="store_true",
        help="Generate images.inc and assemble app.asm into app.bin.",
    )
    args = parser.parse_args()

    if not args.build_container and not args.assemble:
        write_container()
        run_ez80asm()
    else:
        if args.build_container:
            write_container()
        if args.assemble:
            run_ez80asm()


if __name__ == "__main__":
    main()
