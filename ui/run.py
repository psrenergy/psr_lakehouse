#!/usr/bin/env python3
"""
Launch script for the PSR Lakehouse Data Explorer Streamlit application.
"""

import subprocess
import sys
import os

def main():
    """Launch the Streamlit application."""
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    app_path = os.path.join(script_dir, "app.py")
    
    # Check if app.py exists
    if not os.path.exists(app_path):
        print(f"Error: app.py not found at {app_path}")
        sys.exit(1)
    
    # Launch Streamlit
    try:
        print("Starting PSR Lakehouse Data Explorer...")
        print("The application will open in your default web browser.")
        print("Press Ctrl+C to stop the application.")
        print("-" * 50)
        
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", app_path,
            "--server.headless", "false",
            "--server.enableCORS", "false"
        ])
    except KeyboardInterrupt:
        print("\nApplication stopped by user.")
    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()