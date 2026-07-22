#!/usr/bin/env python3
"""Create an AGNB emulator instance at a caller-specified directory."""

import argparse
from pathlib import Path


SHARED_EMULATOR_DIR = Path.home() / "Agon" / "fab-agon-emulator"


def ensure_symlink(link: Path, target: Path) -> None:
    if not target.exists():
        raise FileNotFoundError(f"Shared emulator resource not found: {target}")

    if link.is_symlink():
        if link.resolve() == target.resolve():
            print(f"Already linked: {link} -> {target}")
            return
        raise RuntimeError(f"Refusing to replace different symlink: {link}")

    if link.exists():
        raise RuntimeError(f"Refusing to replace existing path: {link}")

    link.symlink_to(target, target_is_directory=target.is_dir())
    print(f"Linked: {link} -> {target}")


def setup_emulator(emulator_dir: Path) -> None:
    emulator_dir = emulator_dir.expanduser().resolve()
    variant_name = emulator_dir.parent.name
    sdcard_dir = emulator_dir / "sdcard"
    autoexec_text = (
        "SET KEYBOARD 1\n"
        f"cd mystuff/agon-utils/examples/agnb/{variant_name}/tgt\n"
        "load app.bin\n"
    )

    emulator_dir.mkdir(parents=True, exist_ok=True)
    sdcard_dir.mkdir(parents=True, exist_ok=True)
    (sdcard_dir / "mystuff").mkdir(exist_ok=True)

    ensure_symlink(
        emulator_dir / "firmware",
        SHARED_EMULATOR_DIR / "firmware",
    )
    ensure_symlink(
        emulator_dir / "fab-agon-emulator",
        SHARED_EMULATOR_DIR / "fab-agon-emulator",
    )

    for name in ("bin", "mos", "firmware.bin", "MOS.bin"):
        ensure_symlink(
            sdcard_dir / name,
            SHARED_EMULATOR_DIR / "sdcard" / name,
        )

    local_autoexec = sdcard_dir / "autoexec.txt"
    if local_autoexec.is_file() and local_autoexec.read_text() == autoexec_text:
        print(f"Already configured: {local_autoexec}")
    else:
        local_autoexec.write_text(autoexec_text)
        print(f"Configured: {local_autoexec}")

    print(f"AGNB emulator instance ready: {emulator_dir}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create an AGNB-local emulator directory using shared symlinks."
    )
    parser.add_argument(
        "emulator_dir",
        type=Path,
        help="Target emulator directory, such as loose/.emulator.",
    )
    args = parser.parse_args()
    setup_emulator(args.emulator_dir)


if __name__ == "__main__":
    main()
