#!/usr/bin/env python3
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import linregress
import matplotlib
matplotlib.use('TkAgg')

# Data: (Original, Compressed)
# data = np.array([
#     [14.2, 5.2],
#     [24.7, 7.7],
#     [136.8, 39.9],
#     [238.8, 78.8]
# ])

data = np.array([
    [307200, 24690],
    [196608, 18286],
    [76800, 9976],
    [43200, 6826]
])

x = data[:, 0]
y = data[:, 1]

# Take logarithms
logx = np.log(x)
logy = np.log(y)

# Linear regression on log-log values
slope, intercept, r_value, p_value, std_err = linregress(logx, logy)

# Construct power law model: y = a * x^b
a = np.exp(intercept)
b = slope

# Generate fitted curve for plotting
x_fit = np.linspace(min(x), max(x), 100)
y_fit = a * x_fit**b

plt.figure(figsize=(8, 6))
plt.loglog(x, y, 'o', label='Data points')
plt.loglog(x_fit, y_fit, '-', label=f'Fit: y = {a:.3f} x^{b:.3f}\n$R^2$ = {r_value**2:.3f}')
plt.xlabel('Original size')
plt.ylabel('Compressed size')
plt.title('Log–Log Plot with Power Law Fit')
plt.legend()
plt.grid(True, which="both", ls="--")
plt.show()
