#!/usr/bin/env python3
import os
import shutil
import subprocess
import sys

def clean_build_artifacts():
    """Remove build, dist, and any leftover .egg-info directories."""
    paths_to_remove = ["build", "dist", "agonutils.egg-info"]

    for path in paths_to_remove:
        if os.path.exists(path):
            print(f"Removing '{path}' directory...")
            shutil.rmtree(path)
        else:
            print(f"'{path}' directory not found, skipping...")

def uninstall_package(package_name="agonutils"):
    """Uninstall the package via pip (if installed)."""
    print(f"Uninstalling {package_name} (if installed)...")
    subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", package_name], check=False)

def rebuild_extension():
    """Compile the C extension in place without needing a reinstall."""
    print("Building C extension in place...")
    subprocess.run([sys.executable, "setup.py", "build_ext", "--inplace"], check=True)

def install_editable():
    """Install package in editable mode to allow automatic updates."""
    print("Installing package in editable mode...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-e", "."], check=True)

def verify_install():
    """Verify which .so file is actually being loaded."""
    print("Verifying import of agonutils...")

    code = (
        "import agonutils; "
        "print('agonutils loaded from:', agonutils.__file__); "
        "agonutils.hello()"
    )

    subprocess.run([sys.executable, "-c", code], check=True)

if __name__ == "__main__":
    clean_build_artifacts()
    rebuild_extension()  # Build the extension first
    install_editable()   # Install in dev mode (symlink)
    verify_install()
