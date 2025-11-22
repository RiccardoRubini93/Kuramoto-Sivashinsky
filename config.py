"""
Configuration management for Kuramoto-Sivashinsky simulation.
"""

import json
import os


class Config:
    """Configuration manager for KS simulations."""
    
    # Default configurations
    DEFAULTS = {
        'simulation': {
            'L': 16.0,
            'N': 128,
            'dt': 0.5,
            'diffusion': 1.0,
            'initial_condition': 'default',
            'n_steps': 1000,
            'n_transient': 500
        },
        'visualization': {
            'xlim': [0, 16],
            'ylim': [-5, 5],
            'animation_interval': 25,
            'fps': 40,
            'colormap': 'magma'
        },
        'output': {
            'save_animation': False,
            'save_data': False,
            'animation_filename': 'KS_animation.mp4',
            'data_filename': 'KS_data.npz'
        }
    }
    
    # Preset configurations for different Reynolds numbers
    PRESETS = {
        'low_re': {
            'L': 8.0,
            'N': 64,
            'dt': 0.25,
            'diffusion': 2.0,
            'description': 'Low Reynolds number (stable)'
        },
        'medium_re': {
            'L': 16.0,
            'N': 128,
            'dt': 0.5,
            'diffusion': 1.0,
            'description': 'Medium Reynolds number (chaotic)'
        },
        'high_re': {
            'L': 32.0,
            'N': 256,
            'dt': 0.25,
            'diffusion': 0.5,
            'description': 'High Reynolds number (turbulent)'
        }
    }
    
    def __init__(self, config_dict=None, preset=None):
        """
        Initialize configuration.
        
        Parameters:
        -----------
        config_dict : dict, optional
            Custom configuration dictionary
        preset : str, optional
            Use a preset configuration ('low_re', 'medium_re', 'high_re')
        """
        # Start with defaults
        self.config = self._deep_copy(self.DEFAULTS)
        
        # Apply preset if specified
        if preset:
            if preset not in self.PRESETS:
                raise ValueError(f"Unknown preset: {preset}. Available: {list(self.PRESETS.keys())}")
            preset_config = self.PRESETS[preset]
            for key, value in preset_config.items():
                if key != 'description':
                    self.config['simulation'][key] = value
        
        # Apply custom config
        if config_dict:
            self._update_config(self.config, config_dict)
    
    def _deep_copy(self, d):
        """Deep copy a dictionary."""
        if isinstance(d, dict):
            return {k: self._deep_copy(v) for k, v in d.items()}
        return d
    
    def _update_config(self, base, update):
        """Recursively update configuration."""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._update_config(base[key], value)
            else:
                base[key] = value
    
    def get(self, section, key=None):
        """
        Get configuration value.
        
        Parameters:
        -----------
        section : str
            Configuration section
        key : str, optional
            Specific key within section
            
        Returns:
        --------
        Configuration value or section dictionary
        """
        if section not in self.config:
            raise KeyError(f"Unknown section: {section}")
        
        if key is None:
            return self.config[section]
        
        if key not in self.config[section]:
            raise KeyError(f"Unknown key '{key}' in section '{section}'")
        
        return self.config[section][key]
    
    def set(self, section, key, value):
        """
        Set configuration value.
        
        Parameters:
        -----------
        section : str
            Configuration section
        key : str
            Configuration key
        value : any
            Value to set
        """
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value
    
    def save(self, filename):
        """
        Save configuration to JSON file.
        
        Parameters:
        -----------
        filename : str
            Output filename
        """
        with open(filename, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    @classmethod
    def load(cls, filename):
        """
        Load configuration from JSON file.
        
        Parameters:
        -----------
        filename : str
            Input filename
            
        Returns:
        --------
        Config
            Configuration object
        """
        with open(filename, 'r') as f:
            config_dict = json.load(f)
        return cls(config_dict=config_dict)
    
    def __repr__(self):
        """String representation."""
        lines = ["Configuration:"]
        for section, values in self.config.items():
            lines.append(f"  [{section}]")
            for key, value in values.items():
                lines.append(f"    {key}: {value}")
        return "\n".join(lines)
