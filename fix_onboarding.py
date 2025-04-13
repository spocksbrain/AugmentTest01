#!/usr/bin/env python3
"""
Fix script for the onboarding process
"""

import os
import sys
import json
import logging
import shutil
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

def main():
    """Fix the onboarding process."""
    logger.info("Fixing onboarding process")

    # Get the config directory
    config_dir = os.path.expanduser("~/.exo")
    config_file = os.path.join(config_dir, "config.json")
    mcp_servers_file = os.path.join(config_dir, "mcp_servers.json")

    # Check if the config directory exists
    if not os.path.exists(config_dir):
        logger.info(f"Config directory {config_dir} does not exist, creating it")
        os.makedirs(config_dir, exist_ok=True)

    # Backup existing config files if they exist
    if os.path.exists(config_file):
        backup_file = f"{config_file}.bak"
        logger.info(f"Backing up {config_file} to {backup_file}")
        shutil.copy2(config_file, backup_file)

    if os.path.exists(mcp_servers_file):
        backup_file = f"{mcp_servers_file}.bak"
        logger.info(f"Backing up {mcp_servers_file} to {backup_file}")
        shutil.copy2(mcp_servers_file, backup_file)

    # Create a new config file with empty values
    # We'll use empty strings to ensure compatibility with environment variables
    config = {
        "OPENAI_API_KEY": "",
        "ANTHROPIC_API_KEY": "",
        "GOOGLE_API_KEY": "",
        "OPENROUTER_API_KEY": "",
        "OLLAMA_BASE_URL": "http://localhost:11434",
        "DEFAULT_LLM_PROVIDER": "openai",
        "DEFAULT_LLM_MODEL": "gpt-3.5-turbo"
    }

    # Write the config file
    with open(config_file, "w") as f:
        json.dump(config, f, indent=2)

    # Create an empty MCP servers file
    mcp_servers = {}

    # Write the MCP servers file
    with open(mcp_servers_file, "w") as f:
        json.dump(mcp_servers, f, indent=2)

    logger.info("Onboarding process fixed")
    logger.info("You can now run the onboarding process with:")
    logger.info("  python run_exo.py --onboard")

if __name__ == "__main__":
    main()
