"""Tests for the editable shared image manifest."""

import sys
import tempfile
import unittest
from pathlib import Path


SHARED_SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SHARED_SCRIPTS_DIR))

from image_manifest import (  # noqa: E402
    ImageManifestEntry,
    included_entries,
    load_manifest,
    write_manifest,
)


class ImageManifestTests(unittest.TestCase):
    def test_round_trip_preserves_order_bufferIds_and_selection(self):
        entries = [
            ImageManifestEntry(
                include=True,
                source="first source.png",
                name="first",
                bufferId=400,
                width=2,
                height=3,
                format=1,
                png="first.png",
                rgba2="first.rgba2",
                dataSize=6,
            ),
            ImageManifestEntry(
                include=False,
                source="second source.png",
                name="second",
                bufferId=900,
                width=4,
                height=5,
                format=1,
                png="second.png",
                rgba2="second.rgba2",
                dataSize=20,
            ),
        ]
        with tempfile.TemporaryDirectory() as temp_dir:
            manifest_file = Path(temp_dir) / "images.jsonl"
            write_manifest(manifest_file, entries)
            loaded = load_manifest(manifest_file)

        self.assertEqual(loaded, entries)
        self.assertEqual(included_entries(loaded), [entries[0]])
        self.assertEqual(loaded[0].bufferId, 400)
        self.assertEqual(loaded[1].bufferId, 900)


if __name__ == "__main__":
    unittest.main()
