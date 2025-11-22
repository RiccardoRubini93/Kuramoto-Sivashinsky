"""
Simulation runner for Kuramoto-Sivashinsky equation.
"""

import numpy as np
from KS import KS
from config import Config


class KSSimulator:
    """
    High-level simulator for Kuramoto-Sivashinsky equation.
    
    Handles simulation execution, data collection, and result management.
    """
    
    def __init__(self, config=None):
        """
        Initialize simulator.
        
        Parameters:
        -----------
        config : Config or dict, optional
            Configuration object or dictionary
        """
        if config is None:
            self.config = Config()
        elif isinstance(config, dict):
            self.config = Config(config_dict=config)
        elif isinstance(config, Config):
            self.config = config
        else:
            raise TypeError("config must be Config object or dict")
        
        # Get simulation parameters
        sim_params = self.config.get('simulation')
        
        # Initialize KS model
        self.model = KS(
            L=sim_params['L'],
            N=sim_params['N'],
            dt=sim_params['dt'],
            diffusion=sim_params['diffusion'],
            initial_condition=sim_params['initial_condition']
        )
        
        # Data storage
        self.history = {
            'u': [],
            't': [],
            'energy': [],
            'spectrum': []
        }
        
        self.n_steps = sim_params['n_steps']
        self.n_transient = sim_params['n_transient']
    
    def run_transient(self, n_steps=None):
        """
        Run transient phase to reach attractor.
        
        Parameters:
        -----------
        n_steps : int, optional
            Number of transient steps (uses config default if None)
        """
        if n_steps is None:
            n_steps = self.n_transient
        
        for _ in range(n_steps):
            self.model.step()
    
    def run(self, n_steps=None, record_every=1, record_spectrum=False):
        """
        Run simulation and collect data.
        
        Parameters:
        -----------
        n_steps : int, optional
            Number of steps (uses config default if None)
        record_every : int
            Record data every N steps
        record_spectrum : bool
            Whether to record power spectrum
            
        Returns:
        --------
        dict
            Simulation results
        """
        if n_steps is None:
            n_steps = self.n_steps
        
        # Clear history
        self.history = {
            'u': [],
            't': [],
            'energy': [],
            'spectrum': []
        }
        
        # Run simulation
        for step in range(n_steps):
            self.model.step()
            
            if step % record_every == 0:
                self.history['u'].append(self.model.x.copy())
                self.history['t'].append(self.model.time)
                self.history['energy'].append(self.model.get_energy())
                
                if record_spectrum:
                    k, spec = self.model.get_spectrum()
                    self.history['spectrum'].append(spec.copy())
        
        # Convert lists to arrays
        self.history['u'] = np.array(self.history['u'])
        self.history['t'] = np.array(self.history['t'])
        self.history['energy'] = np.array(self.history['energy'])
        if record_spectrum:
            self.history['spectrum'] = np.array(self.history['spectrum'])
        
        return self.history
    
    def get_current_state(self):
        """
        Get current state of the simulation.
        
        Returns:
        --------
        dict
            Current state information
        """
        return {
            'x': self.model.xx,
            'u': self.model.x,
            't': self.model.time,
            'step': self.model.step_count,
            'energy': self.model.get_energy()
        }
    
    def save_results(self, filename):
        """
        Save simulation results to file.
        
        Parameters:
        -----------
        filename : str
            Output filename
        """
        # Prepare data
        data = {
            'x': self.model.xx,
            'u_history': self.history['u'],
            't_history': self.history['t'],
            'energy_history': self.history['energy'],
            'L': self.model.L,
            'N': self.model.n,
            'dt': self.model.dt,
            'diffusion': self.model.diffusion
        }
        
        if len(self.history['spectrum']) > 0:
            data['spectrum_history'] = self.history['spectrum']
            k, _ = self.model.get_spectrum()
            data['wavenumbers'] = k
        
        np.savez(filename, **data)
    
    @staticmethod
    def load_results(filename):
        """
        Load simulation results from file.
        
        Parameters:
        -----------
        filename : str
            Input filename
            
        Returns:
        --------
        dict
            Loaded simulation results
        """
        data = np.load(filename)
        return {key: data[key] for key in data.keys()}
    
    def reset(self):
        """Reset the simulation to initial conditions."""
        sim_params = self.config.get('simulation')
        self.model = KS(
            L=sim_params['L'],
            N=sim_params['N'],
            dt=sim_params['dt'],
            diffusion=sim_params['diffusion'],
            initial_condition=sim_params['initial_condition']
        )
        self.history = {
            'u': [],
            't': [],
            'energy': [],
            'spectrum': []
        }
