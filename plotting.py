"""
Command-line interface for Kuramoto-Sivashinsky simulation.

Usage:
    python plotting.py [L] [--preset PRESET] [--save]
    
Examples:
    python plotting.py 32               # Run with L=32/(2*pi)
    python plotting.py --preset high_re  # Use high Reynolds preset
    python plotting.py 16 --save        # Run and save animation
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import cm
import argparse
import sys
from KS import KS
from config import Config
from simulator import KSSimulator


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description='Kuramoto-Sivashinsky Equation Simulator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        'L', 
        type=float, 
        nargs='?',
        default=None,
        help='Domain length parameter (domain will be [0, L])'
    )
    
    parser.add_argument(
        '--preset',
        choices=['low_re', 'medium_re', 'high_re'],
        default='medium_re',
        help='Use preset configuration (default: medium_re)'
    )
    
    parser.add_argument(
        '--N',
        type=int,
        default=None,
        help='Number of grid points (overrides preset)'
    )
    
    parser.add_argument(
        '--dt',
        type=float,
        default=None,
        help='Time step (overrides preset)'
    )
    
    parser.add_argument(
        '--diffusion',
        type=float,
        default=None,
        help='Diffusion coefficient (overrides preset)'
    )
    
    parser.add_argument(
        '--steps',
        type=int,
        default=1000,
        help='Number of simulation steps (default: 1000)'
    )
    
    parser.add_argument(
        '--transient',
        type=int,
        default=500,
        help='Number of transient steps (default: 500)'
    )
    
    parser.add_argument(
        '--save',
        action='store_true',
        help='Save animation to file'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default='KS_animation.mp4',
        help='Output filename for animation (default: KS_animation.mp4)'
    )
    
    parser.add_argument(
        '--save-data',
        action='store_true',
        help='Save simulation data'
    )
    
    parser.add_argument(
        '--data-output',
        type=str,
        default='KS_data.npz',
        help='Output filename for data (default: KS_data.npz)'
    )
    
    parser.add_argument(
        '--no-animation',
        action='store_true',
        help='Skip animation, only show final plots'
    )
    
    return parser.parse_args()


def create_animation(simulator, n_steps, save=False, output='KS_animation.mp4'):
    """
    Create animated visualization of KS simulation.
    
    Parameters:
    -----------
    simulator : KSSimulator
        Simulator instance
    n_steps : int
        Number of steps to simulate
    save : bool
        Whether to save animation
    output : str
        Output filename
    """
    model = simulator.model
    x = model.xx
    
    # Storage for data
    u_history = []
    t_history = []
    energy_history = []
    vspec = np.zeros(model.xspec.shape[0], np.float64)
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))
    line, = ax.plot(x, model.x, lw=3, color='blue')
    ax.set_xlim(0, 2*np.pi*model.L)
    ax.set_ylim(-5, 5)
    ax.set_xlabel('x', fontsize=12)
    ax.set_ylabel('u(x,t)', fontsize=12)
    ax.grid(True, alpha=0.3)
    
    def init():
        """Initialize animation."""
        line.set_ydata(np.ma.array(x, mask=True))
        return line,
    
    def update(n):
        """Update animation frame."""
        model.step()
        vspec[:] += np.abs(model.xspec)**2
        u = model.x
        
        line.set_ydata(u)
        ax.set_title(f'Kuramoto-Sivashinsky Solution - Time = {model.time:.2f}', fontsize=14)
        
        # Store data
        u_history.append(u.copy())
        t_history.append(model.time)
        energy_history.append(model.get_energy())
        
        if n % 50 == 0:
            print(f"Step {n}/{n_steps}, Time = {model.time:.2f}")
        
        return line,
    
    # Create animation
    ani = animation.FuncAnimation(
        fig, update, frames=n_steps, init_func=init,
        interval=25, blit=True, repeat=False
    )
    
    if save:
        print(f"Saving animation to {output}...")
        ani.save(output, fps=40, extra_args=['-vcodec', 'libx264'])
        print("Animation saved!")
    
    plt.show()
    
    return {
        'u': np.array(u_history),
        't': np.array(t_history),
        'energy': np.array(energy_history),
        'spectrum': vspec / n_steps,
        'x': x
    }


def plot_results(results, model):
    """
    Plot simulation results.
    
    Parameters:
    -----------
    results : dict
        Simulation results
    model : KS
        KS model instance
    """
    x = results['x']
    u = results['u']
    t = results['t']
    
    # Create figure with subplots
    fig = plt.figure(figsize=(14, 10))
    
    # Spacetime contour plot
    ax1 = fig.add_subplot(2, 2, 1)
    contour = ax1.contourf(x, t, u, 100, cmap=cm.magma)
    ax1.set_xlabel('x', fontsize=12)
    ax1.set_ylabel('t', fontsize=12)
    ax1.set_title('Spacetime Evolution', fontsize=14)
    plt.colorbar(contour, ax=ax1, label='u(x,t)')
    
    # Energy evolution
    ax2 = fig.add_subplot(2, 2, 2)
    ax2.plot(t, results['energy'], 'b-', linewidth=2)
    ax2.set_xlabel('Time', fontsize=12)
    ax2.set_ylabel('Energy', fontsize=12)
    ax2.set_title('Energy Evolution', fontsize=14)
    ax2.grid(True, alpha=0.3)
    
    # Power spectrum
    ax3 = fig.add_subplot(2, 2, 3)
    k = model.wavenums
    spec = results['spectrum']
    # Ensure matching lengths
    min_len = min(len(k), len(spec))
    k = k[:min_len]
    spec = spec[:min_len]
    spec_norm = spec / np.max(spec)
    ax3.semilogy(k, spec_norm, 'r-', linewidth=2)
    ax3.set_xlabel('Wavenumber k', fontsize=12)
    ax3.set_ylabel('Normalized Power', fontsize=12)
    ax3.set_title('Time-averaged Power Spectrum', fontsize=14)
    ax3.set_ylim([1e-4, 2])
    ax3.grid(True, alpha=0.3)
    
    # Final solution
    ax4 = fig.add_subplot(2, 2, 4)
    ax4.plot(x, u[-1], 'g-', linewidth=2)
    ax4.set_xlabel('x', fontsize=12)
    ax4.set_ylabel('u(x,t)', fontsize=12)
    ax4.set_title(f'Final Solution (t = {t[-1]:.2f})', fontsize=14)
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()


def main():
    """Main entry point."""
    args = parse_args()
    
    # Create configuration
    config = Config(preset=args.preset)
    
    # Override with command-line arguments
    if args.L is not None:
        # When L is specified, use it as domain length parameter
        # Set N equal to L for compatibility with original interface
        config.set('simulation', 'L', args.L / (2*np.pi))
        config.set('simulation', 'N', int(args.L))
    
    if args.N is not None:
        config.set('simulation', 'N', args.N)
    
    if args.dt is not None:
        config.set('simulation', 'dt', args.dt)
    
    if args.diffusion is not None:
        config.set('simulation', 'diffusion', args.diffusion)
    
    config.set('simulation', 'n_steps', args.steps)
    config.set('simulation', 'n_transient', args.transient)
    
    # Print configuration
    print("=" * 60)
    print("Kuramoto-Sivashinsky Equation Simulator")
    print("=" * 60)
    sim_params = config.get('simulation')
    print(f"Domain Length L: {sim_params['L']:.2f} (domain: [0, {2*np.pi*sim_params['L']:.2f}])")
    print(f"Grid Points N: {sim_params['N']}")
    print(f"Time Step dt: {sim_params['dt']}")
    print(f"Diffusion: {sim_params['diffusion']}")
    print(f"Transient Steps: {sim_params['n_transient']}")
    print(f"Simulation Steps: {sim_params['n_steps']}")
    print("=" * 60)
    
    # Create simulator
    simulator = KSSimulator(config)
    
    # Run transient
    print("\nRunning transient phase...")
    simulator.run_transient()
    print("Transient complete!")
    
    # Run simulation
    if args.no_animation:
        print("\nRunning simulation (no animation)...")
        results = simulator.run(record_every=1, record_spectrum=True)
        results['x'] = simulator.model.xx
        
        # Calculate average spectrum
        if len(results['spectrum']) > 0:
            results['spectrum'] = np.mean(results['spectrum'], axis=0)
        else:
            # Compute current spectrum if not recorded
            k, spec = simulator.model.get_spectrum()
            results['spectrum'] = spec
        
        print("Simulation complete!")
        
        # Save data if requested
        if args.save_data:
            print(f"\nSaving data to {args.data_output}...")
            simulator.save_results(args.data_output)
            print("Data saved!")
        
        # Plot results
        print("\nGenerating plots...")
        plot_results(results, simulator.model)
    else:
        print("\nStarting animated simulation...")
        results = create_animation(simulator, args.steps, args.save, args.output)
        
        # Save data if requested
        if args.save_data:
            print(f"\nSaving data to {args.data_output}...")
            data = {
                'x': results['x'],
                'u_history': results['u'],
                't_history': results['t'],
                'energy_history': results['energy'],
                'spectrum': results['spectrum'],
                'wavenumbers': simulator.model.wavenums[:-1],
                'L': simulator.model.L,
                'N': simulator.model.n,
                'dt': simulator.model.dt,
                'diffusion': simulator.model.diffusion
            }
            np.savez(args.data_output, **data)
            print("Data saved!")
        
        # Show summary plots
        print("\nGenerating summary plots...")
        plot_results(results, simulator.model)
    
    print("\nDone!")


if __name__ == '__main__':
    main()
