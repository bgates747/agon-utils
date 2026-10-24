#!/usr/bin/env python3
"""Agent-side numerical verification after the Author closes the review."""
from pathlib import Path
import subprocess

HERE=Path(__file__).resolve().parent
PROFILE=HERE.parents[2]/'.emulator'
subprocess.run(['sha256sum','--check','--status','.runtime.sha256'],cwd=PROFILE,check=True)
actual=(PROFILE/'sdcard/agnb/results.dat').read_bytes()
expected=(HERE/'build/expected.dat').read_bytes()
assert actual==expected,(actual.hex(),expected.hex())
print(f'AGNB review output matches all {len(expected)} result bytes.')
