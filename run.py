#!/usr/bin/env python
"""
Quick launcher for Black-Box Testing application.
Run this file to start the Streamlit app.
"""

import sys
import os
import asyncio

# CRITICAL FIX: Windows needs SelectorEventLoop for Playwright
# Set BEFORE any other imports to ensure it applies globally
if sys.platform == 'win32':
    # Use Proactor policy on Windows for proper subprocess support
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

import subprocess

def main():
    """Launch Streamlit application."""
    # Check if streamlit is installed
    try:
        import streamlit
    except ImportError:
        print("Error: Streamlit is not installed.")
        print("Please run: pip install -r requirements.txt")
        sys.exit(1)
    
    # Check if playwright is installed
    try:
        import playwright
    except ImportError:
        print("Error: Playwright is not installed.")
        print("Please run: pip install -r requirements.txt")
        sys.exit(1)
    
    # Launch Streamlit
    app_path = os.path.join("app", "main.py")
    
    if not os.path.exists(app_path):
        print(f"Error: Could not find {app_path}")
        sys.exit(1)
    
    print("🚀 Starting Black-Box Testing Tool...")
    print("📍 Application will open in your browser at http://localhost:8501")
    print("💡 Press Ctrl+C to stop the server\n")
    
    subprocess.run([
        sys.executable,
        "-m",
        "streamlit",
        "run",
        app_path,
        "--server.port=8501",
        "--server.address=localhost"
    ])

if __name__ == "__main__":
    main()

