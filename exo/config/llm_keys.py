"""
LLM API key configuration for exo.

This module provides functions for managing API keys for various LLM providers.
"""

import os
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Default config directory
CONFIG_DIR = os.path.expanduser("~/.exo/config")
LLM_KEYS_FILE = os.path.join(CONFIG_DIR, "llm_keys.json")

# Default LLM API keys structure
DEFAULT_LLM_KEYS = {
    "openai": "",
    "anthropic": "",
    "google": "",  # Google's Gemini models
    "azure_openai": "",
    "openrouter": "",
    "ollama": {
        "host": "http://localhost:11434",
        "api_key": ""
    }
}


def ensure_config_dir():
    """Ensure the config directory exists."""
    os.makedirs(CONFIG_DIR, exist_ok=True)


def load_llm_keys():
    """Load LLM API keys from the config file."""
    ensure_config_dir()
    
    if not os.path.exists(LLM_KEYS_FILE):
        # Create default LLM keys file
        save_llm_keys(DEFAULT_LLM_KEYS)
        return DEFAULT_LLM_KEYS
    
    try:
        with open(LLM_KEYS_FILE, "r") as f:
            llm_keys = json.load(f)
        
        # Ensure all expected keys exist
        for key, value in DEFAULT_LLM_KEYS.items():
            if key not in llm_keys:
                llm_keys[key] = value
            elif key == "ollama" and isinstance(value, dict):
                # Ensure ollama config has all expected fields
                if not isinstance(llm_keys[key], dict):
                    llm_keys[key] = value
                else:
                    for subkey, subvalue in value.items():
                        if subkey not in llm_keys[key]:
                            llm_keys[key][subkey] = subvalue
        
        return llm_keys
    except Exception as e:
        logger.error(f"Error loading LLM keys: {e}")
        return DEFAULT_LLM_KEYS


def save_llm_keys(llm_keys):
    """Save LLM API keys to the config file."""
    ensure_config_dir()
    
    try:
        with open(LLM_KEYS_FILE, "w") as f:
            json.dump(llm_keys, f, indent=2)
        
        # Set secure permissions
        os.chmod(LLM_KEYS_FILE, 0o600)
        
        return True
    except Exception as e:
        logger.error(f"Error saving LLM keys: {e}")
        return False


def get_llm_key(provider):
    """Get the API key for a specific LLM provider."""
    llm_keys = load_llm_keys()
    
    # Special case for ollama which has a nested structure
    if provider == "ollama":
        # Check if the key is in the config file
        if provider in llm_keys and isinstance(llm_keys[provider], dict):
            return llm_keys[provider]
        return DEFAULT_LLM_KEYS[provider]
    
    # Check if the key is in the config file
    if provider in llm_keys and llm_keys[provider]:
        return llm_keys[provider]
    
    # Check if the key is in environment variables
    env_var = f"{provider.upper()}_API_KEY"
    if env_var in os.environ:
        return os.environ[env_var]
    
    # For Azure OpenAI, also check AZURE_OPENAI_API_KEY
    if provider == "azure_openai" and "AZURE_OPENAI_API_KEY" in os.environ:
        return os.environ["AZURE_OPENAI_API_KEY"]
    
    return None


def set_llm_key(provider, api_key):
    """Set the API key for a specific LLM provider."""
    llm_keys = load_llm_keys()
    
    # Special case for ollama which has a nested structure
    if provider == "ollama" and isinstance(api_key, dict):
        if "host" in api_key or "api_key" in api_key:
            if provider not in llm_keys or not isinstance(llm_keys[provider], dict):
                llm_keys[provider] = DEFAULT_LLM_KEYS[provider]
            
            # Update only the provided fields
            for key, value in api_key.items():
                if key in llm_keys[provider]:
                    llm_keys[provider][key] = value
    else:
        llm_keys[provider] = api_key
    
    return save_llm_keys(llm_keys)


def get_all_llm_providers():
    """Get a list of all supported LLM providers."""
    return list(DEFAULT_LLM_KEYS.keys())
