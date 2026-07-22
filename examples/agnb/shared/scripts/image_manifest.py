"""Read and write the shared line-oriented AGNB image manifest."""

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from PIL import Image


MANIFEST_FILENAME = "images.jsonl"
INVALID_BUFFER_ID = 0xFFFF
MAX_U16 = 0xFFFF


@dataclass(frozen=True)
class ImageManifestEntry:
    include: bool
    source: str
    name: str
    bufferId: int
    width: int
    height: int
    format: int
    png: str
    rgba2: str
    dataSize: int


def validate_entries(entries: list[ImageManifestEntry]) -> None:
    if not entries:
        raise ValueError("Image manifest contains no entries")

    names = set()
    bufferIds = set()
    png_files = set()
    rgba2_files = set()
    for entry in entries:
        if type(entry.include) is not bool:
            raise ValueError(f"include must be true or false for {entry.name}")
        if not entry.source or not entry.name or not entry.png or not entry.rgba2:
            raise ValueError("Manifest filenames and names must not be empty")
        if entry.name in names:
            raise ValueError(f"Duplicate manifest name: {entry.name}")
        if entry.bufferId in bufferIds:
            raise ValueError(f"Duplicate bufferId: {entry.bufferId}")
        if not 0 <= entry.bufferId < INVALID_BUFFER_ID:
            raise ValueError(f"Invalid bufferId for {entry.name}: {entry.bufferId}")
        if not 1 <= entry.width <= MAX_U16 or not 1 <= entry.height <= MAX_U16:
            raise ValueError(
                f"Invalid dimensions for {entry.name}: {entry.width}x{entry.height}"
            )
        if entry.format != 1:
            raise ValueError(f"Unsupported image format for {entry.name}: {entry.format}")
        if entry.dataSize != entry.width * entry.height:
            raise ValueError(
                f"Invalid RGBA2222 dataSize for {entry.name}: {entry.dataSize}"
            )
        if entry.png in png_files:
            raise ValueError(f"Duplicate PNG filename: {entry.png}")
        if entry.rgba2 in rgba2_files:
            raise ValueError(f"Duplicate RGBA2222 filename: {entry.rgba2}")

        names.add(entry.name)
        bufferIds.add(entry.bufferId)
        png_files.add(entry.png)
        rgba2_files.add(entry.rgba2)


def load_manifest(manifest_file: Path) -> list[ImageManifestEntry]:
    entries = []
    try:
        lines = manifest_file.read_text().splitlines()
    except FileNotFoundError as error:
        raise FileNotFoundError(
            f"Image manifest not found: {manifest_file}; "
            "run shared/scripts/prepare_images.py first"
        ) from error

    required_fields = tuple(ImageManifestEntry.__dataclass_fields__)
    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            values = json.loads(line)
        except json.JSONDecodeError as error:
            raise ValueError(
                f"Invalid JSON on manifest line {line_number}: {error.msg}"
            ) from error
        if not isinstance(values, dict):
            raise ValueError(f"Manifest line {line_number} must be a JSON object")
        if set(values) != set(required_fields):
            raise ValueError(
                f"Manifest line {line_number} fields must be: "
                f"{', '.join(required_fields)}"
            )
        try:
            entries.append(ImageManifestEntry(**values))
        except TypeError as error:
            raise ValueError(f"Invalid manifest line {line_number}: {error}") from error

    validate_entries(entries)
    return entries


def write_manifest(
    manifest_file: Path, entries: list[ImageManifestEntry]
) -> None:
    validate_entries(entries)
    text = "".join(json.dumps(asdict(entry)) + "\n" for entry in entries)
    manifest_file.write_text(text)


def included_entries(entries: list[ImageManifestEntry]) -> list[ImageManifestEntry]:
    selected = [entry for entry in entries if entry.include]
    if not selected:
        raise ValueError("Image manifest selects no entries")
    return selected


def validate_asset_files(
    entries: list[ImageManifestEntry], asset_dir: Path
) -> None:
    """Confirm that manifest metadata still matches its PNG and RGBA2222 files."""
    for entry in entries:
        png_file = asset_dir / entry.png
        rgba2_file = asset_dir / entry.rgba2
        if not png_file.is_file():
            raise FileNotFoundError(f"Manifest PNG not found: {png_file}")
        if not rgba2_file.is_file():
            raise FileNotFoundError(f"Manifest RGBA2222 file not found: {rgba2_file}")
        with Image.open(png_file) as image:
            if image.size != (entry.width, entry.height):
                raise ValueError(
                    f"PNG dimensions disagree with manifest for {entry.name}: "
                    f"manifest={entry.width}x{entry.height}, file={image.width}x{image.height}"
                )
        actual_size = rgba2_file.stat().st_size
        if actual_size != entry.dataSize:
            raise ValueError(
                f"RGBA2222 size disagrees with manifest for {entry.name}: "
                f"manifest={entry.dataSize}, file={actual_size}"
            )
