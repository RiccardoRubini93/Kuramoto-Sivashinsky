"""
Example 4: Creating and using custom configurations.

This example demonstrates advanced configuration management.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config
from simulator import KSSimulator
import matplotlib.pyplot as plt
import numpy as np

# Create a custom configuration
print("Creating custom configuration...")
custom_config = Config()

# Modify simulation parameters
custom_config.set('simulation', 'L', 24.0)
custom_config.set('simulation', 'N', 192)
custom_config.set('simulation', 'dt', 0.3)
custom_config.set('simulation', 'diffusion', 0.8)
custom_config.set('simulation', 'n_steps', 300)
custom_config.set('simulation', 'n_transient', 200)

# Save the configuration
custom_config.save('my_custom_config.json')
print("Configuration saved to my_custom_config.json")

# Load it back
loaded_config = Config.load('my_custom_config.json')
print("\nLoaded configuration:")
print(loaded_config)

# Run simulation with custom config
print("\nRunning simulation with custom configuration...")
simulator = KSSimulator(loaded_config)
simulator.run_transient()
results = simulator.run(record_every=3)

# Create comparison with preset
print("\nRunning simulation with medium_re preset...")
preset_config = Config(preset='medium_re')
preset_config.set('simulation', 'n_steps', 300)
preset_simulator = KSSimulator(preset_config)
preset_simulator.run_transient()
preset_results = preset_simulator.run(record_every=3)

# Compare results
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Custom config solution
state1 = simulator.get_current_state()
axes[0, 0].plot(state1['x'], state1['u'], 'b-', linewidth=2)
axes[0, 0].set_xlabel('x')
axes[0, 0].set_ylabel('u(x,t)')
axes[0, 0].set_title('Custom Config - Final Solution')
axes[0, 0].grid(True, alpha=0.3)

# Custom config energy
axes[0, 1].plot(results['t'], results['energy'], 'b-', linewidth=1.5)
axes[0, 1].set_xlabel('Time')
axes[0, 1].set_ylabel('Energy')
axes[0, 1].set_title('Custom Config - Energy Evolution')
axes[0, 1].grid(True, alpha=0.3)

# Preset solution
state2 = preset_simulator.get_current_state()
axes[1, 0].plot(state2['x'], state2['u'], 'r-', linewidth=2)
axes[1, 0].set_xlabel('x')
axes[1, 0].set_ylabel('u(x,t)')
axes[1, 0].set_title('Medium Re Preset - Final Solution')
axes[1, 0].grid(True, alpha=0.3)

# Preset energy
axes[1, 1].plot(preset_results['t'], preset_results['energy'], 'r-', linewidth=1.5)
axes[1, 1].set_xlabel('Time')
axes[1, 1].set_ylabel('Energy')
axes[1, 1].set_title('Medium Re Preset - Energy Evolution')
axes[1, 1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('example4_output.png', dpi=150)
print("\nOutput saved to example4_output.png")

# Print statistics
print("\n--- Statistics Comparison ---")
print(f"Custom Config:")
print(f"  Domain: [0, {2*np.pi*state1['x'][-1]:.2f}]")
print(f"  Mean Energy: {np.mean(results['energy']):.2f}")
print(f"  Energy Std: {np.std(results['energy']):.2f}")

print(f"\nPreset Config:")
print(f"  Domain: [0, {2*np.pi*state2['x'][-1]:.2f}]")
print(f"  Mean Energy: {np.mean(preset_results['energy']):.2f}")
print(f"  Energy Std: {np.std(preset_results['energy']):.2f}")

plt.show()
