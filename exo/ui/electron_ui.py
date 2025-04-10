"""
Electron UI module for the exo Multi-Agent Framework.

This module provides a native desktop UI using Electron.
"""

import os
import sys
import subprocess
import threading
import logging
import platform
import time
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)

class ElectronUI:
    """
    Electron UI for the exo Multi-Agent Framework.
    
    This class provides a native desktop UI using Electron.
    """
    
    def __init__(self, host: str = "localhost", port: int = 8080, websocket_port: int = 8765):
        """
        Initialize the Electron UI.
        
        Args:
            host: Host to bind to
            port: Port to bind to
            websocket_port: Port for the WebSocket server
        """
        self.host = host
        self.port = port
        self.websocket_port = websocket_port
        self.electron_process = None
        self.electron_thread = None
        self.is_running = False
        
        # Get the path to the Electron UI directory
        self.electron_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "electron")
        
        # Check if the Electron UI directory exists
        if not os.path.exists(self.electron_dir):
            logger.error(f"Electron UI directory not found: {self.electron_dir}")
            raise FileNotFoundError(f"Electron UI directory not found: {self.electron_dir}")
    
    def start(self, open_ui: bool = True) -> bool:
        """
        Start the Electron UI.
        
        Args:
            open_ui: Whether to open the UI
            
        Returns:
            True if the UI was started successfully, False otherwise
        """
        if self.is_running:
            logger.warning("Electron UI is already running")
            return True
        
        # Check if we're in a container
        in_container = os.path.exists('/.dockerenv') or os.environ.get('CONTAINER_ENV')
        if in_container:
            logger.info("Running in a container, skipping Electron UI")
            return False
        
        # Launch the Electron app in a separate thread
        self.electron_thread = threading.Thread(target=self._launch_electron_app)
        self.electron_thread.daemon = True
        self.electron_thread.start()
        
        # Wait for the Electron app to start
        time.sleep(1.0)
        
        # Check if the Electron app is running
        if self.electron_process and self.electron_process.poll() is None:
            self.is_running = True
            logger.info("Electron UI started successfully")
            return True
        else:
            logger.error("Failed to start Electron UI")
            return False
    
    def stop(self) -> None:
        """Stop the Electron UI."""
        if not self.is_running:
            logger.warning("Electron UI is not running")
            return
        
        # Terminate the Electron process
        if self.electron_process:
            try:
                self.electron_process.terminate()
                self.electron_process.wait(timeout=5.0)
                logger.info("Electron UI stopped")
            except subprocess.TimeoutExpired:
                logger.warning("Electron UI did not terminate gracefully, killing it")
                self.electron_process.kill()
            except Exception as e:
                logger.error(f"Error stopping Electron UI: {e}")
        
        self.is_running = False
    
    def _launch_electron_app(self) -> None:
        """Launch the Electron app."""
        try:
            # Get the path to the launch script
            launch_script = os.path.join(self.electron_dir, "launch_electron.py")
            
            # Check if the launch script exists
            if not os.path.exists(launch_script):
                logger.error(f"Electron launch script not found: {launch_script}")
                return
            
            # Build the command
            cmd = [sys.executable, launch_script]
            
            # Set environment variables
            env = os.environ.copy()
            env["EXO_HOST"] = self.host
            env["EXO_PORT"] = str(self.port)
            env["EXO_WEBSOCKET_PORT"] = str(self.websocket_port)
            
            # Launch the Electron app
            logger.info(f"Launching Electron app: {' '.join(cmd)}")
            self.electron_process = subprocess.Popen(cmd, env=env)
            
            # Wait for the process to exit
            self.electron_process.wait()
            
            logger.info("Electron app exited")
        except Exception as e:
            logger.error(f"Error launching Electron app: {e}")
    
    def is_available(self) -> bool:
        """
        Check if the Electron UI is available.
        
        Returns:
            True if the Electron UI is available, False otherwise
        """
        # Check if we're in a container
        in_container = os.path.exists('/.dockerenv') or os.environ.get('CONTAINER_ENV')
        if in_container:
            return False
        
        # Check if the Electron UI directory exists
        if not os.path.exists(self.electron_dir):
            return False
        
        # Check if Node.js is installed
        try:
            subprocess.run(["node", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
        
        # Check if npm is installed
        try:
            subprocess.run(["npm", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
        
        return True
