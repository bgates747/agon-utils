#!/usr/bin/env python3
"""Create or verify the project-local bespoke Fab emulator profile."""

from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent.parent
AGON_ROOT = Path.home() / "Agon"
FAB_ROOT = AGON_ROOT / "mystuff" / "fab-agon-emulator"
VDP_ROOT = AGON_ROOT / "mystuff" / "agon-vdp-sprite-transforms"
PROFILE = PROJECT_DIR / "emulator"
MODULE_NAME = "vdp_sprite_affine_transforms.so"
MODULE = VDP_ROOT / "video" / "build" / "userspace" / MODULE_NAME


def ensure_symlink(link: Path, target: Path, *, allow_missing=False) -> None:
    if not target.exists() and not allow_missing:
        raise FileNotFoundError(f"Required emulator input is absent: {target}")
    if link.is_symlink():
        if link.readlink() == target:
            return
        raise RuntimeError(f"Refusing to replace different symlink: {link}")
    if link.exists():
        raise RuntimeError(f"Refusing to replace existing path: {link}")
    link.symlink_to(target, target_is_directory=target.is_dir())


def main() -> None:
    PROFILE.mkdir(parents=True, exist_ok=True)
    build_dir = PROJECT_DIR / "build"
    build_dir.mkdir(exist_ok=True)
    sdcard = PROFILE / "sdcard"
    sdcard.mkdir(exist_ok=True)

    ensure_symlink(
        PROFILE / "fab-agon-emulator",
        FAB_ROOT / "target" / "release" / "fab-agon-emulator",
    )
    ensure_symlink(PROFILE / "mos_console8.bin", FAB_ROOT / "firmware" / "mos_console8.bin")
    ensure_symlink(PROFILE / "mos_console8.map", FAB_ROOT / "firmware" / "mos_console8.map")
    ensure_symlink(PROFILE / MODULE_NAME, MODULE, allow_missing=True)
    ensure_symlink(sdcard / "sprite_affine_transforms", build_dir)

    marker = PROFILE / ".bespoke-vdp-profile"
    marker.write_text(f"{MODULE_NAME}\n", encoding="utf-8")
    print(f"Bespoke profile ready: {PROFILE}")
    if not MODULE.exists():
        print(f"Blocked pending native VDP module: {MODULE}")


if __name__ == "__main__":
    main()
