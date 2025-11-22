"""
Example 3: Comparing different initial conditions.

This example shows how to compare different initial conditions.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from KS import KS
import matplotlib.pyplot as plt
import numpy as np

# Initial conditions to compare
initial_conditions = ['default', 'random', 'sine']
colors = ['blue', 'red', 'green']

fig, axes = plt.subplots(3, 2, figsize=(14, 12))

for idx, (ic, color) in enumerate(zip(initial_conditions, colors)):
    print(f"\nSimulating with '{ic}' initial condition...")
    
    # Create solver
    ks = KS(L=16, N=128, dt=0.5, diffusion=1.0, initial_condition=ic)
    
    # Plot initial condition
    axes[idx, 0].plot(ks.xx, ks.x, color=color, linewidth=2)
    axes[idx, 0].set_xlabel('x')
    axes[idx, 0].set_ylabel('u(x,0)')
    axes[idx, 0].set_title(f'Initial Condition: {ic}')
    axes[idx, 0].grid(True, alpha=0.3)
    axes[idx, 0].set_ylim([-3, 3])
    
    # Run transient
    for i in range(500):
        ks.step()
    
    # Run simulation
    energy_history = []
    for i in range(200):
        ks.step()
        energy_history.append(ks.get_energy())
    
    # Plot final state and energy
    axes[idx, 1].plot(range(len(energy_history)), energy_history, 
                      color=color, linewidth=1.5)
    axes[idx, 1].set_xlabel('Step')
    axes[idx, 1].set_ylabel('Energy')
    axes[idx, 1].set_title(f'Energy Evolution: {ic}')
    axes[idx, 1].grid(True, alpha=0.3)
    
    print(f"  Final energy: {energy_history[-1]:.2f}")
    print(f"  Mean energy: {np.mean(energy_history):.2f}")
    print(f"  Energy std: {np.std(energy_history):.2f}")

plt.tight_layout()
plt.savefig('example3_output.png', dpi=150)
print("\nOutput saved to example3_output.png")
plt.show()
