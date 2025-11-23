import numpy as np
import pylab as pl


class KS(object):
    """
    Solution of 1-D Kuramoto-Sivashinsky equation.
    
    Solves: u_t + u*u_x + u_xx + diffusion*u_xxxx = 0
    with periodic BCs on [0, 2*pi*L] using Fourier spectral methods.
    """
    
    def __init__(self, L=16, N=128, dt=0.5, diffusion=1.0, initial_condition='default'):
        """
        Initialize the Kuramoto-Sivashinsky solver.
        
        Parameters:
        -----------
        L : float
            Domain length parameter (domain is [0, 2*pi*L])
        N : int
            Number of Fourier collocation points
        dt : float
            Time step size
        diffusion : float
            Diffusion coefficient
        initial_condition : str or array
            Initial condition type or custom array
        """
        # Validate inputs
        if N < 4 or not isinstance(N, (int, np.integer)):
            raise ValueError("N must be an integer >= 4")
        if L <= 0:
            raise ValueError("L must be positive")
        if dt <= 0:
            raise ValueError("dt must be positive")
        if diffusion <= 0:
            raise ValueError("diffusion must be positive")
        
        self.L = L 
        self.n = N 
        self.dt = dt
        self.diffusion = diffusion
        
        # Setup wavenumbers and spectral operators
        # Use rfftfreq to get all positive frequencies including Nyquist
        self.wavenums = N * np.fft.rfftfreq(N)
        k = self.wavenums.astype(np.float64) / L
        
        # Spectral derivative operator and linear term
        self.ik = 1j * k
        self.lin = k**2 - diffusion * k**4
        
        # Physical space grid
        self.xx = np.linspace(0, 2*np.pi*L, N, endpoint=False)
        
        # Initialize solution with specified initial condition
        if isinstance(initial_condition, str):
            if initial_condition == 'default':
                x = np.cos(4*np.pi*self.xx/(2*np.pi*L)) * (1.0 + np.sin(2*np.pi*self.xx/(2*np.pi*L)))
            elif initial_condition == 'random':
                np.random.seed(42)  # For reproducibility
                x = 0.1 * np.random.rand(N)
            elif initial_condition == 'sine':
                x = np.sin(4*np.pi*self.xx/(2*np.pi*L))
            elif initial_condition == 'zero':
                # Start with zero and add small Gaussian perturbation at center
                x = np.zeros(N)
                # Gaussian parameters (chosen to create a very small perturbation)
                center = np.pi * L  # Center of domain [0, 2*pi*L)
                amplitude = 0.01  # Very small amplitude
                width = L / 4  # Standard deviation of Gaussian
                # Add Gaussian perturbation
                x += amplitude * np.exp(-((self.xx - center)**2) / (2 * width**2))
            else:
                raise ValueError(f"Unknown initial condition: {initial_condition}")
        else:
            # Custom initial condition array
            if len(initial_condition) != N:
                raise ValueError(f"Initial condition must have length {N}")
            x = np.array(initial_condition)
        
        # Remove mean from initial condition
        self.x = x - x.mean()
        
        # Spectral space variable
        self.xspec = np.fft.rfft(self.x, axis=-1)
        
        # Statistics
        self.time = 0.0
        self.step_count = 0
    
    def nlterm(self, xspec):
        """
        Compute nonlinear term in spectral space.
        
        Parameters:
        -----------
        xspec : array
            Solution in spectral space
            
        Returns:
        --------
        array
            Nonlinear term -0.5 * d/dx(u^2) in spectral space
        """
        x = np.fft.irfft(xspec, axis=-1)
        return -0.5 * self.ik * np.fft.rfft(x**2, axis=-1)
    
    def step(self):
        """
        Advance solution by one time step using semi-implicit RK3.
        
        Uses a semi-implicit third-order Runge-Kutta method where
        the nonlinear term is treated explicitly and the linear
        term is treated implicitly with trapezoidal rule.
        """
        # Compute spectral representation
        self.xspec = np.fft.rfft(self.x, axis=-1)
        
        xspec_save = self.xspec.copy()
        
        # Third-order Runge-Kutta stages
        for n in range(3):
            dt = self.dt / (3 - n)
            
            # Explicit RK3 step for nonlinear term
            self.xspec = xspec_save + dt * self.nlterm(self.xspec)
            
            # Implicit trapezoidal adjustment for linear term
            self.xspec = (self.xspec + 0.5 * self.lin * dt * xspec_save) / (1.0 - 0.5 * self.lin * dt)
        
        # Transform back to physical space
        self.x = np.fft.irfft(self.xspec, axis=-1)
        
        # Update time and step count
        self.time += self.dt
        self.step_count += 1
    
    def get_energy(self):
        """
        Compute the total energy of the system.
        
        Returns:
        --------
        float
            Total energy (L2 norm squared)
        """
        return np.sum(self.x**2) * (2*np.pi*self.L) / self.n
    
    def get_spectrum(self):
        """
        Get the power spectrum of the current solution.
        
        Returns:
        --------
        tuple
            (wavenumbers, power_spectrum)
        """
        spec = np.abs(self.xspec)**2
        return self.wavenums, spec
    
    def plot_spectrum(self, u):
        """
        Plot the power spectrum of the solution.
        
        Parameters:
        -----------
        u : array
            Solution in physical space
        """
        # Use rfft to match the wavenumber array
        sp = np.abs(np.fft.rfft(u))
        k = self.wavenums
        
        pl.figure(1)
        pl.semilogy(k, sp/max(sp), "r--", lw=3)
        pl.xlabel("k", fontsize=12)
        pl.ylim([1e-4, 1.2])
        pl.show()
    
    def save_state(self, filename):
        """
        Save the current state to a file.
        
        Parameters:
        -----------
        filename : str
            Output filename
        """
        state = {
            'x': self.x,
            'xspec': self.xspec,
            'time': self.time,
            'step_count': self.step_count,
            'L': self.L,
            'N': self.n,
            'dt': self.dt,
            'diffusion': self.diffusion
        }
        np.savez(filename, **state)
    
    def load_state(self, filename):
        """
        Load a saved state from a file.
        
        Parameters:
        -----------
        filename : str
            Input filename
        """
        state = np.load(filename)
        self.x = state['x']
        self.xspec = state['xspec']
        self.time = float(state['time'])
        self.step_count = int(state['step_count'])
		

		











