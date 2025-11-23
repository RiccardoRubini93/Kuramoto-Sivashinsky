"""
Production-ready entry point for KS Web GUI.
This module provides the WSGI application for production deployment.
"""

import os
from ks_web_gui import KSWebGUI

# Get configuration from environment variables
PORT = int(os.environ.get('PORT', 8080))
HOST = os.environ.get('HOST', '0.0.0.0')
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

# Create the GUI instance
gui = KSWebGUI(port=PORT, debug=DEBUG, host=HOST)

# Export the Flask server for WSGI
server = gui.app.server

if __name__ == '__main__':
    gui.run()
