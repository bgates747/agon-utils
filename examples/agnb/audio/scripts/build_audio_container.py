#!/usr/bin/env python3
"""Build an AGNB container from the processed unsigned-PCM WAV files.

Provisional AGNB 0.2 audio record layout::

    LIST BUFR
      BHDR  u16 bufferId
      AUDI  u8 vdpFormat=0x09; u16 sampleRate
      DATA  unsigned 8-bit mono PCM bytes

The AUDI payload is deliberately the exact tail required by the VDP's
buffer-to-sound create-sample command: format 1 selects unsigned 8-bit mono
PCM, bit 3 announces that the two-byte sample-rate argument follows.
"""

import argparse
import struct
import wave
from dataclasses import dataclass
from pathlib import Path


AUDIO_DIR = Path(__file__).resolve().parents[1]
PROCESSED_DIR = AUDIO_DIR / "assets" / "processed"
TARGET_DIR = AUDIO_DIR / "tgt"
CONTAINER_FILE = TARGET_DIR / "sfx.agnb"

VERSION_MAJOR = 0
VERSION_MINOR = 2
DEFAULT_START_BUFFER_ID = 0xFB00
INVALID_BUFFER_ID = 0xFFFF
MAX_U16 = 0xFFFF
MAX_U32 = 0xFFFFFFFF
VDP_FORMAT_UNSIGNED_8BIT_MONO_WITH_RATE = 0x09


@dataclass(frozen=True)
class AudioRecord:
    name: str
    bufferId: int
    sampleRate: int
    pcm: bytes


def parse_int(value: str) -> int:
    """Accept decimal or Python-style hexadecimal command-line integers."""
    try:
        return int(value, 0)
    except ValueError as error:
        raise argparse.ArgumentTypeError(f"invalid integer: {value}") from error


def align4(size: int) -> int:
    return (size + 3) & ~3


def make_chunk(chunk_id: bytes, payload: bytes) -> bytes:
    if len(chunk_id) != 4:
        raise ValueError(f"RIFF chunk ID must contain four bytes: {chunk_id!r}")
    if len(payload) > MAX_U32:
        raise ValueError(f"RIFF payload is too large: {len(payload)} bytes")
    return (
        chunk_id
        + struct.pack("<I", len(payload))
        + payload
        + bytes(align4(len(payload)) - len(payload))
    )


def load_audio_records(start_buffer_id: int) -> list[AudioRecord]:
    sources = sorted(
        path
        for path in PROCESSED_DIR.iterdir()
        if path.is_file() and path.suffix.lower() == ".wav"
    )
    if not sources:
        raise RuntimeError(
            f"No processed WAV files found in {PROCESSED_DIR}; "
            "run prepare_audio.py first"
        )
    if not 0 <= start_buffer_id < INVALID_BUFFER_ID:
        raise ValueError(f"Invalid starting bufferId: {start_buffer_id:#x}")
    if start_buffer_id + len(sources) > INVALID_BUFFER_ID:
        raise ValueError("Assigned bufferIds would include or exceed reserved 0xFFFF")

    records = []
    for index, source in enumerate(sources):
        with wave.open(str(source), "rb") as wav:
            if wav.getcomptype() != "NONE":
                raise ValueError(f"{source.name} is not uncompressed PCM")
            if wav.getnchannels() != 1:
                raise ValueError(f"{source.name} is not mono")
            if wav.getsampwidth() != 1:
                raise ValueError(f"{source.name} is not 8-bit PCM")
            sample_rate = wav.getframerate()
            if not 1 <= sample_rate <= MAX_U16:
                raise ValueError(
                    f"{source.name} sample rate cannot fit a VDP u16: {sample_rate}"
                )
            frame_count = wav.getnframes()
            if frame_count == 0:
                raise ValueError(f"{source.name} contains no PCM samples")
            pcm = wav.readframes(frame_count)

        if len(pcm) != frame_count:
            raise ValueError(
                f"{source.name} PCM size mismatch: {len(pcm)} != {frame_count}"
            )
        records.append(
            AudioRecord(
                name=source.stem,
                bufferId=start_buffer_id + index,
                sampleRate=sample_rate,
                pcm=pcm,
            )
        )
    return records


def make_buffer_record(record: AudioRecord) -> bytes:
    nested = b"".join(
        (
            make_chunk(b"BHDR", struct.pack("<H", record.bufferId)),
            make_chunk(
                b"AUDI",
                struct.pack(
                    "<BH",
                    VDP_FORMAT_UNSIGNED_8BIT_MONO_WITH_RATE,
                    record.sampleRate,
                ),
            ),
            make_chunk(b"DATA", record.pcm),
        )
    )
    return make_chunk(b"LIST", b"BUFR" + nested)


def build_container(records: list[AudioRecord]) -> bytes:
    body = bytearray(b"AGNB")
    body.extend(make_chunk(b"VERS", bytes((VERSION_MAJOR, VERSION_MINOR))))
    for record in records:
        body.extend(make_buffer_record(record))
    if len(body) > MAX_U32:
        raise ValueError(f"RIFF container is too large: {len(body) + 8} bytes")
    return b"RIFF" + struct.pack("<I", len(body)) + body


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build sfx.agnb from processed unsigned 8-bit PCM WAV files."
    )
    parser.add_argument(
        "--start-buffer-id",
        type=parse_int,
        default=DEFAULT_START_BUFFER_ID,
        help="First explicit bufferId (default: 0xFB00).",
    )
    args = parser.parse_args()

    records = load_audio_records(args.start_buffer_id)
    container = build_container(records)
    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    CONTAINER_FILE.write_bytes(container)

    for record in records:
        print(
            f"{record.name}: bufferId=0x{record.bufferId:04X}, "
            f"sampleRate={record.sampleRate}, dataSize={len(record.pcm)}"
        )
    print(
        f"Generated {CONTAINER_FILE} with {len(records)} audio records "
        f"({len(container)} bytes)"
    )


if __name__ == "__main__":
    main()
