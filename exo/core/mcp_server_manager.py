"""
MCP Server Manager for handling local and remote MCP servers.
"""

import json
import logging
import os
import subprocess
import threading
import time
from typing import Dict, List, Any, Optional
import requests

from exo.core.configuration import ConfigurationService

logger = logging.getLogger(__name__)

class MCPServerManager:
    """
    Manager for MCP servers, handling both local and remote servers.
    
    This class provides methods for:
    - Starting and stopping local MCP servers
    - Checking server status
    - Managing server configurations
    """
    
    def __init__(self):
        """Initialize the MCP Server Manager."""
        self.local_servers = {}  # Store local server processes
        
    def initialize_servers(self):
        """Initialize all configured MCP servers."""
        servers = ConfigurationService.load_mcp_servers()
        
        # Start any local servers that are marked as default
        for server in servers:
            if server.get("local") and server.get("default"):
                self.ensure_local_server_running(server)
    
    def ensure_local_server_running(self, server: Dict[str, Any]) -> bool:
        """
        Ensure a local MCP server is running.
        
        Args:
            server: Server configuration
            
        Returns:
            bool: True if the server is running, False otherwise
        """
        server_id = server.get("id")
        server_url = server.get("url")
        
        # Check if the server is already running
        if self._check_server_status(server_url):
            logger.info(f"Local MCP server {server_id} is already running at {server_url}")
            return True
        
        # If it's not running, try to start it
        if server_id == "filesystem":
            return self._start_filesystem_server(server)
        
        # Add other local server types here
        
        logger.warning(f"Unknown local MCP server type: {server_id}")
        return False
    
    def _check_server_status(self, url: str) -> bool:
        """
        Check if a server is running at the given URL.
        
        Args:
            url: Server URL
            
        Returns:
            bool: True if the server is running, False otherwise
        """
        try:
            response = requests.get(f"{url}/health", timeout=2)
            return response.status_code == 200
        except Exception:
            return False
    
    def _start_filesystem_server(self, server: Dict[str, Any]) -> bool:
        """
        Start the filesystem MCP server.
        
        Args:
            server: Server configuration
            
        Returns:
            bool: True if the server was started successfully, False otherwise
        """
        try:
            # Get the server URL and extract the port
            url = server.get("url", "http://localhost:8090")
            port = url.split(":")[-1]
            
            # Start the server as a subprocess
            cmd = ["python", "-m", "exo.mcp.filesystem", "--port", port]
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Store the process
            self.local_servers[server.get("id")] = process
            
            # Wait for the server to start
            for _ in range(5):  # Try for 5 seconds
                if self._check_server_status(url):
                    logger.info(f"Filesystem MCP server started at {url}")
                    return True
                time.sleep(1)
            
            logger.warning(f"Filesystem MCP server started but not responding at {url}")
            return False
        except Exception as e:
            logger.error(f"Error starting filesystem MCP server: {e}")
            return False
    
    def stop_all_local_servers(self):
        """Stop all running local MCP servers."""
        for server_id, process in self.local_servers.items():
            try:
                process.terminate()
                process.wait(timeout=5)
                logger.info(f"Stopped local MCP server: {server_id}")
            except Exception as e:
                logger.error(f"Error stopping local MCP server {server_id}: {e}")
                try:
                    process.kill()
                except Exception:
                    pass
        
        self.local_servers = {}


# Create a singleton instance
mcp_server_manager = MCPServerManager()
