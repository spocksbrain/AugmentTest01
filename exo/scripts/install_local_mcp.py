#!/usr/bin/env python3
"""
Local MCP Server Installation Script

This script installs and configures a local MCP server for the exo Multi-Agent Framework.
"""

import os
import sys
import json
import logging
import argparse
import subprocess
import platform
import shutil
import tempfile
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

# Default installation directory
DEFAULT_INSTALL_DIR = os.path.join(os.path.expanduser("~"), ".exo", "local_mcp")

# MCP server repository URL
MCP_REPO_URL = "https://github.com/example/mcp-server.git"  # Replace with actual repo URL

# Required system dependencies by platform
SYSTEM_DEPENDENCIES = {
    "linux": {
        "debian": ["git", "python3", "python3-pip", "python3-venv", "nodejs", "npm"],
        "fedora": ["git", "python3", "python3-pip", "nodejs", "npm"],
        "arch": ["git", "python3", "python3-pip", "nodejs", "npm"],
    },
    "darwin": ["git", "python3", "nodejs", "npm"],
    "win32": ["git", "python3", "nodejs"],
}

# Required Python packages
PYTHON_DEPENDENCIES = [
    "flask>=2.0.0",
    "flask-socketio>=5.0.0",
    "requests>=2.25.0",
    "pyyaml>=5.4.0",
    "python-dotenv>=0.15.0",
]

def get_platform_info():
    """Get information about the current platform."""
    system = platform.system().lower()
    if system == "linux":
        # Determine Linux distribution
        try:
            with open("/etc/os-release") as f:
                os_release = {}
                for line in f:
                    if "=" in line:
                        key, value = line.strip().split("=", 1)
                        os_release[key] = value.strip('"')
            
            if "ID" in os_release:
                distro = os_release["ID"]
                if distro in ["ubuntu", "debian", "linuxmint"]:
                    return system, "debian"
                elif distro in ["fedora", "rhel", "centos"]:
                    return system, "fedora"
                elif distro in ["arch", "manjaro"]:
                    return system, "arch"
        except Exception as e:
            logger.warning(f"Could not determine Linux distribution: {e}")
        
        return system, "unknown"
    elif system == "darwin":
        return system, "macos"
    elif system == "windows":
        return "win32", "windows"
    else:
        return system, "unknown"

def check_dependencies(system, distro):
    """Check if required system dependencies are installed."""
    logger.info("Checking system dependencies...")
    
    missing_deps = []
    
    if system not in SYSTEM_DEPENDENCIES:
        logger.warning(f"Unsupported system: {system}")
        return False, []
    
    if system == "linux" and distro not in SYSTEM_DEPENDENCIES[system]:
        logger.warning(f"Unsupported Linux distribution: {distro}")
        return False, []
    
    deps = SYSTEM_DEPENDENCIES[system]
    if system == "linux":
        deps = SYSTEM_DEPENDENCIES[system][distro]
    
    for dep in deps:
        if system in ["linux", "darwin"]:
            # Use which to check if the command is available
            try:
                result = subprocess.run(
                    ["which", dep],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    check=False
                )
                if result.returncode != 0:
                    missing_deps.append(dep)
            except Exception as e:
                logger.warning(f"Error checking dependency {dep}: {e}")
                missing_deps.append(dep)
        elif system == "win32":
            # On Windows, check if the command is available in PATH
            try:
                result = subprocess.run(
                    ["where", dep],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    check=False
                )
                if result.returncode != 0:
                    missing_deps.append(dep)
            except Exception as e:
                logger.warning(f"Error checking dependency {dep}: {e}")
                missing_deps.append(dep)
    
    return len(missing_deps) == 0, missing_deps

