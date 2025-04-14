"""
MCP Server Manager for the exo Multi-Agent Framework

This module handles the management of MCP servers, including adding, removing,
and interacting with MCP servers.
"""

import os
import sys
import json
import time
import logging
import platform
import subprocess
import requests
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union

from exo.core.onboarding import Onboarding

logger = logging.getLogger(__name__)

class MCPManager:
    """
    MCP Server Manager for the exo Multi-Agent Framework

    This class handles the management of MCP servers, including adding, removing,
    and interacting with MCP servers.
    """

    # Constants for local MCP server
    LOCAL_MCP_CONFIG = os.path.join(os.path.expanduser("~"), ".exo", "local_mcp.json")

    def __init__(self, onboarding: Optional[Onboarding] = None):
        """
        Initialize the MCP Server Manager.

        Args:
            onboarding: Onboarding instance to use for configuration
        """
        self.onboarding = onboarding or Onboarding()
        self.servers = self.onboarding.list_mcp_servers()
        self.default_server_url = self.onboarding.get_env_var("MCP_SERVER_URL")
        self.default_api_key = self.onboarding.get_env_var("MCP_API_KEY")

        # Load local MCP server if available
        self.local_mcp = self._load_local_mcp()
        if self.local_mcp:
            logger.info(f"Local MCP server found at {self.local_mcp['url']}")

    def add_server(self, interactive: bool = True) -> Optional[str]:
        """
        Add a new MCP server.

        Args:
            interactive: Whether to prompt for server details interactively

        Returns:
            Server ID if added successfully, None otherwise
        """
        server_id = self.onboarding.add_mcp_server(interactive)
        if server_id:
            self.servers = self.onboarding.list_mcp_servers()
        return server_id

    def remove_server(self, server_id: str) -> bool:
        """
        Remove an MCP server.

        Args:
            server_id: ID of the MCP server to remove

        Returns:
            True if removed successfully
        """
        success = self.onboarding.remove_mcp_server(server_id)
        if success:
            self.servers = self.onboarding.list_mcp_servers()
        return success

    def list_servers(self) -> List[Dict[str, str]]:
        """
        List all MCP servers.

        Returns:
            List of server details dictionaries
        """
        # Convert the dictionary to a list of dictionaries with the ID included
        server_list = []
        for server_id, server_info in self.servers.items():
            server_list.append({
                "id": server_id,
                **server_info
            })
        return server_list

    def get_server(self, server_id: str) -> Optional[Dict[str, str]]:
        """
        Get details for an MCP server.

        Args:
            server_id: ID of the MCP server

        Returns:
            Dictionary of server details, or None if not found
        """
        return self.onboarding.get_mcp_server(server_id)

    def validate_server(self, server_id: Optional[str] = None) -> bool:
        """
        Validate connection to an MCP server.

        Args:
            server_id: ID of the MCP server to validate, or None for default

        Returns:
            True if connection is valid
        """
        return self.onboarding.validate_mcp_connection(server_id)

    def send_request(self, endpoint: str, method: str = "GET",
                    data: Optional[Dict[str, Any]] = None,
                    server_id: Optional[str] = None) -> Tuple[bool, Any]:
        """
        Send a request to an MCP server.

        Args:
            endpoint: API endpoint to call
            method: HTTP method to use
            data: Data to send with the request
            server_id: ID of the MCP server to use, or None for default

        Returns:
            Tuple of (success, response_data)
        """
        # Get server details
        url = None
        api_key = None

        if server_id is None:
            # Use default server
            url = self.default_server_url
            api_key = self.default_api_key
        else:
            # Use specified server
            server = self.get_server(server_id)
            if server:
                url = server.get("url")
                api_key = server.get("api_key")

        if not url or not api_key:
            logger.error("No MCP server available")
            return False, {"error": "No MCP server available"}

        # Ensure endpoint starts with /
        if not endpoint.startswith("/"):
            endpoint = f"/{endpoint}"

        # Prepare request
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        full_url = f"{url}{endpoint}"

        try:
            # Send request
            if method.upper() == "GET":
                response = requests.get(full_url, headers=headers, timeout=10)
            elif method.upper() == "POST":
                response = requests.post(full_url, headers=headers, json=data, timeout=10)
            elif method.upper() == "PUT":
                response = requests.put(full_url, headers=headers, json=data, timeout=10)
            elif method.upper() == "DELETE":
                response = requests.delete(full_url, headers=headers, timeout=10)
            else:
                logger.error("Unsupported HTTP method: %s", method)
                return False, {"error": f"Unsupported HTTP method: {method}"}

            # Check response
            if response.status_code >= 200 and response.status_code < 300:
                try:
                    return True, response.json()
                except ValueError:
                    return True, {"message": response.text}
            else:
                logger.error("MCP server request failed: %s - %s",
                            response.status_code, response.text)
                return False, {
                    "error": f"MCP server request failed: {response.status_code}",
                    "message": response.text
                }
        except Exception as e:
            logger.error("Error sending request to MCP server: %s", e)
            return False, {"error": f"Error sending request to MCP server: {e}"}

    def get_server_status(self, server_id: Optional[str] = None) -> Tuple[bool, Dict[str, Any]]:
        """
        Get status of an MCP server.

        Args:
            server_id: ID of the MCP server to check, or None for default

        Returns:
            Tuple of (success, status_data)
        """
        return self.send_request("/api/status", server_id=server_id)

    def get_server_info(self, server_id: Optional[str] = None) -> Tuple[bool, Dict[str, Any]]:
        """
        Get information about an MCP server.

        Args:
            server_id: ID of the MCP server to check, or None for default

        Returns:
            Tuple of (success, info_data)
        """
        return self.send_request("/api/info", server_id=server_id)

    def execute_command(self, command: str, args: Optional[Dict[str, Any]] = None,
                       server_id: Optional[str] = None) -> Tuple[bool, Dict[str, Any]]:
        """
        Execute a command on an MCP server.

        Args:
            command: Command to execute
            args: Arguments for the command
            server_id: ID of the MCP server to use, or None for default

        Returns:
            Tuple of (success, response_data)
        """
        data = {
            "command": command,
            "args": args or {}
        }

        return self.send_request("/api/execute", method="POST", data=data, server_id=server_id)

    def _load_local_mcp(self) -> Optional[Dict[str, Any]]:
        """
        Load local MCP server configuration.

        Returns:
            Dictionary with local MCP server information, or None if not found
        """
        if not os.path.exists(self.LOCAL_MCP_CONFIG):
            return None

        try:
            with open(self.LOCAL_MCP_CONFIG, "r") as f:
                local_mcp = json.load(f)
            return local_mcp
        except Exception as e:
            logger.error(f"Error loading local MCP server configuration: {e}")
            return None

    def is_local_server_running(self) -> bool:
        """
        Check if the local MCP server is running.

        Returns:
            True if the server is running, False otherwise
        """
        if not self.local_mcp:
            return False

        try:
            response = requests.get(f"{self.local_mcp['url']}/api/status", timeout=2)
            return response.status_code == 200
        except Exception:
            return False

    def start_local_server(self) -> bool:
        """
        Start the local MCP server.

        Returns:
            True if the server was started successfully, False otherwise
        """
        if not self.local_mcp:
            logger.error("No local MCP server configured")
            return False

        if self.is_local_server_running():
            logger.info("Local MCP server is already running")
            return True

        # Run the management script
        try:
            script_path = os.path.join(os.path.dirname(__file__), "..", "scripts", "manage_local_mcp.py")
            script_path = os.path.abspath(script_path)

            result = subprocess.run(
                [sys.executable, script_path, "start"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )

            if result.returncode == 0:
                logger.info("Local MCP server started successfully")
                return True
            else:
                logger.error(f"Failed to start local MCP server: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"Error starting local MCP server: {e}")
            return False

    def stop_local_server(self) -> bool:
        """
        Stop the local MCP server.

        Returns:
            True if the server was stopped successfully, False otherwise
        """
        if not self.local_mcp:
            logger.error("No local MCP server configured")
            return False

        if not self.is_local_server_running():
            logger.info("Local MCP server is not running")
            return True

        # Run the management script
        try:
            script_path = os.path.join(os.path.dirname(__file__), "..", "scripts", "manage_local_mcp.py")
            script_path = os.path.abspath(script_path)

            result = subprocess.run(
                [sys.executable, script_path, "stop"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )

            if result.returncode == 0:
                logger.info("Local MCP server stopped successfully")
                return True
            else:
                logger.error(f"Failed to stop local MCP server: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"Error stopping local MCP server: {e}")
            return False

    def install_local_server(self, port: int = 5000) -> bool:
        """
        Install a local MCP server.

        Args:
            port: Port to use for the server

        Returns:
            True if the server was installed successfully, False otherwise
        """
        # Run the installation script
        try:
            script_path = os.path.join(os.path.dirname(__file__), "..", "scripts", "install_local_mcp.py")
            script_path = os.path.abspath(script_path)

            result = subprocess.run(
                [sys.executable, script_path, "--port", str(port)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )

            if result.returncode == 0:
                logger.info("Local MCP server installed successfully")
                # Reload the local MCP configuration
                self.local_mcp = self._load_local_mcp()
                return True
            else:
                logger.error(f"Failed to install local MCP server: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"Error installing local MCP server: {e}")
            return False

    def onboard_new_server(self, local: bool = False) -> Optional[str]:
        """
        Onboard a new MCP server interactively.

        Args:
            local: Whether to install a local MCP server

        Returns:
            Server ID if added successfully, None otherwise
        """
        if local:
            print("\nInstalling a local MCP server:")
            print("-----------------------------")
            print("This process will install a local MCP server on your machine.")

            # Ask for the port
            port = input("\nEnter the port to use (default: 5000): ").strip()
            if not port:
                port = 5000
            else:
                try:
                    port = int(port)
                except ValueError:
                    print("Invalid port number, using default (5000)")
                    port = 5000

            # Install the server
            if not self.install_local_server(port):
                print("Failed to install local MCP server")
                return None

            # Start the server
            print("\nStarting the local MCP server...")
            if not self.start_local_server():
                print("Warning: Failed to start the local MCP server")
                print("You can start it manually later")

            # Add the server to the list of servers
            server_name = "Local MCP Server"
            server_id = "local_mcp"

            # Add the server to the list of servers
            self.servers[server_id] = {
                "name": server_name,
                "url": self.local_mcp["url"],
                "api_key": self.local_mcp["api_key"],
                "local": True
            }

            # Save the configuration
            self.onboarding._save_mcp_servers()

            print(f"\nLocal MCP server '{server_name}' added successfully!")
            print(f"Server URL: {self.local_mcp['url']}")
            print(f"API key: {self.local_mcp['api_key']}")

            return server_id
        else:
            print("\nOnboarding a new MCP server:")
            print("----------------------------")
            print("This process will guide you through adding a new MCP server to the system.")

            # Add the server
            server_id = self.add_server(interactive=True)
            if not server_id:
                print("Failed to add MCP server")
                return None

            # Test the connection
            print("\nTesting connection to the server...")
            success, status = self.get_server_status(server_id)

            if success:
                print("Connection successful!")
                print(f"Server status: {status.get('status', 'Unknown')}")

                # Get server info
                success, info = self.get_server_info(server_id)
                if success:
                    print(f"Server name: {info.get('name', 'Unknown')}")
                    print(f"Server version: {info.get('version', 'Unknown')}")
                    print(f"Server capabilities: {', '.join(info.get('capabilities', []))}")
            else:
                print("Warning: Could not connect to the server")
                print("The server has been added, but may not be accessible")

            return server_id
