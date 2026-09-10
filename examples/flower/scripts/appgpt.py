"""Plot a double-arm epitrochoid.

From the repository root, install dependencies and run with the same interpreter:
    .venv/bin/python -m pip install numpy matplotlib
    .venv/bin/python examples/flower/scripts/appgpt.py
"""

import os
import sys

# Use Matplotlib's bundled fonts on macOS: system_profiler can stall on startup.
if sys.platform == "darwin":
    os.environ.setdefault("MPL_IGNORE_SYSTEM_FONTS", "1")

import numpy as np
import matplotlib.pyplot as plt

R1 = 512
R2 = .333 * R1
petals = 3.03    # now interpreted as: oscillations of the offset arm per main revolution
vectors = 1.01   # now interpreted as: number of segments per oscillation (sampling density)
periods = 103     # number of full turns of the main arm

# Main arm:
#   We want the main arm to complete `periods` full turns.
#   We'll sample it at (vectors * petals) points per turn, to keep decent resolution.
steps_per_rev = int(vectors * petals)
total_steps = int(steps_per_rev * periods)

# Angular step sizes under the new interpretation:
# theta_main goes 0 → 2π * periods over total_steps
# theta_offset goes petals times faster than theta_main
dtheta_main = 2 * np.pi * periods / total_steps
dtheta_offset = petals * dtheta_main

theta_main = np.zeros(total_steps)
theta_offset = np.zeros(total_steps)
x = np.zeros(total_steps)
y = np.zeros(total_steps)

for i in range(total_steps):
    theta_main[i] = i * dtheta_main
    theta_offset[i] = i * dtheta_offset
    x[i] = R1 * np.cos(theta_main[i]) + R2 * np.cos(theta_offset[i])
    y[i] = R1 * np.sin(theta_main[i]) + R2 * np.sin(theta_offset[i])

# Center for plotting
x -= np.mean(x)
y -= np.mean(y)

plt.figure(figsize=(8, 8))
plt.plot(x, y, '-', lw=0.5)
plt.axis('equal')

# Dynamic title with the new semantics
plt.title(
    "Double-Arm Epitrochoid\n"
    f"R1={R1}, R2={R2/R1:.2f}×R1, petals={petals}, vectors={vectors}, periods={periods}"
)
plt.xlabel("X position (units)")
plt.ylabel("Y position (units)")

plt.show()
