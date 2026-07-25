#!/usr/bin/env python3
"""Convert the local AGNB audio samples to unsigned 8-bit PCM WAV files."""

import shutil
import subprocess
from pathlib import Path


AUDIO_DIR = Path(__file__).resolve().parents[1]
ORIGINAL_DIR = AUDIO_DIR / "assets" / "original"
PROCESSED_DIR = AUDIO_DIR / "assets" / "processed"
def prepare_audio() -> None:
    sources = sorted(
        path
        for path in ORIGINAL_DIR.iterdir()
        if path.is_file() and path.suffix.lower() == ".wav"
    )
    if not sources:
        raise RuntimeError(f"No WAV files found in {ORIGINAL_DIR}")

    if PROCESSED_DIR.exists():
        shutil.rmtree(PROCESSED_DIR)
    PROCESSED_DIR.mkdir(parents=True)

    for source in sources:
        destination = PROCESSED_DIR / source.name
        subprocess.run(
            [
                "ffmpeg",
                "-hide_banner",
                "-loglevel",
                "error",
                "-y",
                "-i",
                str(source),
                "-ac",
                "1",
                "-acodec",
                "pcm_u8",
                str(destination),
            ],
            check=True,
        )
        size = destination.stat().st_size
        print(f"Prepared {destination.name}: {size} bytes")

    print(f"Generated {len(sources)} unsigned 8-bit PCM WAV files in {PROCESSED_DIR}")


if __name__ == "__main__":
    prepare_audio()
