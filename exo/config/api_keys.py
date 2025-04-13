"""
API key configuration for exo.

This module provides functions for managing API keys for various services.
"""

import os
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Default config directory
CONFIG_DIR = os.path.expanduser("~/.exo/config")
API_KEYS_FILE = os.path.join(CONFIG_DIR, "api_keys.json")

# Default API keys structure
DEFAULT_API_KEYS = {
    "openai": "",
    "anthropic": "",
    "google": "",
    "azure": "",
    "openrouter": ""
}


def ensure_config_dir():
    """Ensure the config directory exists."""
    os.makedirs(CONFIG_DIR, exist_ok=True)


def load_api_keys():
    """Load API keys from the config file."""
    ensure_config_dir()
    
    if not os.path.exists(API_KEYS_FILE):
        # Create default API keys file
        save_api_keys(DEFAULT_API_KEYS)
        return DEFAULT_API_KEYS
    
    try:
        with open(API_KEYS_FILE, "r") as f:
            api_keys = json.load(f)
        
        # Ensure all expected keys exist
        for key in DEFAULT_API_KEYS:
            if key not in api_keys:
                api_keys[key] = DEFAULT_API_KEYS[key]
        
        return api_keys
    except Exception as e:
        logger.error(f"Error loading API keys: {e}")
        return DEFAULT_API_KEYS


def save_api_keys(api_keys):
    """Save API keys to the config file."""
    ensure_config_dir()
    
    try:
        with open(API_KEYS_FILE, "w") as f:
            json.dump(api_keys, f, indent=2)
        
        # Set secure permissions
        os.chmod(API_KEYS_FILE, 0o600)
        
        return True
    except Exception as e:
        logger.error(f"Error saving API keys: {e}")
        return False


def get_api_key(service):
    """Get the API key for a specific service."""
    api_keys = load_api_keys()
    
    # Check if the key is in the config file
    if service in api_keys and api_keys[service]:
        return api_keys[service]
    
    # Check if the key is in environment variables
    env_var = f"{service.upper()}_API_KEY"
    if env_var in os.environ:
        return os.environ[env_var]
    
    return None


def set_api_key(service, api_key):
    """Set the API key for a specific service."""
    api_keys = load_api_keys()
    api_keys[service] = api_key
    return save_api_keys(api_keys)


def get_google_api_key():
    """Get the Google API key."""
    return get_api_key("google")


def set_google_api_key(api_key):
    """Set the Google API key."""
    return set_api_key("google", api_key)
