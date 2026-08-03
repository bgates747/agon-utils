#!/usr/bin/env python3
"""Create or verify the project-local bespoke Fab emulator profile."""

import argparse

from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent.parent
AGON_ROOT = Path.home() / "Agon"
LEGACY_FAB_ROOT = AGON_ROOT / "mystuff" / "fab-agon-emulator"
FAB_ROOT = AGON_ROOT / "mystuff" / "fab-agon-emulator-sprite-transforms"
VDP_ROOT = AGON_ROOT / "mystuff" / "agon-vdp-sprite-transforms"
PROFILE = PROJECT_DIR / "emulator"
MODULE_NAME = "vdp_sprite_affine_transforms.so"
MODULE = VDP_ROOT / "video" / "build" / "userspace" / MODULE_NAME
FIXTURES = {
    "transforms": "sprite_affine_transforms.bin",
    "formats": "sprite_affine_formats.bin",
    "torture": "sprite_affine_torture.bin",
}
OLD_AUTOEXEC = (
    b"SET KEYBOARD 1\r\n"
    b"cd /sprite_affine_transforms\r\n"
    b"load sprite_affine_transforms.bin\r\n"
)
AUTOEXEC = OLD_AUTOEXEC + b"run\r\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create or verify the sprite-affine Fab profile."
    )
    parser.add_argument(
        "--fixture",
        choices=FIXTURES,
        help=(
            "replace autoexec.txt with the selected generated fixture; without "
            "this option, an existing autoexec.txt is preserved"
        ),
    )
    return parser.parse_args()


def autoexec_for(binary_name: str) -> bytes:
    return (
        b"SET KEYBOARD 1\r\n"
        b"cd /sprite_affine_transforms\r\n"
        + f"load {binary_name}\r\n".encode("ascii")
        + b"run\r\n"
    )


def ensure_symlink(
    link: Path,
    target: Path,
    *,
    allow_missing: bool = False,
    migrate_from: tuple[Path, ...] = (),
) -> None:
    if not target.exists() and not allow_missing:
        raise FileNotFoundError(f"Required emulator input is absent: {target}")
    if link.is_symlink():
        current_target = link.readlink()
        if current_target == target:
            return
        if current_target in migrate_from:
            link.unlink()
            link.symlink_to(target, target_is_directory=target.is_dir())
            print(f"Migrated generated symlink: {link} -> {target}")
            return
        raise RuntimeError(f"Refusing to replace different symlink: {link}")
    if link.exists():
        raise RuntimeError(f"Refusing to replace existing path: {link}")
    link.symlink_to(target, target_is_directory=target.is_dir())


def main() -> None:
    args = parse_args()
    PROFILE.mkdir(parents=True, exist_ok=True)
    build_dir = PROJECT_DIR / "build"
    build_dir.mkdir(exist_ok=True)
    sdcard = PROFILE / "sdcard"
    sdcard.mkdir(exist_ok=True)

    ensure_symlink(
        PROFILE / "fab-agon-emulator",
        FAB_ROOT / "target" / "release" / "fab-agon-emulator",
        migrate_from=(
            LEGACY_FAB_ROOT / "target" / "release" / "fab-agon-emulator",
        ),
    )
    ensure_symlink(
        PROFILE / "mos_console8.bin",
        FAB_ROOT / "firmware" / "mos_console8.bin",
        migrate_from=(LEGACY_FAB_ROOT / "firmware" / "mos_console8.bin",),
    )
    ensure_symlink(
        PROFILE / "mos_console8.map",
        FAB_ROOT / "firmware" / "mos_console8.map",
        migrate_from=(LEGACY_FAB_ROOT / "firmware" / "mos_console8.map",),
    )
    ensure_symlink(PROFILE / MODULE_NAME, MODULE, allow_missing=True)
    ensure_symlink(sdcard / "sprite_affine_transforms", build_dir)

    autoexec = sdcard / "autoexec.txt"
    if autoexec.is_symlink():
        raise RuntimeError(f"Refusing symlink in place of autoexec file: {autoexec}")
    if args.fixture:
        fixture_binary = build_dir / FIXTURES[args.fixture]
        if not fixture_binary.is_file():
            raise FileNotFoundError(f"Selected fixture is absent: {fixture_binary}")
        if autoexec.exists() and not autoexec.is_file():
            raise RuntimeError(f"Expected a regular autoexec file: {autoexec}")
        autoexec.write_bytes(autoexec_for(fixture_binary.name))
        print(f"Selected fixture for next launch: {fixture_binary.name}")
    elif not autoexec.exists():
        autoexec.write_bytes(AUTOEXEC)
    elif not autoexec.is_file():
        raise RuntimeError(f"Expected a regular autoexec file: {autoexec}")
    elif autoexec.read_bytes() == OLD_AUTOEXEC:
        autoexec.write_bytes(AUTOEXEC)

    marker = PROFILE / ".bespoke-vdp-profile"
    marker.write_text(f"{MODULE_NAME}\n", encoding="utf-8")
    print(f"Bespoke profile ready: {PROFILE}")
    if not MODULE.exists():
        print(f"Blocked pending native VDP module: {MODULE}")


if __name__ == "__main__":
    main()
