#!/usr/bin/env python3
import subprocess
import sys

AGONUTILS_SRC = "/Users/bgates/Agon/mystuff/agon-utils"

def dev_install():
    print(f"Installing {AGONUTILS_SRC} in dev mode...")
    subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", "agonutils"], check=False)
    subprocess.run([sys.executable, "-m", "pip", "install", "-e", AGONUTILS_SRC], check=True)
    print("agonutils dev-installed successfully.")

if __name__ == "__main__":
    dev_install()
