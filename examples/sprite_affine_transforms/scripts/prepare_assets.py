#!/usr/bin/env python3
"""Generate deterministic bitmap payloads for sprite affine-transform tests."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

import agonutils as au
from PIL import Image


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = PROJECT_ROOT.parents[1]
ASSETS_DIR = PROJECT_ROOT / "assets"
SOURCE_DIR = ASSETS_DIR / "source"
RGBA2222_DIR = ASSETS_DIR / "rgba2222"
RGBA8888_DIR = ASSETS_DIR / "rgba8888"
MASK_DIR = ASSETS_DIR / "mask"
MANIFEST_FILE = ASSETS_DIR / "manifest.json"
PALETTE_FILE = REPOSITORY_ROOT / "examples" / "palettes" / "Agon64.gpl"
PALETTE_SHA256 = "c61dd1476415352e74add70f1ed0c81b1d141361a12b26587a6829ee66ec7f94"


@dataclass(frozen=True)
class ImageFixture:
    name: str
    source_filename: str
    origin_path: str
    source_sha256: str
    width: int
    height: int
    source_mode: str
    purpose: str
    embed_by_default: bool


IMAGE_FIXTURES = (
    ImageFixture(
        name="ship_1c",
        source_filename="ship_1c.png",
        origin_path="assets/img/orig/sprites/ship_1c.png",
        source_sha256="fc4c814eea915ff3d4967a320854ee533928957ed8f3bd2f5204194f87533862",
        width=16,
        height=16,
        source_mode="P",
        purpose="small asymmetric baseline",
        embed_by_default=True,
    ),
    ImageFixture(
        name="laser_a_5x13",
        source_filename="laser_a_5x13.png",
        origin_path="assets/img/orig/sprites/laser_a.png",
        source_sha256="2137b6e51bdc8c9e02e55316ee61008be6f94f34a4451c7131f4b749d9c877f1",
        width=5,
        height=13,
        source_mode="RGBA",
        purpose="odd-width and odd-height affine bounds torture",
        embed_by_default=True,
    ),
    ImageFixture(
        name="ctl_panel_top_352x48",
        source_filename="ctl_panel_top_352x48.png",
        origin_path="assets/img/proc/ui/ctl_panel_top.png",
        source_sha256="8f869d20ae1fb20bc8939acec48709aa801c484a910fc9d78e1e0cc35907be38",
        width=352,
        height=48,
        source_mode="RGBA",
        purpose="large wide clipping and multi-block RGBA8888 upload torture",
        embed_by_default=False,
    ),
)

MASK_NAME = "mask_9x5_msb"
MASK_SOURCE_FILE = SOURCE_DIR / f"{MASK_NAME}.txt"
MASK_WIDTH = 9
MASK_HEIGHT = 5
EXPECTED_MASK_HEX = "808060002a001d00a380"

ALPHA_EDGE_NAME = "rgba8888_alpha_edge_12x8"
ALPHA_EDGE_WIDTH = 12
ALPHA_EDGE_HEIGHT = 8
EXPECTED_ALPHA_EDGE_SHA256 = (
    "686f080d188051e1e8cc00a21210d0f76050ec95e9325e2d12b324e4dcd1b0e2"
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(64 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def relative_path(path: Path) -> str:
    return path.relative_to(PROJECT_ROOT).as_posix()


def file_record(path: Path, width: int, height: int, image_format: str) -> dict[str, object]:
    return {
        "path": relative_path(path),
        "width": width,
        "height": height,
        "format": image_format,
        "byte_size": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def validate_runtime() -> None:
    module_path = Path(au.__file__).resolve()
    if not module_path.is_relative_to(REPOSITORY_ROOT):
        raise RuntimeError(
            f"agonutils must load from {REPOSITORY_ROOT}, not {module_path}"
        )
    actual_palette_hash = sha256_file(PALETTE_FILE)
    if actual_palette_hash != PALETTE_SHA256:
        raise RuntimeError(
            f"Agon64 palette checksum mismatch: expected {PALETTE_SHA256}, "
            f"got {actual_palette_hash}"
        )


def generate_image_fixture(fixture: ImageFixture) -> dict[str, object]:
    source_file = SOURCE_DIR / fixture.source_filename
    actual_source_hash = sha256_file(source_file)
    if actual_source_hash != fixture.source_sha256:
        raise RuntimeError(
            f"Source checksum mismatch for {source_file}: expected "
            f"{fixture.source_sha256}, got {actual_source_hash}"
        )

    with Image.open(source_file) as image:
        image.load()
        if image.size != (fixture.width, fixture.height):
            raise RuntimeError(
                f"Unexpected dimensions for {source_file}: expected "
                f"{fixture.width}x{fixture.height}, got {image.width}x{image.height}"
            )
        if image.mode != fixture.source_mode:
            raise RuntimeError(
                f"Unexpected Pillow mode for {source_file}: expected "
                f"{fixture.source_mode}, got {image.mode}"
            )
        rgba8888 = image.convert("RGBA").tobytes("raw", "RGBA")

    rgba2222_file = RGBA2222_DIR / f"{fixture.name}.rgba2222"
    au.img_to_rgba2(
        str(source_file),
        str(rgba2222_file),
        str(PALETTE_FILE),
        "rgb",
        None,
    )
    expected_rgba2222_size = fixture.width * fixture.height
    if rgba2222_file.stat().st_size != expected_rgba2222_size:
        raise RuntimeError(
            f"Unexpected RGBA2222 size for {rgba2222_file}: expected "
            f"{expected_rgba2222_size}, got {rgba2222_file.stat().st_size}"
        )

    rgba8888_file = RGBA8888_DIR / f"{fixture.name}.rgba8888"
    rgba8888_file.write_bytes(rgba8888)
    expected_rgba8888_size = fixture.width * fixture.height * 4
    if rgba8888_file.stat().st_size != expected_rgba8888_size:
        raise RuntimeError(
            f"Unexpected RGBA8888 size for {rgba8888_file}: expected "
            f"{expected_rgba8888_size}, got {rgba8888_file.stat().st_size}"
        )

    return {
        "name": fixture.name,
        "purpose": fixture.purpose,
        "embed_by_default": fixture.embed_by_default,
        "provenance": {
            "repository": "nurples",
            "path": fixture.origin_path,
            "sha256": fixture.source_sha256,
        },
        "source": file_record(
            source_file,
            fixture.width,
            fixture.height,
            f"PNG/{fixture.source_mode}",
        ),
        "derived": [
            file_record(
                rgba2222_file,
                fixture.width,
                fixture.height,
                "RGBA2222",
            ),
            file_record(
                rgba8888_file,
                fixture.width,
                fixture.height,
                "RGBA8888",
            ),
        ],
    }


def read_mask_rows() -> list[str]:
    rows = [
        line.strip()
        for line in MASK_SOURCE_FILE.read_text(encoding="ascii").splitlines()
        if line.strip() and not line.lstrip().startswith(";")
    ]
    if len(rows) != MASK_HEIGHT:
        raise RuntimeError(
            f"Mask source must have {MASK_HEIGHT} rows, found {len(rows)}"
        )
    for row in rows:
        if len(row) != MASK_WIDTH or set(row) - {".", "#"}:
            raise RuntimeError(
                f"Mask rows must be {MASK_WIDTH} characters of '.' and '#': {row!r}"
            )
    return rows


def pack_mask_msb(rows: list[str]) -> bytes:
    row_stride = (MASK_WIDTH + 7) // 8
    payload = bytearray()
    for row in rows:
        packed_row = bytearray(row_stride)
        for x, pixel in enumerate(row):
            if pixel == "#":
                packed_row[x // 8] |= 0x80 >> (x % 8)
        payload.extend(packed_row)
    return bytes(payload)


def generate_mask_fixture() -> dict[str, object]:
    rows = read_mask_rows()
    payload = pack_mask_msb(rows)
    if payload.hex() != EXPECTED_MASK_HEX:
        raise RuntimeError(
            f"Mask packing changed: expected {EXPECTED_MASK_HEX}, got {payload.hex()}"
        )

    mask_file = MASK_DIR / f"{MASK_NAME}.mask"
    mask_file.write_bytes(payload)
    return {
        "name": MASK_NAME,
        "provenance": {
            "repository": "agon-utils",
            "path": relative_path(MASK_SOURCE_FILE),
            "sha256": sha256_file(MASK_SOURCE_FILE),
        },
        "source": file_record(
            MASK_SOURCE_FILE,
            MASK_WIDTH,
            MASK_HEIGHT,
            "ASCII mask (#=1, .=0)",
        ),
        "derived": [
            {
                **file_record(
                    mask_file,
                    MASK_WIDTH,
                    MASK_HEIGHT,
                    "Mask/1bpp/MSB-first",
                ),
                "row_stride_bytes": (MASK_WIDTH + 7) // 8,
                "padding_bits": "zero",
            }
        ],
    }


def generate_rgba8888_alpha_edge_fixture() -> dict[str, object]:
    """Generate an RGBA8888 payload that distinguishes zero from low alpha.

    Rows 1..6 contain four three-pixel bands. The first has alpha zero; the
    next two use non-zero alpha values below 64; and the last is opaque. The
    opaque white top row and yellow bottom row make orientation obvious after
    an affine transform.
    """

    pixels = bytearray()
    for y in range(ALPHA_EDGE_HEIGHT):
        for x in range(ALPHA_EDGE_WIDTH):
            if y == 0:
                rgba = (255, 255, 255, 255)
            elif y == ALPHA_EDGE_HEIGHT - 1:
                rgba = (255, 255, 0, 255)
            elif x < 3:
                rgba = (255, 0, 255, 0)
            elif x < 6:
                rgba = (255, 0, 0, 1)
            elif x < 9:
                rgba = (0, 255, 0, 63)
            else:
                rgba = (0, 0, 255, 255)
            pixels.extend(rgba)

    payload = bytes(pixels)
    expected_size = ALPHA_EDGE_WIDTH * ALPHA_EDGE_HEIGHT * 4
    if len(payload) != expected_size:
        raise RuntimeError(
            f"Unexpected alpha-edge size: expected {expected_size}, got {len(payload)}"
        )

    rgba8888_file = RGBA8888_DIR / f"{ALPHA_EDGE_NAME}.rgba8888"
    rgba8888_file.write_bytes(payload)
    actual_hash = sha256_file(rgba8888_file)
    if actual_hash != EXPECTED_ALPHA_EDGE_SHA256:
        raise RuntimeError(
            "RGBA8888 alpha-edge payload changed: expected "
            f"{EXPECTED_ALPHA_EDGE_SHA256}, got {actual_hash}"
        )
    return {
        "name": ALPHA_EDGE_NAME,
        "purpose": "binary-alpha conversion edge: A=0 versus A=1 and A=63",
        "generated_source": {
            "implementation": (
                "scripts/prepare_assets.py:generate_rgba8888_alpha_edge_fixture"
            ),
            "bands": [
                {"x": "0..2", "rgba": [255, 0, 255, 0], "expected": "transparent"},
                {"x": "3..5", "rgba": [255, 0, 0, 1], "expected": "opaque red"},
                {"x": "6..8", "rgba": [0, 255, 0, 63], "expected": "opaque green"},
                {"x": "9..11", "rgba": [0, 0, 255, 255], "expected": "opaque blue"},
            ],
        },
        "derived": [
            file_record(
                rgba8888_file,
                ALPHA_EDGE_WIDTH,
                ALPHA_EDGE_HEIGHT,
                "RGBA8888",
            )
        ],
    }


def main() -> None:
    validate_runtime()
    RGBA2222_DIR.mkdir(parents=True, exist_ok=True)
    RGBA8888_DIR.mkdir(parents=True, exist_ok=True)
    MASK_DIR.mkdir(parents=True, exist_ok=True)

    manifest = {
        "schema_version": 1,
        "generated_by": "scripts/prepare_assets.py",
        "conversion": {
            "rgba2222": {
                "implementation": "agonutils.img_to_rgba2",
                "palette": {
                    "path": PALETTE_FILE.relative_to(REPOSITORY_ROOT).as_posix(),
                    "sha256": PALETTE_SHA256,
                },
                "method": "rgb",
                "transparent_color": None,
                "layout": "one byte per pixel, bits AA BB GG RR",
            },
            "rgba8888": {
                "implementation": "Pillow Image.convert('RGBA').tobytes('raw', 'RGBA')",
                "layout": "row-major R G B A bytes",
            },
            "mask": {
                "implementation": "scripts/prepare_assets.py:pack_mask_msb",
                "layout": "row-major, rows byte-aligned, pixel 0 in bit 7",
            },
        },
        "assets": [
            *(generate_image_fixture(fixture) for fixture in IMAGE_FIXTURES),
            generate_rgba8888_alpha_edge_fixture(),
            generate_mask_fixture(),
        ],
    }
    MANIFEST_FILE.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"Generated {MANIFEST_FILE} with {len(manifest['assets'])} fixtures")


if __name__ == "__main__":
    main()
