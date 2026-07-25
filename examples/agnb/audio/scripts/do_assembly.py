#!/usr/bin/env python3
"""Build, deploy, and optionally launch the AGNB audio test harness."""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


AUDIO_DIR = Path(__file__).resolve().parents[1]
SCRIPT_DIR = AUDIO_DIR / "scripts"
ASM_DIR = AUDIO_DIR / "src" / "asm"
TARGET_DIR = AUDIO_DIR / "tgt"
APP_BINARY = TARGET_DIR / "app.bin"
CONTAINER_FILE = TARGET_DIR / "sfx.agnb"

EMULATOR_DIR = AUDIO_DIR / ".emulator"
EMULATOR_SDCARD = EMULATOR_DIR / "sdcard"
EMULATOR_TARGET = (
    EMULATOR_SDCARD
    / "mystuff"
    / "agon-utils"
    / "examples"
    / "agnb"
    / "audio"
    / "tgt"
)
SHARED_EMULATOR_DIR = Path.home() / "Agon" / "fab-agon-emulator"
MOS_TARGET = "mystuff/agon-utils/examples/agnb/audio/tgt"


def run_python(script_name: str, *arguments: str) -> None:
    subprocess.run(
        [sys.executable, str(SCRIPT_DIR / script_name), *arguments],
        check=True,
        cwd=AUDIO_DIR.parents[2],
    )


def prepare_audio() -> None:
    run_python("prepare_audio.py")


def build_container(start_buffer_id: int) -> None:
    run_python(
        "build_audio_container.py",
        "--start-buffer-id",
        hex(start_buffer_id),
    )


def assemble() -> None:
    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        ["ez80asm", "-l", "app.asm", "../../tgt/app.bin"],
        check=True,
        cwd=ASM_DIR,
        capture_output=True,
        text=True,
    )
    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, end="", file=sys.stderr)
    print(f"Generated {APP_BINARY}")


def ensure_symlink(link: Path, target: Path) -> None:
    if not target.exists():
        raise FileNotFoundError(f"Shared emulator resource not found: {target}")
    if link.is_symlink():
        if link.resolve() == target.resolve():
            return
        raise RuntimeError(f"Refusing to replace different symlink: {link}")
    if link.exists():
        raise RuntimeError(f"Refusing to replace existing emulator path: {link}")
    link.symlink_to(target, target_is_directory=target.is_dir())


def setup_emulator() -> None:
    EMULATOR_SDCARD.mkdir(parents=True, exist_ok=True)
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
            EMULATOR_SDCARD / name,
            SHARED_EMULATOR_DIR / "sdcard" / name,
        )

    autoexec = (
        "SET KEYBOARD 1\n"
        f"cd {MOS_TARGET}\n"
        "load app.bin\n"
    )
    autoexec_file = EMULATOR_SDCARD / "autoexec.txt"
    if not autoexec_file.is_file() or autoexec_file.read_text() != autoexec:
        autoexec_file.write_text(autoexec)
    print(f"Audio emulator instance ready: {EMULATOR_DIR}")


def deploy() -> None:
    for required in (APP_BINARY, CONTAINER_FILE):
        if not required.is_file():
            raise FileNotFoundError(f"Build output not found: {required}")
    setup_emulator()
    if EMULATOR_TARGET.exists():
        shutil.rmtree(EMULATOR_TARGET)
    EMULATOR_TARGET.mkdir(parents=True)
    shutil.copy2(APP_BINARY, EMULATOR_TARGET / APP_BINARY.name)
    shutil.copy2(CONTAINER_FILE, EMULATOR_TARGET / CONTAINER_FILE.name)
    print(f"Deployed app.bin and sfx.agnb to {EMULATOR_TARGET}")


def launch_emulator() -> None:
    setup_emulator()
    environment = os.environ.copy()
    environment.setdefault("SDL_VIDEO_DRIVER", "wayland")
    process = subprocess.Popen(
        [str(EMULATOR_DIR / "fab-agon-emulator")],
        cwd=EMULATOR_DIR,
        env=environment,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    print(f"Launched fab-agon-emulator in background (PID {process.pid})")


def parse_int(value: str) -> int:
    try:
        return int(value, 0)
    except ValueError as error:
        raise argparse.ArgumentTypeError(f"invalid integer: {value}") from error


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build and deploy the AGNB audio test harness."
    )
    parser.add_argument("-p", "--prepare", action="store_true")
    parser.add_argument("-b", "--build-container", action="store_true")
    parser.add_argument("-a", "--assemble", action="store_true")
    parser.add_argument("-c", "--copy-to-emulator", action="store_true")
    parser.add_argument("-e", "--emulator", action="store_true")
    parser.add_argument(
        "--start-buffer-id",
        type=parse_int,
        default=0xFB00,
        help="First explicit audio bufferId (default: 0xFB00).",
    )
    args = parser.parse_args()

    selected = any(
        (
            args.prepare,
            args.build_container,
            args.assemble,
            args.copy_to_emulator,
            args.emulator,
        )
    )
    if not selected:
        prepare_audio()
        build_container(args.start_buffer_id)
        assemble()
        deploy()
        return

    if args.prepare:
        prepare_audio()
    if args.build_container:
        build_container(args.start_buffer_id)
    if args.assemble:
        assemble()
    if args.copy_to_emulator:
        deploy()
    if args.emulator:
        launch_emulator()


if __name__ == "__main__":
    main()
