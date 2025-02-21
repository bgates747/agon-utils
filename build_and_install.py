#!/usr/bin/env python3
import os
import shutil
import subprocess
import sys
import glob
import site

def clean_build_artifacts():
    """Remove build, dist, agonutils.egg-info, and any leftover sdist directories."""
    paths_to_remove = ["build", "dist", "agonutils.egg-info"]

    for path in paths_to_remove:
        if os.path.exists(path):
            print(f"Removing '{path}' directory...")
            shutil.rmtree(path)
        else:
            print(f"'{path}' directory not found, skipping...")

    # Remove any agonutils-* directories (e.g., agonutils-1.0) left by `sdist`
    for leftover in glob.glob("agonutils-*"):
        if os.path.isdir(leftover):
            print(f"Removing leftover sdist directory '{leftover}'...")
            shutil.rmtree(leftover)

    # Final check to ensure it's gone
    if os.path.exists("agonutils-1.0"):
        print("ERROR: agonutils-1.0 still exists after cleanup. Manually removing...")
        shutil.rmtree("agonutils-1.0", ignore_errors=True)

def uninstall_package(package_name="agonutils"):
    """Uninstall the package via pip (if installed)."""
    print(f"Uninstalling {package_name}...")
    subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", package_name],
                   check=False)  # check=False so script doesn't stop if not installed

def remove_leftover_files(package_name="agonutils"):
    """
    Search the current .venv (or sys.path) for leftover .so or .egg files
    matching the package name, and remove them.
    """
    venv_site = site.getsitepackages() if hasattr(site, 'getsitepackages') else []
    if hasattr(site, 'getusersitepackages'):
        venv_site.append(site.getusersitepackages())
    # It's possible site-packages can return multiple paths (e.g. for dist-packages).

    for spath in venv_site:
        if not os.path.isdir(spath):
            continue
        # Walk the site-packages and remove any suspicious .so or .egg files
        for root, dirs, files in os.walk(spath):
            for fname in files:
                # e.g. agonutils.cpython-312-x86_64-linux-gnu.so or agonutils-1.0.egg
                lower = fname.lower()
                if package_name in lower and (lower.endswith(".so") or lower.endswith(".egg")):
                    fullpath = os.path.join(root, fname)
                    print(f"Removing leftover file: {fullpath}")
                    try:
                        os.remove(fullpath)
                    except OSError as e:
                        print(f"Warning: Could not remove {fullpath}: {e}")

def build_and_install():
    """Build a fresh wheel with python -m build, then install it."""
    print("Building wheel with python -m build...")
    subprocess.run([sys.executable, "-m", "build"], check=True)

    wheel_files = glob.glob("dist/*.whl")
    if not wheel_files:
        print("No wheel files found in 'dist/'")
        sys.exit(1)
    wheel_file = wheel_files[0]

    print(f"Installing {wheel_file}...")
    subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", wheel_file], check=True)
    print("Install successful!")

def verify_install():
    """Verify which .so file is actually being loaded."""
    print("Verifying import of agonutils...")
    code = (
        "import agonutils; "
        "print('agonutils loaded from:', agonutils.__file__)"
    )
    subprocess.run([sys.executable, "-c", code], check=True)

if __name__ == "__main__":
    clean_build_artifacts()
    uninstall_package("agonutils")
    remove_leftover_files("agonutils")
    build_and_install()
    verify_install()