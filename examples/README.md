# Examples Directory

This directory contains example scripts demonstrating how to use the Kuramoto-Sivashinsky simulator.

## Examples

### Example 1: Basic Usage (`example1_basic_usage.py`)
Demonstrates direct usage of the KS class:
- Creating a solver instance
- Running transient and simulation phases
- Collecting and plotting data

**Run:**
```bash
python examples/example1_basic_usage.py
```

### Example 2: High-Level Simulator (`example2_simulator.py`)
Shows how to use the simulator with configuration presets:
- Using preset configurations
- Running simulations with the high-level API
- Creating comprehensive visualizations
- Saving simulation data

**Run:**
```bash
python examples/example2_simulator.py
```

### Example 3: Initial Conditions Comparison (`example3_initial_conditions.py`)
Compares different initial conditions:
- Default (cosine-based)
- Random noise
- Sine wave
Shows how initial conditions affect the dynamics.

**Run:**
```bash
python examples/example3_initial_conditions.py
```

### Example 4: Custom Configuration (`example4_custom_config.py`)
Demonstrates creating and using custom configurations:
- Building custom configuration objects
- Saving/loading configurations
- Parameter exploration

**Run:**
```bash
python examples/example4_custom_config.py
```

## Requirements

All examples require:
- numpy
- matplotlib

Install with:
```bash
pip install -r ../requirements.txt
```

## Output

Each example saves its output as PNG images:
- `example1_output.png`
- `example2_output.png`
- `example3_output.png`
- `example4_output.png`

Some examples also save data files (`.npz` format).
