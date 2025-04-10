#!/usr/bin/env python3
"""
Launch script for the exo Electron UI.

This script checks for dependencies and launches the Electron app.
"""

import os
import sys
import subprocess
import platform
import shutil
import argparse
import logging
from typing import List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('electron-launcher')

# Constants
ELECTRON_DIR = os.path.dirname(os.path.abspath(__file__))
NODE_MODULES_DIR = os.path.join(ELECTRON_DIR, 'node_modules')
PACKAGE_JSON = os.path.join(ELECTRON_DIR, 'package.json')


def check_dependencies() -> bool:
    """Check if all dependencies are installed."""
    # Check for Node.js
    if not shutil.which('node'):
        logger.error('Node.js is not installed. Please install Node.js 14 or later.')
        return False
    
    # Check for npm
    if not shutil.which('npm'):
        logger.error('npm is not installed. Please install npm 6 or later.')
        return False
    
    # Check for Electron dependencies
    if not os.path.exists(NODE_MODULES_DIR) or not os.path.exists(os.path.join(NODE_MODULES_DIR, 'electron')):
        logger.info('Electron dependencies not found. Installing...')
        try:
            subprocess.run(['npm', 'install'], cwd=ELECTRON_DIR, check=True)
        except subprocess.CalledProcessError:
            logger.error('Failed to install Electron dependencies.')
            return False
    
    # Check for system dependencies based on platform
    system = platform.system().lower()
    
    if system == 'linux':
        return check_linux_dependencies()
    elif system == 'darwin':
        return True  # macOS typically has all required dependencies
    elif system == 'windows':
        return check_windows_dependencies()
    else:
        logger.warning(f'Unsupported platform: {system}')
        return True  # Assume dependencies are installed
    
    return True


def check_linux_dependencies() -> bool:
    """Check Linux-specific dependencies."""
    # Check for libasound2
    try:
        subprocess.run(['ldconfig', '-p'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        ldconfig_output = subprocess.check_output(['ldconfig', '-p']).decode('utf-8')
        if 'libasound.so.2' not in ldconfig_output:
            logger.warning('libasound2 not found. Audio functionality may not work.')
            
            # Try to install libasound2
            if os.geteuid() == 0:  # Running as root
                try:
                    # Detect distribution
                    if os.path.exists('/etc/debian_version'):
                        logger.info('Installing libasound2 using apt...')
                        subprocess.run(['apt-get', 'update'], check=True)
                        subprocess.run(['apt-get', 'install', '-y', 'libasound2'], check=True)
                    elif os.path.exists('/etc/fedora-release'):
                        logger.info('Installing alsa-lib using dnf...')
                        subprocess.run(['dnf', 'install', '-y', 'alsa-lib'], check=True)
                    elif os.path.exists('/etc/arch-release'):
                        logger.info('Installing alsa-lib using pacman...')
                        subprocess.run(['pacman', '-Sy', '--noconfirm', 'alsa-lib'], check=True)
                    else:
                        logger.warning('Unsupported Linux distribution. Please install libasound2 manually.')
                        return False
                except subprocess.CalledProcessError:
                    logger.error('Failed to install libasound2.')
                    return False
            else:
                logger.warning('Not running as root. Please install libasound2 manually.')
                return False
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.warning('Failed to check for libasound2. Audio functionality may not work.')
    
    return True


def check_windows_dependencies() -> bool:
    """Check Windows-specific dependencies."""
    # Check for Visual C++ Redistributable
    try:
        # This is a simple check that doesn't guarantee the correct version is installed
        subprocess.run(['reg', 'query', 'HKLM\\SOFTWARE\\Microsoft\\VisualStudio\\14.0\\VC\\Runtimes\\x64', '/v', 'Installed'],
                      stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.warning('Visual C++ Redistributable 2015-2019 may not be installed.')
        logger.info('Please install Visual C++ Redistributable 2015-2019 from https://aka.ms/vs/16/release/vc_redist.x64.exe')
        return False
    
    return True


def launch_electron(args: List[str] = None) -> None:
    """Launch the Electron app."""
    if not check_dependencies():
        logger.error('Dependency check failed. Please install the required dependencies.')
        sys.exit(1)
    
    # Build the command
    if os.path.exists(os.path.join(NODE_MODULES_DIR, '.bin', 'electron')):
        electron_bin = os.path.join(NODE_MODULES_DIR, '.bin', 'electron')
    elif os.path.exists(os.path.join(NODE_MODULES_DIR, '.bin', 'electron.cmd')):
        electron_bin = os.path.join(NODE_MODULES_DIR, '.bin', 'electron.cmd')
    else:
        electron_bin = 'electron'
    
    cmd = [electron_bin, ELECTRON_DIR]
    if args:
        cmd.extend(args)
    
    logger.info(f'Launching Electron app: {" ".join(cmd)}')
    
    try:
        process = subprocess.Popen(cmd)
        logger.info(f'Electron app launched with PID {process.pid}')
        return process
    except Exception as e:
        logger.error(f'Failed to launch Electron app: {e}')
        sys.exit(1)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Launch the exo Electron UI')
    parser.add_argument('--dev', action='store_true', help='Launch in development mode')
    parser.add_argument('--skip-dependency-check', action='store_true', help='Skip dependency check')
    args = parser.parse_args()
    
    if not args.skip_dependency_check:
        if not check_dependencies():
            logger.error('Dependency check failed. Please install the required dependencies.')
            sys.exit(1)
    
    electron_args = []
    if args.dev:
        electron_args.append('--dev')
    
    launch_electron(electron_args)


if __name__ == '__main__':
    main()