def install_system_dependencies(system, distro, missing_deps):
    """Install missing system dependencies."""
    logger.info(f"Installing missing system dependencies: {', '.join(missing_deps)}")
    
    if system == "linux":
        if distro == "debian":
            try:
                subprocess.run(
                    ["sudo", "apt-get", "update"],
                    check=True
                )
                subprocess.run(
                    ["sudo", "apt-get", "install", "-y"] + missing_deps,
                    check=True
                )
                return True
            except Exception as e:
                logger.error(f"Error installing dependencies: {e}")
                return False
        elif distro == "fedora":
            try:
                subprocess.run(
                    ["sudo", "dnf", "install", "-y"] + missing_deps,
                    check=True
                )
                return True
            except Exception as e:
                logger.error(f"Error installing dependencies: {e}")
                return False
        elif distro == "arch":
            try:
                subprocess.run(
                    ["sudo", "pacman", "-S", "--noconfirm"] + missing_deps,
                    check=True
                )
                return True
            except Exception as e:
                logger.error(f"Error installing dependencies: {e}")
                return False
    elif system == "darwin":
        # On macOS, use Homebrew
        try:
            # Check if Homebrew is installed
            brew_check = subprocess.run(
                ["which", "brew"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            
            if brew_check.returncode != 0:
                logger.error("Homebrew is not installed. Please install it from https://brew.sh/")
                return False
            
            # Install dependencies
            for dep in missing_deps:
                subprocess.run(
                    ["brew", "install", dep],
                    check=True
                )
            return True
        except Exception as e:
            logger.error(f"Error installing dependencies: {e}")
            return False
    elif system == "win32":
        # On Windows, suggest manual installation
        logger.error("Please install the following dependencies manually:")
        for dep in missing_deps:
            logger.error(f"  - {dep}")
        return False
    
    logger.error(f"Unsupported system or distribution: {system}/{distro}")
    return False

def clone_mcp_repo(install_dir, branch="main"):
    """Clone the MCP server repository."""
    logger.info(f"Cloning MCP server repository to {install_dir}...")
    
    # Create the installation directory if it doesn't exist
    os.makedirs(install_dir, exist_ok=True)
    
    # Check if the directory is empty
    if os.listdir(install_dir):
        logger.warning(f"Installation directory {install_dir} is not empty")
        logger.warning("Checking if it's already a git repository...")
        
        # Check if it's already a git repository
        try:
            result = subprocess.run(
                ["git", "status"],
                cwd=install_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            
            if result.returncode == 0:
                logger.info("Directory is already a git repository, pulling latest changes...")
                subprocess.run(
                    ["git", "pull"],
                    cwd=install_dir,
                    check=True
                )
                return True
            else:
                logger.error(f"Installation directory {install_dir} is not empty and not a git repository")
                logger.error("Please choose a different directory or clear the existing one")
                return False
        except Exception as e:
            logger.error(f"Error checking git repository: {e}")
            return False
    
    # Clone the repository
    try:
        subprocess.run(
            ["git", "clone", "--branch", branch, MCP_REPO_URL, install_dir],
            check=True
        )
        return True
    except Exception as e:
        logger.error(f"Error cloning repository: {e}")
        return False

def setup_python_environment(install_dir):
    """Set up a Python virtual environment for the MCP server."""
    logger.info("Setting up Python virtual environment...")
    
    venv_dir = os.path.join(install_dir, "venv")
    
    # Create virtual environment
    try:
        subprocess.run(
            [sys.executable, "-m", "venv", venv_dir],
            check=True
        )
    except Exception as e:
        logger.error(f"Error creating virtual environment: {e}")
        return False
    
    # Determine the pip executable path
    if os.name == "nt":  # Windows
        pip_path = os.path.join(venv_dir, "Scripts", "pip")
    else:  # Unix-like
        pip_path = os.path.join(venv_dir, "bin", "pip")
    
    # Upgrade pip
    try:
        subprocess.run(
            [pip_path, "install", "--upgrade", "pip"],
            check=True
        )
    except Exception as e:
        logger.error(f"Error upgrading pip: {e}")
        return False
    
    # Install dependencies
    try:
        subprocess.run(
            [pip_path, "install"] + PYTHON_DEPENDENCIES,
            check=True
        )
    except Exception as e:
        logger.error(f"Error installing Python dependencies: {e}")
        return False
    
    # Install the MCP server package
    try:
        subprocess.run(
            [pip_path, "install", "-e", "."],
            cwd=install_dir,
            check=True
        )
    except Exception as e:
        logger.error(f"Error installing MCP server package: {e}")
        return False
    
    return True

def configure_mcp_server(install_dir, port=5000, api_key=None):
    """Configure the MCP server."""
    logger.info("Configuring MCP server...")
    
    config_dir = os.path.join(install_dir, "config")
    os.makedirs(config_dir, exist_ok=True)
    
    # Generate a random API key if none is provided
    if api_key is None:
        import secrets
        api_key = secrets.token_hex(16)
    
    # Create configuration file
    config = {
        "server": {
            "host": "0.0.0.0",
            "port": port,
            "debug": False,
            "api_key": api_key
        },
        "database": {
            "type": "sqlite",
            "path": os.path.join(config_dir, "mcp.db")
        },
        "logging": {
            "level": "INFO",
            "file": os.path.join(config_dir, "mcp.log")
        }
    }
    
    config_path = os.path.join(config_dir, "config.json")
    try:
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)
        logger.info(f"Configuration saved to {config_path}")
        return True, api_key
    except Exception as e:
        logger.error(f"Error saving configuration: {e}")
        return False, None

def create_startup_script(install_dir, system):
    """Create a startup script for the MCP server."""
    logger.info("Creating startup script...")
    
    if system in ["linux", "darwin"]:
        # Unix-like systems
        script_path = os.path.join(install_dir, "start_mcp.sh")
        script_content = f"""#!/bin/bash
# Start the MCP server

# Activate virtual environment
if [ -d "{install_dir}/venv" ]; then
    source "{install_dir}/venv/bin/activate"
fi

# Start the server
cd "{install_dir}"
python -m mcp.server --config "{install_dir}/config/config.json"
"""
        try:
            with open(script_path, "w") as f:
                f.write(script_content)
            os.chmod(script_path, 0o755)  # Make executable
            logger.info(f"Startup script created at {script_path}")
            return True
        except Exception as e:
            logger.error(f"Error creating startup script: {e}")
            return False
    elif system == "win32":
        # Windows
        script_path = os.path.join(install_dir, "start_mcp.bat")
        script_content = f"""@echo off
REM Start the MCP server

REM Activate virtual environment
if exist "{install_dir}\\venv\\Scripts\\activate.bat" (
    call "{install_dir}\\venv\\Scripts\\activate.bat"
)

REM Start the server
cd /d "{install_dir}"
python -m mcp.server --config "{install_dir}\\config\\config.json"
"""
        try:
            with open(script_path, "w") as f:
                f.write(script_content)
            logger.info(f"Startup script created at {script_path}")
            return True
        except Exception as e:
            logger.error(f"Error creating startup script: {e}")
            return False
    else:
        logger.error(f"Unsupported system: {system}")
        return False

def create_service_file(install_dir, system, distro):
    """Create a systemd service file for the MCP server on Linux."""
    if system != "linux":
        return False
    
    logger.info("Creating systemd service file...")
    
    service_name = "mcp-server"
    service_path = os.path.join(install_dir, f"{service_name}.service")
    
    service_content = f"""[Unit]
Description=MCP Server for exo Multi-Agent Framework
After=network.target

[Service]
Type=simple
User={os.getlogin()}
WorkingDirectory={install_dir}
ExecStart={install_dir}/venv/bin/python -m mcp.server --config {install_dir}/config/config.json
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
"""
    
    try:
        with open(service_path, "w") as f:
            f.write(service_content)
        logger.info(f"Service file created at {service_path}")
        
        # Print instructions for installing the service
        logger.info("\nTo install the service, run:")
        logger.info(f"  sudo cp {service_path} /etc/systemd/system/")
        logger.info("  sudo systemctl daemon-reload")
        logger.info(f"  sudo systemctl enable {service_name}")
        logger.info(f"  sudo systemctl start {service_name}")
        
        return True
    except Exception as e:
        logger.error(f"Error creating service file: {e}")
        return False

def install_local_mcp(install_dir=DEFAULT_INSTALL_DIR, port=5000, api_key=None, branch="main"):
    """Install a local MCP server."""
    logger.info(f"Installing local MCP server to {install_dir}...")
    
    # Get platform information
    system, distro = get_platform_info()
    logger.info(f"Detected platform: {system}/{distro}")
    
    # Check dependencies
    deps_ok, missing_deps = check_dependencies(system, distro)
    if not deps_ok:
        logger.warning(f"Missing dependencies: {', '.join(missing_deps)}")
        
        # Ask if the user wants to install dependencies
        print("\nThe following dependencies are missing:")
        for dep in missing_deps:
            print(f"  - {dep}")
        
        if input("\nDo you want to install them? (y/n): ").lower() == "y":
            if not install_system_dependencies(system, distro, missing_deps):
                logger.error("Failed to install system dependencies")
                return False, None
        else:
            logger.error("Cannot proceed without required dependencies")
            return False, None
    
    # Clone the repository
    if not clone_mcp_repo(install_dir, branch):
        return False, None
    
    # Set up Python environment
    if not setup_python_environment(install_dir):
        return False, None
    
    # Configure the server
    config_ok, api_key = configure_mcp_server(install_dir, port, api_key)
    if not config_ok:
        return False, None
    
    # Create startup script
    if not create_startup_script(install_dir, system):
        logger.warning("Failed to create startup script")
    
    # Create service file on Linux
    if system == "linux":
        create_service_file(install_dir, system, distro)
    
    logger.info("\nLocal MCP server installation complete!")
    logger.info(f"Installation directory: {install_dir}")
    logger.info(f"API key: {api_key}")
    logger.info(f"Server port: {port}")
    
    # Print startup instructions
    if system in ["linux", "darwin"]:
        logger.info("\nTo start the server, run:")
        logger.info(f"  {install_dir}/start_mcp.sh")
    elif system == "win32":
        logger.info("\nTo start the server, run:")
        logger.info(f"  {install_dir}\\start_mcp.bat")
    
    return True, {
        "install_dir": install_dir,
        "api_key": api_key,
        "port": port,
        "url": f"http://localhost:{port}"
    }

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Install a local MCP server")
    parser.add_argument("--install-dir", default=DEFAULT_INSTALL_DIR, help="Installation directory")
    parser.add_argument("--port", type=int, default=5000, help="Server port")
    parser.add_argument("--api-key", help="API key (generated if not provided)")
    parser.add_argument("--branch", default="main", help="Git branch to use")
    args = parser.parse_args()
    
    success, server_info = install_local_mcp(
        install_dir=args.install_dir,
        port=args.port,
        api_key=args.api_key,
        branch=args.branch
    )
    
    if success:
        # Save server information to the exo configuration
        config_dir = os.path.join(os.path.expanduser("~"), ".exo")
        os.makedirs(config_dir, exist_ok=True)
        
        # Save as a local MCP server
        local_mcp_file = os.path.join(config_dir, "local_mcp.json")
        try:
            with open(local_mcp_file, "w") as f:
                json.dump(server_info, f, indent=2)
            logger.info(f"Server information saved to {local_mcp_file}")
        except Exception as e:
            logger.error(f"Error saving server information: {e}")
        
        sys.exit(0)
    else:
        logger.error("Installation failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
