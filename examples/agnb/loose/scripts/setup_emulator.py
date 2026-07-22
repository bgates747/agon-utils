#!/usr/bin/env python3
"""Create an AGNB-local fab-agon-emulator instance using shared symlinks."""

from pathlib import Path
import shutil


AGNB_DIR = Path(__file__).resolve().parent.parent
EMULATOR_DIR = AGNB_DIR / ".emulator"
SDCARD_DIR = EMULATOR_DIR / "sdcard"
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


def main() -> None:
    EMULATOR_DIR.mkdir(parents=True, exist_ok=True)
    SDCARD_DIR.mkdir(parents=True, exist_ok=True)
    (SDCARD_DIR / "mystuff").mkdir(exist_ok=True)

    ensure_symlink(
        EMULATOR_DIR / "firmware",
        SHARED_EMULATOR_DIR / "firmware",
    )
    ensure_symlink(
        EMULATOR_DIR / "fab-agon-emulator",
        SHARED_EMULATOR_DIR / "fab-agon-emulator",
    )

    for name in ("bin", "mos", "firmware.bin", "MOS.bin"):
        ensure_symlink(
            SDCARD_DIR / name,
            SHARED_EMULATOR_DIR / "sdcard" / name,
        )

    shared_autoexec = SHARED_EMULATOR_DIR / "sdcard" / "autoexec.txt"
    local_autoexec = SDCARD_DIR / "autoexec.txt"
    if local_autoexec.exists():
        print(f"Keeping existing local autoexec: {local_autoexec}")
    else:
        if not shared_autoexec.is_file():
            raise FileNotFoundError(
                f"Shared emulator autoexec not found: {shared_autoexec}"
            )
        shutil.copy2(shared_autoexec, local_autoexec)
        print(f"Copied: {shared_autoexec} -> {local_autoexec}")

    print(f"AGNB emulator instance ready: {EMULATOR_DIR}")


if __name__ == "__main__":
    main()
