"""
Example 1: Basic usage of the KS solver.

This example shows how to use the KS class directly to run a simulation.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from KS import KS
import matplotlib.pyplot as plt
import numpy as np

# Create a KS solver instance
print("Creating KS solver...")
ks = KS(L=16, N=128, dt=0.5, diffusion=1.0)

# Run transient phase
print("Running transient phase...")
for i in range(500):
    ks.step()

# Run simulation and collect data
print("Running simulation...")
n_steps = 200
u_history = []
t_history = []
energy_history = []

for i in range(n_steps):
    ks.step()
    if i % 5 == 0:  # Record every 5 steps
        u_history.append(ks.x.copy())
        t_history.append(ks.time)
        energy_history.append(ks.get_energy())

u_history = np.array(u_history)
t_history = np.array(t_history)
energy_history = np.array(energy_history)

print(f"Simulation complete! Final time: {ks.time:.2f}")

# Plot results
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

# Plot final solution
ax1.plot(ks.xx, ks.x, 'b-', linewidth=2)
ax1.set_xlabel('x')
ax1.set_ylabel('u(x,t)')
ax1.set_title(f'Solution at t = {ks.time:.2f}')
ax1.grid(True, alpha=0.3)

# Plot energy evolution
ax2.plot(t_history, energy_history, 'r-', linewidth=2)
ax2.set_xlabel('Time')
ax2.set_ylabel('Energy')
ax2.set_title('Energy Evolution')
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('example1_output.png', dpi=150)
print("Output saved to example1_output.png")
plt.show()
