"""
Entry point for Streamlit Cloud deployment.
This file imports and executes the main Streamlit application.
"""

import sys
import os
from pathlib import Path

# CRITICAL: Set environment variable BEFORE asyncio import
# This forces asyncio to use the correct event loop from the start
if sys.platform == 'win32':
    # Hormati env yang sudah ada; jika tidak ada, pakai folder lokal .pw-browsers bila tersedia,
    # kalau tidak ada fallback ke default ('0'). Harus dilakukan sebelum import asyncio/Playwright.
    if 'PLAYWRIGHT_BROWSERS_PATH' not in os.environ:
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '.'))
        local_browsers_dir = os.path.join(project_root, '.pw-browsers')
        if os.path.isdir(local_browsers_dir):
            os.environ['PLAYWRIGHT_BROWSERS_PATH'] = local_browsers_dir
        else:
            os.environ['PLAYWRIGHT_BROWSERS_PATH'] = '0'  # default path managed by Playwright

import asyncio

# CRITICAL FIX: Set event loop policy BEFORE any imports
# Windows uses ProactorEventLoop by default since Python 3.8
# Playwright requires ProactorEventLoop for subprocess management
if sys.platform == 'win32':
    # Use ProactorEventLoop on Windows (supports subprocess required by Playwright)
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    # Ensure there is a current loop without triggering deprecation warnings
    try:
        # Prefer get_running_loop; avoids DeprecationWarning when no loop exists
        asyncio.get_running_loop()
    except RuntimeError:
        # No running loop yet; create one under the current policy (Proactor on Windows)
        asyncio.set_event_loop(asyncio.new_event_loop())

# Add the current directory to sys.path
sys.path.insert(0, str(Path(__file__).parent))

# Import all from app.main to execute the Streamlit app
# This ensures all Streamlit code in app/main.py is executed
from app.main import *
