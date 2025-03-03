#!/usr/bin/env python3
import os
import shutil
import subprocess
import sys
import glob

def clean_build_artifacts():
    """Remove old build artifacts to avoid conflicts."""
    paths_to_remove = ["build", "dist", "agonutils.egg-info"]

    for path in paths_to_remove:
        if os.path.exists(path):
            print(f"Removing '{path}' directory...")
            shutil.rmtree(path)

def build_wheel():
    """Build the package as a distributable wheel."""
    print("Building wheel...")
    subprocess.run([sys.executable, "-m", "build"], check=True)

def install_wheel():
    """Find and install the freshly built wheel."""
    wheel_files = glob.glob("dist/*.whl")
    if not wheel_files:
        print("No wheel files found in 'dist/'")
        sys.exit(1)

    wheel_file = wheel_files[0]
    print(f"Installing {wheel_file} for testing...")
    subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", wheel_file], check=True)

def verify_install():
    """Verify the installed package is working."""
    print("Verifying installed wheel...")

    code = (
        "import agonutils; "
        "print('agonutils loaded from:', agonutils.__file__); "
        "agonutils.hello()"
    )

    subprocess.run([sys.executable, "-c", code], check=True)

if __name__ == "__main__":
    clean_build_artifacts()
    build_wheel()
    install_wheel()
    verify_install()
