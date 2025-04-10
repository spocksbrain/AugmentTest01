#!/usr/bin/env python3
"""
Local MCP Server Management Script

This script manages local MCP servers for the exo Multi-Agent Framework.
"""

import os
import sys
import json
import time
import signal
import logging
import argparse
import subprocess
import platform
import requests
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Default configuration directory
CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".exo")
LOCAL_MCP_FILE = os.path.join(CONFIG_DIR, "local_mcp.json")

def load_server_info():
    """Load local MCP server information."""
    if not os.path.exists(LOCAL_MCP_FILE):
        logger.error(f"Local MCP server configuration not found: {LOCAL_MCP_FILE}")
        logger.error("Please install a local MCP server first")
        return None
    
    try:
        with open(LOCAL_MCP_FILE, "r") as f:
            server_info = json.load(f)
        return server_info
    except Exception as e:
        logger.error(f"Error loading server information: {e}")
        return None

def is_server_running(url):
    """Check if the MCP server is running."""
    try:
        response = requests.get(f"{url}/api/status", timeout=2)
        return response.status_code == 200
    except Exception:
        return False

def find_server_process():
    """Find the MCP server process."""
    system = platform.system().lower()
    
    if system in ["linux", "darwin"]:
        try:
            # Use ps to find the process
            result = subprocess.run(
                ["ps", "aux"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )
            
            for line in result.stdout.splitlines():
                if "python" in line and "mcp.server" in line:
                    # Extract the PID
                    parts = line.split()
                    if len(parts) > 1:
                        try:
                            return int(parts[1])
                        except ValueError:
                            pass
        except Exception as e:
            logger.error(f"Error finding server process: {e}")
    elif system == "windows":
        try:
            # Use tasklist to find the process
            result = subprocess.run(
                ["tasklist", "/FI", "IMAGENAME eq python.exe", "/FO", "CSV"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )
            
            for line in result.stdout.splitlines():
                if "python.exe" in line and "mcp.server" in line:
                    # Extract the PID
                    parts = line.split(",")
                    if len(parts) > 1:
                        try:
                            return int(parts[1].strip('"'))
                        except ValueError:
                            pass
        except Exception as e:
            logger.error(f"Error finding server process: {e}")
    
    return None

def start_server(server_info):
    """Start the MCP server."""
    if is_server_running(server_info["url"]):
        logger.info("MCP server is already running")
        return True
    
    install_dir = server_info["install_dir"]
    system = platform.system().lower()
    
    if system in ["linux", "darwin"]:
        script_path = os.path.join(install_dir, "start_mcp.sh")
        if not os.path.exists(script_path):
            logger.error(f"Startup script not found: {script_path}")
            return False
        
        try:
            # Start the server in the background
            subprocess.Popen(
                [script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                start_new_session=True
            )
            
            # Wait for the server to start
            for _ in range(10):
                if is_server_running(server_info["url"]):
                    logger.info("MCP server started successfully")
                    return True
                time.sleep(1)
            
            logger.error("Timed out waiting for MCP server to start")
            return False
        except Exception as e:
            logger.error(f"Error starting MCP server: {e}")
            return False
    elif system == "windows":
        script_path = os.path.join(install_dir, "start_mcp.bat")
        if not os.path.exists(script_path):
            logger.error(f"Startup script not found: {script_path}")
            return False
        
        try:
            # Start the server in the background
            subprocess.Popen(
                [script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
            
            # Wait for the server to start
            for _ in range(10):
                if is_server_running(server_info["url"]):
                    logger.info("MCP server started successfully")
                    return True
                time.sleep(1)
            
            logger.error("Timed out waiting for MCP server to start")
            return False
        except Exception as e:
            logger.error(f"Error starting MCP server: {e}")
            return False
    
    logger.error(f"Unsupported system: {system}")
    return False

def stop_server():
    """Stop the MCP server."""
    pid = find_server_process()
    if pid is None:
        logger.info("MCP server is not running")
        return True
    
    system = platform.system().lower()
    
    if system in ["linux", "darwin"]:
        try:
            # Send SIGTERM to the process
            os.kill(pid, signal.SIGTERM)
            
            # Wait for the process to terminate
            for _ in range(5):
                try:
                    # Check if the process still exists
                    os.kill(pid, 0)
                    time.sleep(1)
                except OSError:
                    # Process has terminated
                    logger.info("MCP server stopped successfully")
                    return True
            
            # If the process is still running, send SIGKILL
            try:
                os.kill(pid, signal.SIGKILL)
                logger.info("MCP server forcefully terminated")
                return True
            except OSError:
                # Process has terminated
                logger.info("MCP server stopped successfully")
                return True
        except Exception as e:
            logger.error(f"Error stopping MCP server: {e}")
            return False
    elif system == "windows":
        try:
            # Use taskkill to terminate the process
            subprocess.run(
                ["taskkill", "/PID", str(pid), "/F"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )
            logger.info("MCP server stopped successfully")
            return True
        except Exception as e:
            logger.error(f"Error stopping MCP server: {e}")
            return False
    
    logger.error(f"Unsupported system: {system}")
    return False

def restart_server(server_info):
    """Restart the MCP server."""
    stop_server()
    return start_server(server_info)

def get_server_status(server_info):
    """Get the status of the MCP server."""
    if is_server_running(server_info["url"]):
        logger.info("MCP server is running")
        
        # Get more detailed status
        try:
            response = requests.get(
                f"{server_info['url']}/api/status",
                headers={"Authorization": f"Bearer {server_info['api_key']}"},
                timeout=5
            )
            
            if response.status_code == 200:
                status = response.json()
                logger.info(f"Server version: {status.get('version', 'Unknown')}")
                logger.info(f"Uptime: {status.get('uptime', 'Unknown')}")
                logger.info(f"Active connections: {status.get('active_connections', 'Unknown')}")
                logger.info(f"API requests: {status.get('api_requests', 'Unknown')}")
            else:
                logger.warning(f"Could not get detailed status: {response.status_code}")
        except Exception as e:
            logger.warning(f"Error getting detailed status: {e}")
        
        return True
    else:
        logger.info("MCP server is not running")
        return False

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Manage local MCP server")
    parser.add_argument("action", choices=["start", "stop", "restart", "status"], help="Action to perform")
    args = parser.parse_args()
    
    server_info = load_server_info()
    if server_info is None:
        sys.exit(1)
    
    if args.action == "start":
        if start_server(server_info):
            sys.exit(0)
        else:
            sys.exit(1)
    elif args.action == "stop":
        if stop_server():
            sys.exit(0)
        else:
            sys.exit(1)
    elif args.action == "restart":
        if restart_server(server_info):
            sys.exit(0)
        else:
            sys.exit(1)
    elif args.action == "status":
        if get_server_status(server_info):
            sys.exit(0)
        else:
            sys.exit(1)

if __name__ == "__main__":
    main()
