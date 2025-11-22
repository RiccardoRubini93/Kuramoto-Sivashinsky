"""
Example 2: Using the simulator with configuration presets.

This example demonstrates the high-level simulator interface with presets.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simulator import KSSimulator
from config import Config
import matplotlib.pyplot as plt
import numpy as np

# Use a preset configuration
print("Using 'high_re' preset configuration...")
config = Config(preset='high_re')

# Create simulator
simulator = KSSimulator(config)

# Run transient
print("Running transient phase...")
simulator.run_transient()

# Run simulation
print("Running simulation...")
results = simulator.run(n_steps=500, record_every=2)

print(f"Simulation complete!")
print(f"  Final time: {results['t'][-1]:.2f}")
print(f"  Final energy: {results['energy'][-1]:.2f}")
print(f"  Recorded {len(results['t'])} timesteps")

# Create visualization
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))

# Current solution
state = simulator.get_current_state()
ax1.plot(state['x'], state['u'], 'b-', linewidth=2)
ax1.set_xlabel('x')
ax1.set_ylabel('u(x,t)')
ax1.set_title(f'Solution at t = {state["t"]:.2f}')
ax1.grid(True, alpha=0.3)

# Energy evolution
ax2.plot(results['t'], results['energy'], 'r-', linewidth=1.5)
ax2.set_xlabel('Time')
ax2.set_ylabel('Energy')
ax2.set_title('Energy Evolution')
ax2.grid(True, alpha=0.3)

# Spacetime contour
contour = ax3.contourf(state['x'], results['t'], results['u'], 50, cmap='viridis')
ax3.set_xlabel('x')
ax3.set_ylabel('t')
ax3.set_title('Spacetime Evolution')
plt.colorbar(contour, ax=ax3)

# Energy statistics
ax4.hist(results['energy'], bins=30, edgecolor='black', alpha=0.7)
ax4.set_xlabel('Energy')
ax4.set_ylabel('Frequency')
ax4.set_title('Energy Distribution')
ax4.axvline(np.mean(results['energy']), color='r', linestyle='--', 
            linewidth=2, label=f'Mean: {np.mean(results["energy"]):.2f}')
ax4.legend()
ax4.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('example2_output.png', dpi=150)
print("Output saved to example2_output.png")

# Save results
simulator.save_results('example2_data.npz')
print("Data saved to example2_data.npz")

plt.show()
