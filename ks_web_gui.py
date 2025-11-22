"""
Interactive Web GUI for Kuramoto-Sivashinsky equation simulator.
Uses Dash (Plotly) for browser-based interface.
"""

import dash
from dash import dcc, html, Input, Output, State, callback_context
import plotly.graph_objs as go
import numpy as np
from KS import KS
from config import Config
from simulator import KSSimulator
import json
import base64
import io


class KSWebGUI:
    """Web-based GUI for KS equation simulation."""
    
    def __init__(self, port=8050, debug=False):
        """
        Initialize the web GUI.
        
        Parameters:
        -----------
        port : int
            Port number for the web server
        debug : bool
            Enable debug mode
        """
        self.port = port
        self.debug = debug
        self.app = dash.Dash(__name__, title="KS Equation Simulator")
        
        # Configuration
        self.config = Config()
        self.simulator = None
        self.is_running = False
        
        # Data storage
        self.energy_history = []
        self.time_history = []
        self.current_step = 0
        
        # Setup layout and callbacks
        self._create_layout()
        self._setup_callbacks()
    
    def _create_layout(self):
        """Create the web page layout."""
        
        # Load default preset
        preset = Config.PRESETS['medium_re']
        
        self.app.layout = html.Div([
            # Header
            html.Div([
                html.H1("Kuramoto-Sivashinsky Equation Simulator", 
                       style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': '10px'}),
                html.P("Interactive web-based simulation of the KS equation",
                      style={'textAlign': 'center', 'color': '#7f8c8d', 'marginBottom': '20px'})
            ]),
            
            # Main container
            html.Div([
                # Left panel - Controls
                html.Div([
                    # Preset Selection
                    html.Div([
                        html.H3("Control Panel", style={'color': '#2c3e50', 'marginBottom': '15px'}),
                        html.Label("Preset Configuration:", style={'fontWeight': 'bold'}),
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
                        html.H4("Parameters", style={'color': '#34495e', 'marginTop': '20px'}),
                        
                        html.Label("Domain Length (L):", style={'marginTop': '10px'}),
                        dcc.Input(id='L-input', type='number', value=preset['L'], 
                                 step=0.1, style={'width': '100%', 'marginBottom': '10px'}),
                        
                        html.Label("Grid Points (N):"),
                        dcc.Input(id='N-input', type='number', value=preset['N'], 
                                 step=1, style={'width': '100%', 'marginBottom': '10px'}),
                        
                        html.Label("Time Step (dt):"),
                        dcc.Input(id='dt-input', type='number', value=preset['dt'], 
                                 step=0.01, style={'width': '100%', 'marginBottom': '10px'}),
                        
                        html.Label("Diffusion:"),
                        dcc.Input(id='diff-input', type='number', value=preset['diffusion'], 
                                 step=0.1, style={'width': '100%', 'marginBottom': '10px'}),
                        
                        html.Label("Initial Condition:"),
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
                        html.H4("Simulation Settings", style={'color': '#34495e'}),
                        
                        html.Label("Transient Steps:"),
                        dcc.Input(id='transient-input', type='number', value=500, 
                                 step=50, style={'width': '100%', 'marginBottom': '10px'}),
                        
                        html.Label("Run Steps:"),
                        dcc.Input(id='steps-input', type='number', value=1000, 
                                 step=100, style={'width': '100%', 'marginBottom': '20px'}),
                    ]),
                    
                    # Control Buttons
                    html.Div([
                        html.Button('Start Simulation', id='start-btn', n_clicks=0,
                                   style={'width': '100%', 'padding': '10px', 'marginBottom': '10px',
                                         'backgroundColor': '#27ae60', 'color': 'white', 
                                         'border': 'none', 'borderRadius': '5px', 'cursor': 'pointer'}),
                        html.Button('Stop', id='stop-btn', n_clicks=0,
                                   style={'width': '100%', 'padding': '10px', 'marginBottom': '10px',
                                         'backgroundColor': '#e74c3c', 'color': 'white', 
                                         'border': 'none', 'borderRadius': '5px', 'cursor': 'pointer'}),
                        html.Button('Reset', id='reset-btn', n_clicks=0,
                                   style={'width': '100%', 'padding': '10px', 'marginBottom': '20px',
                                         'backgroundColor': '#95a5a6', 'color': 'white', 
                                         'border': 'none', 'borderRadius': '5px', 'cursor': 'pointer'}),
                    ]),
                    
                    # Export section
                    html.Div([
                        html.H4("Export", style={'color': '#34495e'}),
                        html.Button('Save Data', id='save-data-btn', n_clicks=0,
                                   style={'width': '100%', 'padding': '8px', 'marginBottom': '8px',
                                         'backgroundColor': '#3498db', 'color': 'white', 
                                         'border': 'none', 'borderRadius': '5px', 'cursor': 'pointer'}),
                        html.Button('Save Config', id='save-config-btn', n_clicks=0,
                                   style={'width': '100%', 'padding': '8px', 'marginBottom': '8px',
                                         'backgroundColor': '#3498db', 'color': 'white', 
                                         'border': 'none', 'borderRadius': '5px', 'cursor': 'pointer'}),
                        dcc.Download(id='download-data'),
                        dcc.Download(id='download-config'),
                    ], style={'marginBottom': '20px'}),
                    
                    # Info panel
                    html.Div([
                        html.H4("Status", style={'color': '#34495e'}),
                        html.Div(id='info-text', 
                                style={'padding': '10px', 'backgroundColor': '#ecf0f1', 
                                      'borderRadius': '5px', 'minHeight': '150px',
                                      'fontFamily': 'monospace', 'fontSize': '12px'})
                    ])
                    
                ], style={'width': '25%', 'display': 'inline-block', 'verticalAlign': 'top',
                         'padding': '20px', 'backgroundColor': '#f8f9fa'}),
                
                # Right panel - Visualization
                html.Div([
                    dcc.Graph(id='solution-plot', style={'height': '45vh'}),
                    dcc.Graph(id='energy-plot', style={'height': '45vh'}),
                ], style={'width': '75%', 'display': 'inline-block', 'verticalAlign': 'top',
                         'padding': '20px'}),
                
            ], style={'display': 'flex'}),
            
            # Hidden divs for state management
            dcc.Store(id='simulation-state', data={'running': False, 'initialized': False}),
            dcc.Interval(id='interval-component', interval=100, n_intervals=0, disabled=True),
            
        ], style={'fontFamily': 'Arial, sans-serif', 'backgroundColor': '#ffffff'})
    
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
                    self.current_step = 0
                    
                    return {'running': True, 'initialized': True}, False
                except Exception as e:
                    print(f"Error starting simulation: {e}")
                    return state, True
                    
            elif button_id == 'stop-btn':
                return {'running': False, 'initialized': state.get('initialized', False)}, True
                
            elif button_id == 'reset-btn':
                self.simulator = None
                self.energy_history = []
                self.time_history = []
                self.current_step = 0
                return {'running': False, 'initialized': False}, True
            
            return state, not state.get('running', False)
        
        @self.app.callback(
            [Output('solution-plot', 'figure'),
             Output('energy-plot', 'figure'),
             Output('info-text', 'children', allow_duplicate=True)],
            [Input('interval-component', 'n_intervals')],
            [State('simulation-state', 'data')],
            prevent_initial_call=True
        )
        def update_plots(n_intervals, state):
            """Update plots with simulation data."""
            if not state.get('running', False) or self.simulator is None:
                return {}, {}, "Simulation not running"
            
            try:
                # Step the simulation
                self.simulator.model.step()
                self.current_step += 1
                
                # Get current state
                current_state = self.simulator.get_current_state()
                
                # Update energy history
                self.energy_history.append(current_state['energy'])
                self.time_history.append(current_state['t'])
                
                # Keep only last 500 points
                if len(self.energy_history) > 500:
                    self.energy_history.pop(0)
                    self.time_history.pop(0)
                
                # Create solution plot
                solution_fig = go.Figure()
                solution_fig.add_trace(go.Scatter(
                    x=current_state['x'],
                    y=current_state['u'],
                    mode='lines',
                    line=dict(color='blue', width=2),
                    name='u(x,t)'
                ))
                solution_fig.update_layout(
                    title=f'Solution at t = {current_state["t"]:.2f}',
                    xaxis_title='x',
                    yaxis_title='u(x,t)',
                    yaxis_range=[-5, 5],
                    template='plotly_white',
                    hovermode='x',
                    showlegend=False
                )
                
                # Create energy plot
                energy_fig = go.Figure()
                energy_fig.add_trace(go.Scatter(
                    x=self.time_history,
                    y=self.energy_history,
                    mode='lines',
                    line=dict(color='red', width=1.5),
                    name='Energy'
                ))
                energy_fig.update_layout(
                    title='System Energy',
                    xaxis_title='Time',
                    yaxis_title='Energy',
                    template='plotly_white',
                    hovermode='x',
                    showlegend=False
                )
                
                # Update info
                info = f"Time: {current_state['t']:.2f}\n"
                info += f"Steps: {current_state['step']}\n"
                info += f"Energy: {current_state['energy']:.4f}\n"
                info += f"Running..."
                
                return solution_fig, energy_fig, info
                
            except Exception as e:
                print(f"Error updating plots: {e}")
                return {}, {}, f"Error: {str(e)}"
        
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
                
                # Convert to JSON
                json_str = json.dumps(data, indent=2)
                
                return dict(content=json_str, filename="ks_simulation_data.json")
            except Exception as e:
                print(f"Error saving data: {e}")
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
                print(f"Error saving config: {e}")
                return None
    
    def run(self):
        """Run the web application."""
        print(f"\n{'='*60}")
        print(f"Kuramoto-Sivashinsky Web GUI")
        print(f"{'='*60}")
        print(f"\nOpen your web browser and navigate to:")
        print(f"\n    http://localhost:{self.port}\n")
        print(f"Press Ctrl+C to stop the server")
        print(f"{'='*60}\n")
        
        self.app.run(debug=self.debug, port=self.port, host='0.0.0.0')


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='KS Equation Web GUI')
    parser.add_argument('--port', type=int, default=8050, 
                       help='Port number for web server (default: 8050)')
    parser.add_argument('--debug', action='store_true', 
                       help='Enable debug mode')
    
    args = parser.parse_args()
    
    gui = KSWebGUI(port=args.port, debug=args.debug)
    gui.run()


if __name__ == '__main__':
    main()
