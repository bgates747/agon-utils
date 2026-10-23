#!/usr/bin/env python3
"""Generic AGNB 0.3 plain-buffer writer and strict host reader.

No application setup, implicit calls, buffer allocation, or data interpretation.
CLI: buffers.py manifest.json output.agnb
Manifest: {"records": [{"buffer_id": 42, "path": "payload.bin"}]}
Paths are resolved relative to the manifest and never stored in the container.
"""
import argparse
import json
import struct
from dataclasses import dataclass
from pathlib import Path
from riff import MAX_U32, make_chunk

VERSION = b'\0\3'
MAX_DATA = 0xFFFFFF


@dataclass(frozen=True)
class BufferRecord:
    buffer_id: int
    data: bytes


def validate_record(record: BufferRecord) -> None:
    if type(record.buffer_id) is not int or not 0 <= record.buffer_id < 65535:
        raise ValueError('buffer_id must be an integer in 0..65534')
    if not isinstance(record.data, bytes) or not 1 <= len(record.data) <= MAX_DATA:
        raise ValueError('plain DATA must contain 1..0xFFFFFF bytes')


def build_container(records: list[BufferRecord]) -> bytes:
    body = bytearray(b'AGNB' + make_chunk(b'VERS', VERSION))
    ids = set()
    for record in records:
        validate_record(record)
        if record.buffer_id in ids:
            raise ValueError(f'duplicate buffer ID: {record.buffer_id}')
        ids.add(record.buffer_id)
        nested = (make_chunk(b'BHDR', struct.pack('<H', record.buffer_id))
                  + make_chunk(b'RAWD', b'\0') + make_chunk(b'DATA', record.data))
        body.extend(make_chunk(b'LIST', b'BUFR' + nested))
        if len(body) > MAX_U32:
            raise ValueError('container exceeds RIFF u32 size')
    return b'RIFF' + struct.pack('<I', len(body)) + body


def read_container(data: bytes) -> list[BufferRecord]:
    """Validate exact bounds/order/padding before returning plain records.

    Host validation may hold a whole container; eZ80 incremental loading is a
    separate API. Repeated IDs are rejected by the writer, but the on-disk
    format permits explicit sequential replacement, matching the target loader.
    """
    if len(data) < 12 or data[:4] != b'RIFF' or data[8:12] != b'AGNB':
        raise ValueError('not a RIFF/AGNB container')
    if struct.unpack_from('<I', data, 4)[0] != len(data) - 8:
        raise ValueError('RIFF size does not match physical size')

    def chunk(at, boundary, expected):
        if at + 8 > boundary:
            raise ValueError('truncated chunk header')
        kind = data[at:at+4]
        size = struct.unpack_from('<I', data, at+4)[0]
        start = at + 8
        end = start + size
        next_at = start + ((size + 3) & ~3)
        if kind != expected:
            raise ValueError(f'expected {expected!r}, got {kind!r}')
        if end > boundary or next_at > boundary or any(data[end:next_at]):
            raise ValueError('chunk crosses boundary or has nonzero padding')
        return start, end, next_at

    start, end, at = chunk(12, len(data), b'VERS')
    if data[start:end] != VERSION:
        raise ValueError('unsupported plain-buffer version')
    result = []
    while at < len(data):
        start, end, at = chunk(at, len(data), b'LIST')
        if data[start:start+4] != b'BUFR':
            raise ValueError('expected LIST BUFR')
        pos = start + 4
        a, b, pos = chunk(pos, end, b'BHDR')
        if b-a != 2:
            raise ValueError('BHDR must contain exactly one u16 ID')
        buffer_id = struct.unpack_from('<H', data, a)[0]
        a, b, pos = chunk(pos, end, b'RAWD')
        if data[a:b] != b'\0':
            raise ValueError('RAWD must be one byte0 (consolidated plain data)')
        a, b, pos = chunk(pos, end, b'DATA')
        if pos != end:
            raise ValueError('unexpected trailing record contents')
        record = BufferRecord(buffer_id, data[a:b])
        validate_record(record)
        result.append(record)
    return result


def write_manifest(manifest: Path, output: Path) -> None:
    document = json.loads(manifest.read_text())
    if not isinstance(document, dict) or set(document) != {'records'} or not isinstance(document['records'], list):
        raise ValueError('manifest must contain only a records list')
    records = []
    for item in document['records']:
        if not isinstance(item, dict) or set(item) != {'buffer_id', 'path'} or not isinstance(item['path'], str) or not item['path']:
            raise ValueError('each record requires buffer_id and a nonempty path')
        path = manifest.parent / item['path']
        size = path.stat().st_size
        if not 1 <= size <= MAX_DATA:
            raise ValueError('input file must contain 1..0xFFFFFF bytes')
        records.append(BufferRecord(item['buffer_id'], path.read_bytes()))
    # All semantic/input validation completes before output mutation.
    encoded = build_container(records)
    output.write_bytes(encoded)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    write_manifest(args.manifest, args.output)


if __name__ == '__main__':
    main()
