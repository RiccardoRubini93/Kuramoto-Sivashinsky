"""
Interactive Web GUI for Kuramoto-Sivashinsky equation simulator.
Uses Dash (Plotly) for browser-based interface.
"""

import dash
from dash import dcc, html, Input, Output, State, callback_context
import plotly.graph_objs as go
import numpy as np
from collections import deque
from config import Config
from simulator import KSSimulator
import json
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class KSWebGUI:
    """Web-based GUI for KS equation simulation."""
    
    # Configuration constants
    UPDATE_INTERVAL_MS = 100  # Update frequency in milliseconds
    HISTORY_BUFFER_SIZE = 500  # Maximum number of points to keep in energy history
    DEFAULT_PORT = 8050
    
    # Spectrum plot configuration (log10 scale exponents)
    SPECTRUM_Y_LOG_MIN = -8  # Minimum y-axis value: 10^-8
    SPECTRUM_Y_LOG_MAX = 2   # Maximum y-axis value: 10^2
    
    def __init__(self, port=DEFAULT_PORT, debug=False, host='127.0.0.1'):
        """
        Initialize the web GUI.
        
        Parameters:
        -----------
        port : int
            Port number for the web server
        debug : bool
            Enable debug mode
        host : str
            Host address (default: '127.0.0.1' for localhost only,
            use '0.0.0.0' to allow external access)
        """
        self.port = port
        self.debug = debug
        self.host = host
        self.app = dash.Dash(__name__, title="KS Equation Simulator")
        
        # Simulation state
        self.simulator = None
        self.is_running = False
        
        # Data storage using deque for efficient rolling buffers
        self.energy_history = []
        self.time_history = []
        self.spacetime_data = deque(maxlen=200)  # Keep last 200 frames
        
        # Spectrum history for time averaging using deque
        self.spectrum_history = deque(maxlen=10)  # Average over last 10 frames
        
        # Setup layout and callbacks
        self._create_layout()
        self._setup_callbacks()
    
    def _reset_simulation_state(self):
        """Reset simulation state and data storage."""
        self.simulator = None
        self.energy_history = []
        self.time_history = []
        self.spacetime_data.clear()
        self.spectrum_history.clear()
    
    def _create_layout(self):
        """Create the web page layout."""
        
        # Load default preset
        preset = Config.PRESETS['medium_re']
        
        # Define custom CSS for hover effects and dark theme
        self.app.index_string = '''
        <!DOCTYPE html>
        <html>
            <head>
                {%metas%}
                <title>{%title%}</title>
                {%favicon%}
                {%css%}
                <style>
                    /* Dark theme base styles */
                    body {
                        background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 100%);
                        margin: 0;
                        padding: 0;
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        color: #e0e0e0;
                    }
                    
                    /* Grid container for plots */
                    .plot-grid {
                        display: grid;
                        grid-template-columns: 1fr;
                        grid-template-rows: repeat(2, 1fr);
                        gap: 20px;
                        padding: 20px;
                    }
                    
                    /* Individual plot containers */
                    .plot-container {
                        position: relative;
                        background: rgba(26, 31, 58, 0.8);
                        border: 1px solid rgba(0, 255, 255, 0.3);
                        border-radius: 12px;
                        padding: 15px;
                        box-shadow: 0 4px 20px rgba(0, 255, 255, 0.1);
                        backdrop-filter: blur(10px);
                        overflow: hidden;
                    }
                    
                    /* Neon accent animations */
                    @keyframes neon-pulse {
                        0%, 100% { opacity: 1; }
                        50% { opacity: 0.7; }
                    }
                    
                    /* Control panel styling */
                    .control-panel {
                        background: linear-gradient(180deg, rgba(26, 31, 58, 0.95) 0%, rgba(15, 20, 40, 0.95) 100%);
                        border-right: 2px solid rgba(0, 255, 255, 0.3);
                        box-shadow: 5px 0 30px rgba(0, 0, 0, 0.5);
                    }
                    
                    /* Input and dropdown styling */
                    input[type="number"], .Select-control {
                        background-color: rgba(20, 25, 45, 0.8) !important;
                        border: 1px solid rgba(0, 255, 255, 0.3) !important;
                        color: #e0e0e0 !important;
                        border-radius: 6px;
                        transition: all 0.3s ease;
                    }
                    
                    input[type="number"]:focus {
                        border-color: rgba(0, 255, 255, 0.8) !important;
                        box-shadow: 0 0 10px rgba(0, 255, 255, 0.3);
                        outline: none;
                    }
                    
                    /* Button hover effects */
                    button {
                        transition: all 0.3s ease !important;
                    }
                    
                    button:hover {
                        transform: translateY(-2px);
                        box-shadow: 0 5px 20px rgba(0, 0, 0, 0.3);
                    }
                    
                    /* Status panel */
                    .status-panel {
                        background: rgba(20, 25, 45, 0.8) !important;
                        border: 1px solid rgba(0, 255, 255, 0.3) !important;
                        color: #00ff88 !important;
                    }
                    
                    /* Header glow */
                    h1 {
                        text-shadow: 0 0 20px rgba(0, 255, 255, 0.5);
                        animation: neon-pulse 3s ease-in-out infinite;
                    }
                    
                    /* Label styling */
                    label {
                        color: #a0b0c0 !important;
                        font-weight: 500;
                        text-transform: uppercase;
                        font-size: 11px;
                        letter-spacing: 0.5px;
                    }
                    
                    /* Section headers */
                    h3, h4 {
                        color: #00ffff !important;
                        text-transform: uppercase;
                        letter-spacing: 1px;
                        border-bottom: 2px solid rgba(0, 255, 255, 0.3);
                        padding-bottom: 8px;
                    }
                </style>
            </head>
            <body>
                {%app_entry%}
                <footer>
                    {%config%}
                    {%scripts%}
                    {%renderer%}
                </footer>
            </body>
        </html>
        '''
        
        self.app.layout = html.Div([
            # Header
            html.Div([
                html.H1("Kuramoto-Sivashinsky Equation Simulator", 
                       style={'textAlign': 'center', 'color': '#00ffff', 'marginBottom': '10px', 
                              'fontWeight': 'bold', 'fontSize': '2.5em'}),
                html.P("Interactive web-based simulation of the KS equation",
                      style={'textAlign': 'center', 'color': '#a0b0c0', 'marginBottom': '20px',
                             'fontSize': '1.1em', 'letterSpacing': '1px'})
            ], style={'paddingTop': '20px', 'background': 'rgba(10, 14, 39, 0.5)'}),
            
            # Main container
            html.Div([
                # Left panel - Controls
                html.Div([
                    # Preset Selection
                    html.Div([
                        html.H3("Control Panel", style={'color': '#00ffff', 'marginBottom': '15px'}),
                        html.Label("Preset Configuration:", style={'fontWeight': 'bold', 'color': '#a0b0c0'}),
                        dcc.Dropdown(
                            id='preset-dropdown',
                            options=[
                                {'label': 'Low Reynolds Number', 'value': 'low_re'},
                                {'label': 'Medium Reynolds Number', 'value': 'medium_re'},
                                {'label': 'High Reynolds Number', 'value': 'high_re'}
                            ],
                            value='medium_re',
                            style={'marginBottom': '20px'}
                        ),
                    ]),
                    
                    # Parameters
                    html.Div([
                        html.H4("Parameters", style={'color': '#00ccff', 'marginTop': '20px'}),
                        
                        html.Label("Domain Length (L):", style={'marginTop': '10px', 'color': '#a0b0c0'}),
                        dcc.Input(id='L-input', type='number', value=preset['L'], 
                                 step=0.1, style={'width': '100%', 'marginBottom': '10px'}),
                        
                        html.Label("Grid Points (N):", style={'color': '#a0b0c0'}),
                        dcc.Input(id='N-input', type='number', value=preset['N'], 
                                 step=1, style={'width': '100%', 'marginBottom': '10px'}),
                        
                        html.Label("Time Step (dt):", style={'color': '#a0b0c0'}),
                        dcc.Input(id='dt-input', type='number', value=preset['dt'], 
                                 step=0.01, style={'width': '100%', 'marginBottom': '10px'}),
                        
                        html.Label("Diffusion:", style={'color': '#a0b0c0'}),
                        dcc.Input(id='diff-input', type='number', value=preset['diffusion'], 
                                 step=0.1, style={'width': '100%', 'marginBottom': '10px'}),
                        
                        html.Label("Initial Condition:", style={'color': '#a0b0c0'}),
                        dcc.Dropdown(
                            id='ic-dropdown',
                            options=[
                                {'label': 'Default', 'value': 'default'},
                                {'label': 'Random', 'value': 'random'},
                                {'label': 'Sine', 'value': 'sine'}
                            ],
                            value='default',
                            style={'marginBottom': '20px'}
                        ),
                    ], style={'marginBottom': '20px'}),
                    
                    # Simulation Settings
                    html.Div([
                        html.H4("Simulation Settings", style={'color': '#00ccff'}),
                        
                        html.Label("Transient Steps:", style={'color': '#a0b0c0'}),
                        dcc.Input(id='transient-input', type='number', value=500, 
                                 step=50, style={'width': '100%', 'marginBottom': '10px'}),
                        
                        html.Label("Run Steps:", style={'color': '#a0b0c0'}),
                        dcc.Input(id='steps-input', type='number', value=1000, 
                                 step=100, style={'width': '100%', 'marginBottom': '20px'}),
                    ]),
                    
                    # Control Buttons
                    html.Div([
                        html.Button('Start Simulation', id='start-btn', n_clicks=0,
                                   style={'width': '100%', 'padding': '12px', 'marginBottom': '10px',
                                         'backgroundColor': '#00ff88', 'color': '#0a0e27', 
                                         'border': 'none', 'borderRadius': '8px', 'cursor': 'pointer',
                                         'fontWeight': 'bold', 'fontSize': '14px', 'textTransform': 'uppercase'}),
                        html.Button('Stop', id='stop-btn', n_clicks=0,
                                   style={'width': '100%', 'padding': '12px', 'marginBottom': '10px',
                                         'backgroundColor': '#ff4466', 'color': 'white', 
                                         'border': 'none', 'borderRadius': '8px', 'cursor': 'pointer',
                                         'fontWeight': 'bold', 'fontSize': '14px', 'textTransform': 'uppercase'}),
                        html.Button('Reset', id='reset-btn', n_clicks=0,
                                   style={'width': '100%', 'padding': '12px', 'marginBottom': '20px',
                                         'backgroundColor': '#6677aa', 'color': 'white', 
                                         'border': 'none', 'borderRadius': '8px', 'cursor': 'pointer',
                                         'fontWeight': 'bold', 'fontSize': '14px', 'textTransform': 'uppercase'}),
                    ]),
                    
                    # Export section
                    html.Div([
                        html.H4("Export", style={'color': '#00ccff'}),
                        html.Button('Save Data', id='save-data-btn', n_clicks=0,
                                   style={'width': '100%', 'padding': '10px', 'marginBottom': '8px',
                                         'backgroundColor': '#0099ff', 'color': 'white', 
                                         'border': 'none', 'borderRadius': '8px', 'cursor': 'pointer',
                                         'fontWeight': 'bold', 'fontSize': '13px'}),
                        html.Button('Save Config', id='save-config-btn', n_clicks=0,
                                   style={'width': '100%', 'padding': '10px', 'marginBottom': '8px',
                                         'backgroundColor': '#0099ff', 'color': 'white', 
                                         'border': 'none', 'borderRadius': '8px', 'cursor': 'pointer',
                                         'fontWeight': 'bold', 'fontSize': '13px'}),
                        dcc.Download(id='download-data'),
                        dcc.Download(id='download-config'),
                    ], style={'marginBottom': '20px'}),
                    
                    # Info panel
                    html.Div([
                        html.H4("Status", style={'color': '#00ccff'}),
                        html.Div(id='info-text', className='status-panel',
                                style={'padding': '10px', 'backgroundColor': 'rgba(20, 25, 45, 0.8)', 
                                      'borderRadius': '8px', 'minHeight': '150px', 'border': '1px solid rgba(0, 255, 255, 0.3)',
                                      'fontFamily': 'monospace', 'fontSize': '12px', 'color': '#00ff88'})
                    ])
                    
                ], style={'width': '25%', 'display': 'inline-block', 'verticalAlign': 'top',
                         'padding': '20px', 'backgroundColor': 'rgba(15, 20, 40, 0.95)'}, 
                   className='control-panel'),
                
                # Right panel - Visualization
                html.Div([
                    html.Div([
                        dcc.Graph(id='spectrum-plot', style={'height': '45vh'}),
                    ], className='plot-container'),
                    html.Div([
                        dcc.Graph(id='spacetime-plot', style={'height': '45vh'}),
                    ], className='plot-container'),
                ], style={'width': '75%'}, className='plot-grid'),
                
            ], style={'display': 'flex'}),
            
            # Hidden divs for state management
            dcc.Store(id='simulation-state', data={'running': False, 'initialized': False}),
            dcc.Interval(id='interval-component', interval=self.UPDATE_INTERVAL_MS, n_intervals=0, disabled=True),
            
        ], style={'fontFamily': 'Arial, sans-serif', 'backgroundColor': '#0a0e27', 'minHeight': '100vh'})
    
    def _setup_callbacks(self):
        """Setup all callback functions."""
        
        @self.app.callback(
            [Output('L-input', 'value'),
             Output('N-input', 'value'),
             Output('dt-input', 'value'),
             Output('diff-input', 'value'),
             Output('info-text', 'children')],
            [Input('preset-dropdown', 'value')],
            prevent_initial_call=False
        )
        def update_preset(preset_name):
            """Update parameters when preset is selected."""
            preset = Config.PRESETS.get(preset_name, Config.PRESETS['medium_re'])
            info = f"Loaded preset: {preset_name}\n{preset.get('description', '')}"
            return preset['L'], preset['N'], preset['dt'], preset['diffusion'], info
        
        @self.app.callback(
            [Output('simulation-state', 'data'),
             Output('interval-component', 'disabled')],
            [Input('start-btn', 'n_clicks'),
             Input('stop-btn', 'n_clicks'),
             Input('reset-btn', 'n_clicks')],
            [State('simulation-state', 'data'),
             State('L-input', 'value'),
             State('N-input', 'value'),
             State('dt-input', 'value'),
             State('diff-input', 'value'),
             State('ic-dropdown', 'value'),
             State('transient-input', 'value'),
             State('steps-input', 'value')],
            prevent_initial_call=True
        )
        def control_simulation(start_clicks, stop_clicks, reset_clicks, state,
                              L, N, dt, diff, ic, transient, steps):
            """Control simulation start/stop/reset."""
            ctx = callback_context
            if not ctx.triggered:
                return state, True
            
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]
            
            if button_id == 'start-btn':
                # Initialize simulator
                try:
                    config = Config()
                    config.set('simulation', 'L', float(L))
                    config.set('simulation', 'N', int(N))
                    config.set('simulation', 'dt', float(dt))
                    config.set('simulation', 'diffusion', float(diff))
                    config.set('simulation', 'initial_condition', ic)
                    config.set('simulation', 'n_transient', int(transient))
                    config.set('simulation', 'n_steps', int(steps))
                    
                    self.simulator = KSSimulator(config)
                    self.simulator.run_transient()
                    self.energy_history = []
                    self.time_history = []
                    self.spacetime_data.clear()
                    self.spectrum_history.clear()
                    
                    return {'running': True, 'initialized': True}, False
                except Exception as e:
                    error_msg = f"Error starting simulation: {e}"
                    logging.error(error_msg)
                    return state, True
                    
            elif button_id == 'stop-btn':
                return {'running': False, 'initialized': state.get('initialized', False)}, True
                
            elif button_id == 'reset-btn':
                self._reset_simulation_state()
                return {'running': False, 'initialized': False}, True
            
            return state, not state.get('running', False)
        
        @self.app.callback(
            [Output('spectrum-plot', 'figure'),
             Output('spacetime-plot', 'figure'),
             Output('info-text', 'children', allow_duplicate=True)],
            [Input('interval-component', 'n_intervals')],
            [State('simulation-state', 'data')],
            prevent_initial_call=True
        )
        def update_plots(n_intervals, state):
            """
            Update plots with simulation data.
            
            Note: allow_duplicate=True is necessary because info-text is updated by both
            the preset callback and this callback. Without it, Dash would raise an error
            preventing multiple callbacks from targeting the same output component.
            """
            if not state.get('running', False) or self.simulator is None:
                # Return empty figures when not running
                empty_fig = go.Figure()
                empty_fig.update_layout(
                    template='plotly_dark',
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(20, 25, 45, 0.3)',
                    font=dict(color='#e0e0e0'),
                    margin=dict(l=60, r=20, t=40, b=50)
                )
                return empty_fig, empty_fig, "Simulation not running"
            
            try:
                # Step the simulation
                self.simulator.model.step()
                
                # Get current state
                current_state = self.simulator.get_current_state()
                
                # Update energy history (used in status panel display)
                self.energy_history.append(current_state['energy'])
                self.time_history.append(current_state['t'])
                
                # Keep only last HISTORY_BUFFER_SIZE points
                if len(self.energy_history) > self.HISTORY_BUFFER_SIZE:
                    self.energy_history.pop(0)
                    self.time_history.pop(0)
                
                # Store data for spacetime plot (deque handles max length automatically)
                self.spacetime_data.append(current_state['u'].copy())
                
                # Create spectral density plot (log scale) with time averaging
                spectrum_fig = go.Figure()
                try:
                    # Get power spectrum
                    k, spec = self.simulator.model.get_spectrum()
                    # Convert wavenumber to wavelength: λ = 2π/k (avoiding k=0)
                    mask = k > 0
                    k_nonzero = k[mask]
                    spec_nonzero = spec[mask]
                    
                    if len(k_nonzero) > 0:
                        wavelength = 2 * np.pi / k_nonzero
                        
                        # Ensure wavelength values are positive and valid for log scale
                        wavelength = np.maximum(wavelength, 1e-10)
                        
                        # Ensure spectral density is positive (handle numerical precision)
                        spec_nonzero = np.maximum(spec_nonzero, 1e-10)
                        
                        # Store spectrum for time averaging (deque handles max length automatically)
                        self.spectrum_history.append(spec_nonzero.copy())
                        
                        # Calculate time-averaged spectrum
                        spec_avg = np.mean(self.spectrum_history, axis=0)
                        
                        # Plot the time-averaged spectrum
                        spectrum_fig.add_trace(go.Scatter(
                            x=wavelength,
                            y=spec_avg,
                            mode='lines',
                            line=dict(color='#00ff88', width=2),
                            name='Time-Averaged Spectral Density'
                        ))
                        
                        # Calculate x-axis range safely with robust validation
                        # Ensure positive values and handle edge cases
                        wavelength_min = max(float(wavelength.min()), 1e-10)
                        wavelength_max = max(float(wavelength.max()), wavelength_min * 10)
                        
                        # Validate that log10 will succeed
                        if wavelength_min > 0 and wavelength_max > 0:
                            x_range = [np.log10(wavelength_min), np.log10(wavelength_max)]
                        else:
                            # Fallback to safe default range
                            x_range = [-2, 2]
                        
                        spectrum_fig.update_layout(
                            title='Power Spectrum vs Wavelength (Time-Averaged)',
                            xaxis_title='Wavelength λ (log scale)',
                            yaxis_title='Spectral Density (log scale)',
                            xaxis_type='log',  # Log scale for x-axis
                            yaxis_type='log',  # Log scale for y-axis
                            xaxis=dict(range=x_range, fixedrange=True),
                            yaxis=dict(range=[self.SPECTRUM_Y_LOG_MIN, self.SPECTRUM_Y_LOG_MAX], fixedrange=True),
                            template='plotly_dark',
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(20, 25, 45, 0.3)',
                            font=dict(color='#e0e0e0'),
                            hovermode='x',
                            showlegend=False,
                            margin=dict(l=60, r=20, t=40, b=50)  # Optimize margins
                        )
                        # Reverse x-axis so smaller wavelengths (higher frequencies) are on the right
                        spectrum_fig.update_xaxes(autorange='reversed')
                except Exception as e:
                    # If spectrum computation fails, show error message
                    spectrum_fig.add_annotation(
                        text=f'Error computing spectrum:<br>{str(e)}',
                        xref='paper', yref='paper',
                        x=0.5, y=0.5,
                        showarrow=False,
                        font=dict(size=12, color='#ff4466')
                    )
                    spectrum_fig.update_layout(
                        title='Power Spectrum vs Wavelength (Time-Averaged)',
                        template='plotly_dark',
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(20, 25, 45, 0.3)',
                        font=dict(color='#e0e0e0'),
                        margin=dict(l=60, r=20, t=40, b=50)
                    )
                
                # Create spacetime diagram - 3D Surface Plot
                spacetime_fig = go.Figure()
                if len(self.spacetime_data) > 1:
                    try:
                        spacetime_array = np.array(self.spacetime_data)
                        # Create time axis for the stored frames
                        dt = self.simulator.model.dt
                        time_start = current_state['t'] - len(self.spacetime_data) * dt
                        time_end = current_state['t']
                        time_axis = np.linspace(time_start, time_end, len(self.spacetime_data))
                        
                        # Create 3D surface plot
                        spacetime_fig.add_trace(go.Surface(
                            z=spacetime_array,
                            x=current_state['x'],
                            y=time_axis,
                            colorscale='RdBu_r',
                            cmid=0,
                            cmin=-5,
                            cmax=5,
                            colorbar=dict(title='u(x,t)', len=0.7),
                            contours=dict(
                                z=dict(show=True, usecolormap=True, highlightcolor="limegreen", project=dict(z=True))
                            ),
                            lighting=dict(ambient=0.4, diffuse=0.8, fresnel=0.2, specular=0.3, roughness=0.5),
                            lightposition=dict(x=100, y=200, z=0)
                        ))
                        spacetime_fig.update_layout(
                            title='Spacetime Evolution u(x,t) - 3D View',
                            scene=dict(
                                xaxis=dict(title='x', backgroundcolor='rgba(20, 25, 45, 0.3)', gridcolor='rgba(100, 100, 100, 0.3)', showbackground=True),
                                yaxis=dict(title='Time', backgroundcolor='rgba(20, 25, 45, 0.3)', gridcolor='rgba(100, 100, 100, 0.3)', showbackground=True),
                                zaxis=dict(title='u(x,t)', backgroundcolor='rgba(20, 25, 45, 0.3)', gridcolor='rgba(100, 100, 100, 0.3)', showbackground=True, range=[-5, 5]),
                                camera=dict(
                                    eye=dict(x=1.5, y=-1.8, z=0.8),  # Camera position for "following" perspective
                                    center=dict(x=0, y=0.2, z=0),
                                    up=dict(x=0, y=0, z=1)
                                ),
                                aspectmode='auto'  # Use auto aspect mode to maximize space usage
                            ),
                            template='plotly_dark',
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(20, 25, 45, 0.3)',
                            font=dict(color='#e0e0e0'),
                            hovermode='closest',
                            margin=dict(l=0, r=0, t=30, b=0)  # Minimize margins to maximize plot area
                        )
                    except Exception as e:
                        # If spacetime plot fails, show error message
                        spacetime_fig.add_annotation(
                            text=f'Error creating spacetime plot:<br>{str(e)}',
                            xref='paper', yref='paper',
                            x=0.5, y=0.5,
                            showarrow=False,
                            font=dict(size=12, color='#ff4466')
                        )
                        spacetime_fig.update_layout(
                            title='Spacetime Evolution u(x,t) - 3D View',
                            scene=dict(
                                xaxis=dict(title='x', backgroundcolor='rgba(20, 25, 45, 0.3)', gridcolor='rgba(100, 100, 100, 0.3)', showbackground=True),
                                yaxis=dict(title='Time', backgroundcolor='rgba(20, 25, 45, 0.3)', gridcolor='rgba(100, 100, 100, 0.3)', showbackground=True),
                                zaxis=dict(title='u(x,t)', backgroundcolor='rgba(20, 25, 45, 0.3)', gridcolor='rgba(100, 100, 100, 0.3)', showbackground=True)
                            ),
                            template='plotly_dark',
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(20, 25, 45, 0.3)',
                            font=dict(color='#e0e0e0'),
                            margin=dict(l=0, r=0, t=30, b=0)
                        )
                else:
                    spacetime_fig.add_annotation(
                        text='Collecting data...',
                        xref='paper', yref='paper',
                        x=0.5, y=0.5,
                        showarrow=False,
                        font=dict(size=12, color='#00ffff')
                    )
                    spacetime_fig.update_layout(
                        title='Spacetime Evolution u(x,t) - 3D View',
                        scene=dict(
                            xaxis=dict(title='x', backgroundcolor='rgba(20, 25, 45, 0.3)', gridcolor='rgba(100, 100, 100, 0.3)', showbackground=True),
                            yaxis=dict(title='Time', backgroundcolor='rgba(20, 25, 45, 0.3)', gridcolor='rgba(100, 100, 100, 0.3)', showbackground=True),
                            zaxis=dict(title='u(x,t)', backgroundcolor='rgba(20, 25, 45, 0.3)', gridcolor='rgba(100, 100, 100, 0.3)', showbackground=True)
                        ),
                        template='plotly_dark',
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(20, 25, 45, 0.3)',
                        font=dict(color='#e0e0e0'),
                        margin=dict(l=0, r=0, t=30, b=0)
                    )
                
                # Update info
                info = f"Time: {current_state['t']:.2f}\n"
                info += f"Steps: {current_state['step']}\n"
                info += f"Energy: {current_state['energy']:.4f}\n"
                info += f"Running..."
                
                return spectrum_fig, spacetime_fig, info
                
            except Exception as e:
                error_msg = f"Error updating plots: {e}"
                logging.error(error_msg)
                empty_fig = go.Figure()
                empty_fig.update_layout(
                    template='plotly_dark',
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(20, 25, 45, 0.3)',
                    font=dict(color='#e0e0e0'),
                    margin=dict(l=60, r=20, t=40, b=50)
                )
                return empty_fig, empty_fig, error_msg
        
        @self.app.callback(
            Output('download-data', 'data'),
            [Input('save-data-btn', 'n_clicks')],
            prevent_initial_call=True
        )
        def save_data(n_clicks):
            """Save simulation data to file."""
            if self.simulator is None:
                return None
            
            try:
                # Prepare data
                state = self.simulator.get_current_state()
                data = {
                    'x': state['x'].tolist(),
                    'u': state['u'].tolist(),
                    't': state['t'],
                    'energy_history': self.energy_history,
                    'time_history': self.time_history,
                    'L': self.simulator.model.L,
                    'N': self.simulator.model.n,
                    'dt': self.simulator.model.dt,
                    'diffusion': self.simulator.model.diffusion
                }
                
                # Add spacetime data if available
                if len(self.spacetime_data) > 0:
                    data['spacetime_data'] = [frame.tolist() for frame in self.spacetime_data]
                
                # Convert to JSON
                json_str = json.dumps(data, indent=2)
                
                return dict(content=json_str, filename="ks_simulation_data.json")
            except Exception as e:
                error_msg = f"Error saving data: {e}"
                logging.error(error_msg)
                return None
        
        @self.app.callback(
            Output('download-config', 'data'),
            [Input('save-config-btn', 'n_clicks')],
            [State('L-input', 'value'),
             State('N-input', 'value'),
             State('dt-input', 'value'),
             State('diff-input', 'value'),
             State('ic-dropdown', 'value'),
             State('transient-input', 'value'),
             State('steps-input', 'value')],
            prevent_initial_call=True
        )
        def save_config(n_clicks, L, N, dt, diff, ic, transient, steps):
            """Save current configuration."""
            try:
                config = Config()
                config.set('simulation', 'L', float(L))
                config.set('simulation', 'N', int(N))
                config.set('simulation', 'dt', float(dt))
                config.set('simulation', 'diffusion', float(diff))
                config.set('simulation', 'initial_condition', ic)
                config.set('simulation', 'n_transient', int(transient))
                config.set('simulation', 'n_steps', int(steps))
                
                # Convert to JSON
                json_str = json.dumps(config.config, indent=2)
                
                return dict(content=json_str, filename="ks_config.json")
            except Exception as e:
                error_msg = f"Error saving config: {e}"
                logging.error(error_msg)
                return None
    
    def run(self):
        """Run the web application."""
        print(f"\n{'='*60}")
        print(f"Kuramoto-Sivashinsky Web GUI")
        print(f"{'='*60}")
        print(f"\nOpen your web browser and navigate to:")
        if self.host == '0.0.0.0':
            print(f"\n    http://localhost:{self.port}")
            print(f"    (accessible from any network interface)")
        else:
            print(f"\n    http://{self.host}:{self.port}")
        print(f"\nPress Ctrl+C to stop the server")
        print(f"{'='*60}\n")
        
        self.app.run(debug=self.debug, port=self.port, host=self.host)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='KS Equation Web GUI')
    parser.add_argument('--port', type=int, default=KSWebGUI.DEFAULT_PORT, 
                       help=f'Port number for web server (default: {KSWebGUI.DEFAULT_PORT})')
    parser.add_argument('--debug', action='store_true', 
                       help='Enable debug mode')
    parser.add_argument('--host', type=str, default='127.0.0.1',
                       help='Host address (default: 127.0.0.1 for localhost only, use 0.0.0.0 for external access)')
    
    args = parser.parse_args()
    
    gui = KSWebGUI(port=args.port, debug=args.debug, host=args.host)
    gui.run()


if __name__ == '__main__':
    main()
