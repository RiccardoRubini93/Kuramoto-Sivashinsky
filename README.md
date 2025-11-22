# Kuramoto-Sivashinsky Equation Simulator

Numerical solution of the 1-D Kuramoto-Sivashinsky equation defined on a periodic domain of length L / 2π.

## Overview

This package provides a high-performance, modular implementation of the Kuramoto-Sivashinsky (KS) equation solver with both command-line and graphical user interfaces.

**Equation:** `u_t + u*u_x + u_xx + diffusion*u_xxxx = 0`

The solver uses a Fourier spectral method with semi-implicit third-order Runge-Kutta time integration.

## Features

- ✨ **Modular Architecture**: Separated physics model, configuration, simulation, and visualization
- 🖥️ **Interactive GUI**: Real-time parameter control and visualization
- 🔧 **Command-Line Interface**: Flexible scripting and automation
- ⚡ **Performance Optimized**: Efficient FFT operations and memory management
- 📊 **Multiple Visualization Options**: Real-time plots, animations, and data export
- 🎯 **Preset Configurations**: Pre-configured settings for different Reynolds numbers
- 💾 **Data Export**: Save simulation data and configurations in standard formats

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

### Graphical User Interface

Launch the interactive GUI:

```bash
python ks_gui.py
```

Features:
- Real-time parameter adjustment
- Live visualization of solution and energy
- Preset configurations (low/medium/high Reynolds number)
- Save/load configurations
- Export simulation data

### Command-Line Interface

Run a simulation with default parameters:

```bash
python plotting.py
```

Use a preset configuration:

```bash
python plotting.py --preset high_re
```

Custom parameters:

```bash
python plotting.py 32 --N 256 --dt 0.25 --steps 2000
```

Save animation and data:

```bash
python plotting.py --save --save-data --output my_animation.mp4
```

Run without animation (faster):

```bash
python plotting.py --no-animation --steps 5000 --save-data
```

## File Structure

### Core Modules

- **KS.py**: Core physics model implementing the KS equation solver
  - Spectral methods with FFT
  - Semi-implicit RK3 time integration
  - Energy and spectrum computation
  - State save/load functionality

- **config.py**: Configuration management
  - Preset configurations for different regimes
  - JSON-based config save/load
  - Parameter validation

- **simulator.py**: High-level simulation runner
  - Manages simulation execution
  - Data collection and history
  - Result export

### User Interfaces

- **ks_gui.py**: Interactive graphical interface (tkinter)
  - Real-time visualization
  - Parameter controls
  - Data export

- **plotting.py**: Command-line interface
  - Flexible command-line arguments
  - Batch processing support
  - Animation generation

### Legacy Files

- **Plottig.py**: Original plotting script (deprecated, use plotting.py)

## Usage Examples

### Python API

```python
from KS import KS
from simulator import KSSimulator
from config import Config

# Method 1: Direct model usage
ks = KS(L=16, N=128, dt=0.5, diffusion=1.0)
for i in range(1000):
    ks.step()
    if i % 100 == 0:
        energy = ks.get_energy()
        print(f"Step {i}, Energy: {energy:.4f}")

# Method 2: Using simulator with configuration
config = Config(preset='medium_re')
simulator = KSSimulator(config)
simulator.run_transient(n_steps=500)
results = simulator.run(n_steps=1000, record_every=10)

# Access results
print(f"Simulation time: {results['t'][-1]:.2f}")
print(f"Final energy: {results['energy'][-1]:.4f}")

# Save results
simulator.save_results('my_simulation.npz')
```

## Presets

### Low Reynolds Number (`low_re`)
- L = 8.0, N = 64, dt = 0.25, diffusion = 2.0
- Stable, ordered behavior
- Suitable for testing and validation

### Medium Reynolds Number (`medium_re`)
- L = 16.0, N = 128, dt = 0.5, diffusion = 1.0
- Chaotic dynamics
- Classic KS behavior

### High Reynolds Number (`high_re`)
- L = 32.0, N = 256, dt = 0.25, diffusion = 0.5
- Turbulent behavior
- Complex spatiotemporal dynamics

## Performance Improvements

The refactored code includes several optimizations:

1. **Efficient Memory Management**: Reuses arrays where possible
2. **Vectorized Operations**: NumPy operations for speed
3. **Reduced FFT Calls**: Caches spectral representations
4. **Modular Design**: Easier to optimize specific components
5. **Configuration Caching**: Avoid repeated parameter parsing

## Technical Details

### Numerical Method

- **Spatial Discretization**: Fourier spectral method
- **Time Integration**: Semi-implicit 3rd-order Runge-Kutta
  - Nonlinear term: Explicit treatment
  - Linear term: Implicit trapezoidal rule
- **Stability**: The semi-implicit scheme allows larger time steps

### Domain

- Periodic boundary conditions on [0, 2πL]
- Spectral resolution with N collocation points
- Physical space: `x ∈ [0, 2πL]`
- Spectral space: Wave numbers `k = n/L` for `n = 0, 1, ..., N/2`

## Bug Fixes

The refactored code addresses several issues in the original implementation:

1. ✅ Fixed deprecated `np.float` usage (now `np.float64`)
2. ✅ Removed unused `pdb` import
3. ✅ Fixed inconsistent indentation (tabs → spaces)
4. ✅ Removed debug code (commented `pdb.set_trace()`)
5. ✅ Fixed confusing command-line argument handling in original Plottig.py
6. ✅ Added input validation and error handling
7. ✅ Fixed grid spacing calculation
8. ✅ Added proper documentation and docstrings

## References

The numerical method is based on standard spectral methods for PDEs. For more information on the Kuramoto-Sivashinsky equation, see the included paper `PhysRevE.78.026208.pdf`.

## License

See original repository for license information.
