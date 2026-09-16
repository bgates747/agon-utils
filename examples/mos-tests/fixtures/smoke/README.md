# Maintained smoke fixtures

Promoted without source changes from SETUP-01/W04 cpp and assembly fixtures.
The shared scripts/run_smoke.py observer is promoted from W06/run_image_comparison.py.
It now accepts a fresh evidence directory, stores images alongside evidence and
avoids touching historical hostfs autoexec files. Historical task evidence remains
unchanged. Output is the original W04 marker, return HL=123456, balanced stack
and preserved IX. This is bootstrap validation, not the new register-audit suite.
