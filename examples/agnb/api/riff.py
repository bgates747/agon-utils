"""Shared AGNB RIFF framing, including this format's four-byte padding."""
import struct

MAX_U32 = 0xFFFFFFFF


def align4(size: int) -> int:
    return (size + 3) & ~3


def make_chunk(chunk_id: bytes, payload: bytes) -> bytes:
    """Existing image/audio framing, shared without changing emitted bytes."""
    if len(chunk_id) != 4:
        raise ValueError(f"RIFF chunk ID must contain four bytes: {chunk_id!r}")
    if len(payload) > MAX_U32:
        raise ValueError(f"RIFF payload is too large: {len(payload)} bytes")
    padding = bytes(align4(len(payload)) - len(payload))
    return chunk_id + struct.pack("<I", len(payload)) + payload + padding
