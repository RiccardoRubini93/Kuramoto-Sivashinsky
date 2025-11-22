"""
Example: Launch the web-based GUI.

This example demonstrates how to programmatically start the web GUI
with custom settings.
"""

from ks_web_gui import KSWebGUI

# Example 1: Launch with defaults (localhost:8050)
def run_default():
    """Run with default settings."""
    gui = KSWebGUI()
    gui.run()

# Example 2: Launch on different port
def run_custom_port():
    """Run on custom port."""
    gui = KSWebGUI(port=9000)
    gui.run()

# Example 3: Launch with external access
def run_external():
    """Run with external network access enabled."""
    gui = KSWebGUI(port=8050, host='0.0.0.0')
    gui.run()

# Example 4: Launch in debug mode
def run_debug():
    """Run in debug mode for development."""
    gui = KSWebGUI(debug=True)
    gui.run()


if __name__ == '__main__':
    # Run the default configuration
    run_default()
