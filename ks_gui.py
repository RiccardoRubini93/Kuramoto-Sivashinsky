"""
Interactive GUI for Kuramoto-Sivashinsky equation simulator.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib.animation as animation
from KS import KS
from config import Config
from simulator import KSSimulator
import threading


class KSGUI:
    """Interactive GUI for KS equation simulation."""
    
    def __init__(self, root):
        """
        Initialize the GUI.
        
        Parameters:
        -----------
        root : tk.Tk
            Root window
        """
        self.root = root
        self.root.title("Kuramoto-Sivashinsky Equation Simulator")
        self.root.geometry("1200x800")
        
        # Configuration
        self.config = Config()
        self.simulator = None
        self.is_running = False
        self.animation_obj = None
        
        # Setup GUI
        self._create_widgets()
        self._setup_layout()
        
        # Initialize with default preset
        self.load_preset('medium_re')
    
    def _create_widgets(self):
        """Create all GUI widgets."""
        # Control Panel (Left)
        self.control_frame = ttk.LabelFrame(self.root, text="Control Panel", padding=10)
        
        # Preset Selection
        preset_frame = ttk.Frame(self.control_frame)
        ttk.Label(preset_frame, text="Preset:").grid(row=0, column=0, sticky='w', pady=5)
        self.preset_var = tk.StringVar(value='medium_re')
        preset_combo = ttk.Combobox(preset_frame, textvariable=self.preset_var, 
                                     values=['low_re', 'medium_re', 'high_re'], 
                                     state='readonly', width=15)
        preset_combo.grid(row=0, column=1, sticky='ew', pady=5, padx=5)
        preset_combo.bind('<<ComboboxSelected>>', lambda e: self.load_preset(self.preset_var.get()))
        preset_frame.grid(row=0, column=0, columnspan=2, sticky='ew', pady=5)
        
        # Parameters
        params_frame = ttk.LabelFrame(self.control_frame, text="Parameters", padding=5)
        params_frame.grid(row=1, column=0, columnspan=2, sticky='ew', pady=10)
        
        # Domain length L
        ttk.Label(params_frame, text="Domain Length (L):").grid(row=0, column=0, sticky='w', pady=3)
        self.L_var = tk.StringVar(value="16.0")
        ttk.Entry(params_frame, textvariable=self.L_var, width=10).grid(row=0, column=1, pady=3, padx=5)
        
        # Grid points N
        ttk.Label(params_frame, text="Grid Points (N):").grid(row=1, column=0, sticky='w', pady=3)
        self.N_var = tk.StringVar(value="128")
        ttk.Entry(params_frame, textvariable=self.N_var, width=10).grid(row=1, column=1, pady=3, padx=5)
        
        # Time step dt
        ttk.Label(params_frame, text="Time Step (dt):").grid(row=2, column=0, sticky='w', pady=3)
        self.dt_var = tk.StringVar(value="0.5")
        ttk.Entry(params_frame, textvariable=self.dt_var, width=10).grid(row=2, column=1, pady=3, padx=5)
        
        # Diffusion
        ttk.Label(params_frame, text="Diffusion:").grid(row=3, column=0, sticky='w', pady=3)
        self.diff_var = tk.StringVar(value="1.0")
        ttk.Entry(params_frame, textvariable=self.diff_var, width=10).grid(row=3, column=1, pady=3, padx=5)
        
        # Initial condition
        ttk.Label(params_frame, text="Initial Condition:").grid(row=4, column=0, sticky='w', pady=3)
        self.ic_var = tk.StringVar(value='default')
        ic_combo = ttk.Combobox(params_frame, textvariable=self.ic_var, 
                                values=['default', 'random', 'sine'], 
                                state='readonly', width=8)
        ic_combo.grid(row=4, column=1, pady=3, padx=5)
        
        # Simulation Settings
        sim_frame = ttk.LabelFrame(self.control_frame, text="Simulation", padding=5)
        sim_frame.grid(row=2, column=0, columnspan=2, sticky='ew', pady=10)
        
        ttk.Label(sim_frame, text="Transient Steps:").grid(row=0, column=0, sticky='w', pady=3)
        self.trans_var = tk.StringVar(value="500")
        ttk.Entry(sim_frame, textvariable=self.trans_var, width=10).grid(row=0, column=1, pady=3, padx=5)
        
        ttk.Label(sim_frame, text="Run Steps:").grid(row=1, column=0, sticky='w', pady=3)
        self.steps_var = tk.StringVar(value="1000")
        ttk.Entry(sim_frame, textvariable=self.steps_var, width=10).grid(row=1, column=1, pady=3, padx=5)
        
        # Control Buttons
        btn_frame = ttk.Frame(self.control_frame)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=15)
        
        self.start_btn = ttk.Button(btn_frame, text="Start", command=self.start_simulation)
        self.start_btn.grid(row=0, column=0, padx=5, pady=5)
        
        self.stop_btn = ttk.Button(btn_frame, text="Stop", command=self.stop_simulation, state='disabled')
        self.stop_btn.grid(row=0, column=1, padx=5, pady=5)
        
        self.reset_btn = ttk.Button(btn_frame, text="Reset", command=self.reset_simulation)
        self.reset_btn.grid(row=0, column=2, padx=5, pady=5)
        
        # Save/Export
        export_frame = ttk.LabelFrame(self.control_frame, text="Export", padding=5)
        export_frame.grid(row=4, column=0, columnspan=2, sticky='ew', pady=10)
        
        ttk.Button(export_frame, text="Save Data", command=self.save_data).pack(fill='x', pady=3)
        ttk.Button(export_frame, text="Save Config", command=self.save_config).pack(fill='x', pady=3)
        ttk.Button(export_frame, text="Load Config", command=self.load_config).pack(fill='x', pady=3)
        
        # Info Panel
        info_frame = ttk.LabelFrame(self.control_frame, text="Info", padding=5)
        info_frame.grid(row=5, column=0, columnspan=2, sticky='ew', pady=10)
        
        self.info_text = tk.Text(info_frame, height=8, width=30, state='disabled')
        self.info_text.pack(fill='both', expand=True)
        
        # Visualization Panel (Right)
        self.plot_frame = ttk.Frame(self.root)
        
        # Create matplotlib figure
        self.fig = Figure(figsize=(10, 8), dpi=100)
        
        # Main solution plot
        self.ax1 = self.fig.add_subplot(2, 1, 1)
        self.ax1.set_xlabel('x')
        self.ax1.set_ylabel('u(x,t)')
        self.ax1.set_title('Kuramoto-Sivashinsky Solution')
        self.ax1.grid(True, alpha=0.3)
        
        # Energy/Spectrum plot
        self.ax2 = self.fig.add_subplot(2, 1, 2)
        self.ax2.set_xlabel('Time')
        self.ax2.set_ylabel('Energy')
        self.ax2.set_title('System Energy')
        self.ax2.grid(True, alpha=0.3)
        
        self.fig.tight_layout()
        
        # Embed matplotlib in tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Add toolbar
        toolbar = NavigationToolbar2Tk(self.canvas, self.plot_frame)
        toolbar.update()
    
    def _setup_layout(self):
        """Setup the layout of widgets."""
        self.control_frame.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
        self.plot_frame.grid(row=0, column=1, sticky='nsew', padx=10, pady=10)
        
        # Configure grid weights
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=0)
        self.root.grid_columnconfigure(1, weight=1)
    
    def load_preset(self, preset_name):
        """Load a preset configuration."""
        preset = Config.PRESETS.get(preset_name)
        if preset:
            self.L_var.set(str(preset['L']))
            self.N_var.set(str(preset['N']))
            self.dt_var.set(str(preset['dt']))
            self.diff_var.set(str(preset['diffusion']))
            self.update_info(f"Loaded preset: {preset_name}\n{preset.get('description', '')}")
    
    def get_current_config(self):
        """Get current configuration from GUI."""
        try:
            config = Config()
            config.set('simulation', 'L', float(self.L_var.get()))
            config.set('simulation', 'N', int(self.N_var.get()))
            config.set('simulation', 'dt', float(self.dt_var.get()))
            config.set('simulation', 'diffusion', float(self.diff_var.get()))
            config.set('simulation', 'initial_condition', self.ic_var.get())
            config.set('simulation', 'n_transient', int(self.trans_var.get()))
            config.set('simulation', 'n_steps', int(self.steps_var.get()))
            return config
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid parameter: {e}")
            return None
    
    def start_simulation(self):
        """Start the simulation."""
        if self.is_running:
            return
        
        config = self.get_current_config()
        if config is None:
            return
        
        try:
            # Create simulator
            self.simulator = KSSimulator(config)
            
            # Run transient
            self.update_info("Running transient phase...")
            self.root.update()
            self.simulator.run_transient()
            
            # Start animation
            self.is_running = True
            self.start_btn.config(state='disabled')
            self.stop_btn.config(state='normal')
            
            self.energy_history = []
            self.time_history = []
            
            self.update_info("Simulation running...")
            
            # Start animation
            self.animation_obj = animation.FuncAnimation(
                self.fig, self.update_plot, interval=50, 
                blit=False, repeat=True, cache_frame_data=False
            )
            self.canvas.draw()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start simulation: {e}")
            self.is_running = False
            self.start_btn.config(state='normal')
            self.stop_btn.config(state='disabled')
    
    def update_plot(self, frame):
        """Update the plot for animation."""
        if not self.is_running:
            return
        
        # Step the simulation
        self.simulator.model.step()
        
        # Get current state
        state = self.simulator.get_current_state()
        
        # Update energy history
        self.energy_history.append(state['energy'])
        self.time_history.append(state['t'])
        
        # Keep only last 500 points for energy plot
        if len(self.energy_history) > 500:
            self.energy_history.pop(0)
            self.time_history.pop(0)
        
        # Update solution plot
        self.ax1.clear()
        self.ax1.plot(state['x'], state['u'], 'b-', linewidth=2)
        self.ax1.set_xlabel('x')
        self.ax1.set_ylabel('u(x,t)')
        self.ax1.set_title(f'Solution at t = {state["t"]:.2f}')
        self.ax1.grid(True, alpha=0.3)
        self.ax1.set_ylim([-5, 5])
        
        # Update energy plot
        self.ax2.clear()
        self.ax2.plot(self.time_history, self.energy_history, 'r-', linewidth=1.5)
        self.ax2.set_xlabel('Time')
        self.ax2.set_ylabel('Energy')
        self.ax2.set_title('System Energy')
        self.ax2.grid(True, alpha=0.3)
        
        # Update info
        info_str = f"Time: {state['t']:.2f}\n"
        info_str += f"Steps: {state['step']}\n"
        info_str += f"Energy: {state['energy']:.4f}\n"
        self.update_info(info_str)
    
    def stop_simulation(self):
        """Stop the simulation."""
        self.is_running = False
        if self.animation_obj:
            self.animation_obj.event_source.stop()
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.update_info("Simulation stopped.")
    
    def reset_simulation(self):
        """Reset the simulation."""
        self.stop_simulation()
        self.simulator = None
        self.energy_history = []
        self.time_history = []
        
        # Clear plots
        self.ax1.clear()
        self.ax1.set_xlabel('x')
        self.ax1.set_ylabel('u(x,t)')
        self.ax1.set_title('Kuramoto-Sivashinsky Solution')
        self.ax1.grid(True, alpha=0.3)
        
        self.ax2.clear()
        self.ax2.set_xlabel('Time')
        self.ax2.set_ylabel('Energy')
        self.ax2.set_title('System Energy')
        self.ax2.grid(True, alpha=0.3)
        
        self.canvas.draw()
        self.update_info("Simulation reset.")
    
    def save_data(self):
        """Save simulation data."""
        if self.simulator is None:
            messagebox.showwarning("Warning", "No simulation data to save.")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".npz",
            filetypes=[("NumPy Archive", "*.npz"), ("All Files", "*.*")]
        )
        
        if filename:
            try:
                # Prepare comprehensive data
                state = self.simulator.get_current_state()
                data = {
                    'x': state['x'],
                    'u': state['u'],
                    't': state['t'],
                    'energy_history': np.array(self.energy_history),
                    'time_history': np.array(self.time_history),
                    'L': self.simulator.model.L,
                    'N': self.simulator.model.n,
                    'dt': self.simulator.model.dt,
                    'diffusion': self.simulator.model.diffusion
                }
                np.savez(filename, **data)
                self.update_info(f"Data saved to:\n{filename}")
                messagebox.showinfo("Success", "Data saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save data: {e}")
    
    def save_config(self):
        """Save current configuration."""
        config = self.get_current_config()
        if config is None:
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON", "*.json"), ("All Files", "*.*")]
        )
        
        if filename:
            try:
                config.save(filename)
                messagebox.showinfo("Success", "Configuration saved!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save config: {e}")
    
    def load_config(self):
        """Load configuration from file."""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON", "*.json"), ("All Files", "*.*")]
        )
        
        if filename:
            try:
                config = Config.load(filename)
                sim = config.get('simulation')
                
                self.L_var.set(str(sim['L']))
                self.N_var.set(str(sim['N']))
                self.dt_var.set(str(sim['dt']))
                self.diff_var.set(str(sim['diffusion']))
                self.ic_var.set(sim['initial_condition'])
                self.trans_var.set(str(sim['n_transient']))
                self.steps_var.set(str(sim['n_steps']))
                
                messagebox.showinfo("Success", "Configuration loaded!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load config: {e}")
    
    def update_info(self, text):
        """Update info text widget."""
        self.info_text.config(state='normal')
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(1.0, text)
        self.info_text.config(state='disabled')


def main():
    """Main entry point."""
    root = tk.Tk()
    app = KSGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
