#!/usr/bin/env python3
"""Prepare the PNG and RGBA2222 assets shared by both test harnesses."""

import argparse
import shutil
from pathlib import Path

import agonutils as au
from PIL import Image


PROJECT_DIR = Path(__file__).resolve().parents[2]
SHARED_DIR = PROJECT_DIR / "shared"
ORIGINALS_DIR = SHARED_DIR / "assets" / "orig"
PROCESSED_DIR = SHARED_DIR / "assets" / "processed"
PALETTE_FILE = PROJECT_DIR.parent / "slideshow" / "palettes" / "Agon64.gpl"

SUPPORTED_EXTENSIONS = {".png", ".jpeg", ".jpg", ".gif"}
TRANSPARENT_RGBA = (0, 0, 0, 0)
SCREEN_SIZE = (320, 240)


def crop_to_aspect(image: Image.Image, aspect: tuple[int, int] = (4, 3)) -> Image.Image:
    """Crop a wide image to the requested aspect ratio, centered horizontally."""
    target_aspect = aspect[0] / aspect[1]
    current_aspect = image.width / image.height
    if current_aspect <= target_aspect:
        return image

    new_width = int(image.height * target_aspect)
    left = (image.width - new_width) // 2
    return image.crop((left, 0, left + new_width, image.height))


def prepare_image(source: Path, destination: Path, unscaled: bool) -> None:
    with Image.open(source) as image:
        if unscaled:
            prepared = image.copy()
        else:
            prepared = crop_to_aspect(image).resize(SCREEN_SIZE, Image.Resampling.BICUBIC)
        prepared.save(destination, "PNG", icc_profile=None)

    au.convert_to_palette(
        str(destination),
        str(destination),
        str(PALETTE_FILE),
        "floyd",
        TRANSPARENT_RGBA,
    )
    au.img_to_rgba2(
        str(destination),
        str(destination.with_suffix(".rgba2")),
        str(PALETTE_FILE),
        "rgb",
        TRANSPARENT_RGBA,
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Prepare shared palettized PNG and RGBA2222 assets."
    )
    parser.add_argument(
        "--scaled",
        action="store_true",
        help="Crop and scale images to 320x240 instead of preserving their dimensions.",
    )
    args = parser.parse_args()

    sources = sorted(
        path
        for path in ORIGINALS_DIR.iterdir()
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
    )
    if not sources:
        raise RuntimeError(f"No supported source images found in {ORIGINALS_DIR}")

    if PROCESSED_DIR.exists():
        shutil.rmtree(PROCESSED_DIR)
    PROCESSED_DIR.mkdir(parents=True)

    for source in sources:
        destination = PROCESSED_DIR / f"{source.stem}.png"
        prepare_image(source, destination, not args.scaled)
        print(f"Prepared {destination.name} and {destination.with_suffix('.rgba2').name}")


if __name__ == "__main__":
    main()
