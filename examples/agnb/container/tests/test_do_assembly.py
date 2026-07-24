"""Independent format checks for the AGNB container writer."""

import importlib.util
import struct
import tempfile
import unittest
from pathlib import Path

from PIL import Image


SCRIPT_FILE = Path(__file__).resolve().parents[1] / "scripts" / "do_assembly.py"
SPEC = importlib.util.spec_from_file_location("container_do_assembly", SCRIPT_FILE)
WRITER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(WRITER)


def read_chunk(data: bytes, offset: int, boundary: int):
    if offset + 8 > boundary:
        raise AssertionError(f"truncated chunk header at {offset}")
    chunk_id = data[offset : offset + 4]
    payload_size = struct.unpack_from("<I", data, offset + 4)[0]
    payload_start = offset + 8
    payload_end = payload_start + payload_size
    next_offset = payload_start + ((payload_size + 3) & ~3)
    if payload_end > boundary or next_offset > boundary:
        raise AssertionError(f"chunk {chunk_id!r} crosses its boundary")
    if any(data[payload_end:next_offset]):
        raise AssertionError(f"chunk {chunk_id!r} has nonzero padding")
    return chunk_id, payload_start, payload_end, next_offset


class ContainerWriterTests(unittest.TestCase):
    def test_images_include_contains_application_metadata_without_filenames(self):
        records = WRITER.load_image_records()
        with tempfile.TemporaryDirectory() as temporary_directory:
            original_output = WRITER.ASM_IMAGES_FILE
            try:
                WRITER.ASM_IMAGES_FILE = Path(temporary_directory) / "images.inc"
                WRITER.write_images_include(records)
                generated = WRITER.ASM_IMAGES_FILE.read_text()
            finally:
                WRITER.ASM_IMAGES_FILE = original_output

        first = records[0]
        self.assertIn("image_width: equ image_type+3", generated)
        self.assertIn("image_height: equ image_width+3", generated)
        self.assertIn("image_filesize: equ image_height+3", generated)
        self.assertIn("image_ex_filename: equ image_filesize+3", generated)
        self.assertIn("image_record_size: equ image_ex_filename+3", generated)
        self.assertIn(f"buf_{first.name}: equ {first.bufferId}", generated)
        self.assertIn("image_bufferIds:", generated)
        self.assertIn(f"\tdw {first.bufferId}\n", generated)
        self.assertIn(
            f"\tdl 1, {first.width}, {first.height}, {first.dataSize}, "
            "0xFFFFFF\n",
            generated,
        )
        self.assertNotIn("image_filename", generated)
        self.assertNotIn("fn_", generated)
        self.assertNotIn(".rgba2", generated)

    def test_full_container_matches_shared_assets(self):
        records = WRITER.load_image_records()
        container = WRITER.build_container(records)

        self.assertEqual(container[:4], b"RIFF")
        self.assertEqual(struct.unpack_from("<I", container, 4)[0], len(container) - 8)
        self.assertEqual(container[8:12], b"AGNB")

        offset = 12
        chunk_id, start, end, offset = read_chunk(container, offset, len(container))
        self.assertEqual(chunk_id, b"VERS")
        self.assertEqual(container[start:end], b"\x00\x01")

        record_index = 0
        while offset < len(container):
            chunk_id, list_start, list_end, offset = read_chunk(
                container, offset, len(container)
            )
            self.assertEqual(chunk_id, b"LIST")
            self.assertEqual(container[list_start : list_start + 4], b"BUFR")

            nested_offset = list_start + 4
            nested = []
            while nested_offset < list_end:
                item = read_chunk(container, nested_offset, list_end)
                nested.append(item)
                nested_offset = item[3]
            self.assertEqual(nested_offset, list_end)
            self.assertEqual([item[0] for item in nested], [b"BHDR", b"IMAG", b"DATA"])

            record = records[record_index]
            _id, payload_start, payload_end, _next = nested[0]
            self.assertEqual(payload_end - payload_start, 2)
            self.assertEqual(
                struct.unpack_from("<H", container, payload_start)[0],
                record.bufferId,
            )

            _id, payload_start, payload_end, _next = nested[1]
            self.assertEqual(payload_end - payload_start, 5)
            width, height, image_format = struct.unpack_from(
                "<HHB", container, payload_start
            )
            self.assertEqual((width, height, image_format), (record.width, record.height, 1))

            _id, payload_start, payload_end, _next = nested[2]
            self.assertEqual(payload_end - payload_start, record.width * record.height)
            self.assertEqual(container[payload_start:payload_end], record.rgbaFile.read_bytes())
            record_index += 1

        self.assertEqual(offset, len(container))
        self.assertEqual(record_index, len(records))
        self.assertEqual(len(records), 250)
        self.assertLessEqual(len(records), 256)

        for record in records:
            png_file = WRITER.SHARED_PROCESSED_DIR / f"{record.name}.png"
            with Image.open(png_file) as image:
                self.assertEqual(image.size, (record.width, record.height))


if __name__ == "__main__":
    unittest.main()
