"""
Configuration service for exo.

This module provides a centralized service for managing configuration settings,
including LLM API keys, MCP servers, and general settings.
"""

import json
import logging
import os
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

# Default config directory
CONFIG_DIR = os.path.expanduser("~/.exo")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
MCP_SERVERS_FILE = os.path.join(CONFIG_DIR, "mcp_servers.json")
GENERAL_SETTINGS_FILE = os.path.join(CONFIG_DIR, "general_settings.json")

# Default MCP servers
DEFAULT_MCP_SERVERS = [
    {
        "id": "brave_search",
        "name": "Brave Search MCP Server",
        "description": "Official MCP server for Brave Search integration",
        "url": "https://mcp.brave.com",
        "api_key": "",  # User needs to provide their own API key
        "default": True,
        "official": True
    },
    {
        "id": "filesystem",
        "name": "Filesystem MCP Server",
        "description": "Local MCP server for file system access and operations",
        "url": "http://localhost:8090",  # Default local port
        "api_key": "",  # Local servers typically don't require API keys
        "default": True,
        "official": True,
        "local": True
    }
]

# Default configuration structure
DEFAULT_CONFIG = {
    "default_llm_provider": "openai",
    "default_llm_model": "gpt-3.5-turbo",
    "api_keys": {
        "openai": "",
        "anthropic": "",
        "google": "",
        "openrouter": ""
    },
    "ollama": {
        "host": "http://localhost:11434",
        "api_key": ""
    }
}

# Default general settings
DEFAULT_GENERAL_SETTINGS = {
    "theme": "system",
    "auto_scroll": True
}


class ConfigurationService:
    """
    Centralized service for managing configuration settings.

    This service provides methods for loading and saving configuration settings,
    including LLM API keys, MCP servers, and general settings.
    """

    @staticmethod
    def ensure_config_dir():
        """Ensure the configuration directory exists."""
        os.makedirs(CONFIG_DIR, exist_ok=True)

    @staticmethod
    def load_config() -> Dict[str, Any]:
        """Load configuration from file."""
        ConfigurationService.ensure_config_dir()

        if not os.path.exists(CONFIG_FILE):
            # Create default configuration file
            ConfigurationService.save_config(DEFAULT_CONFIG)
            return DEFAULT_CONFIG.copy()

        try:
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)

            # Ensure the config has the expected structure
            if "api_keys" not in config:
                config["api_keys"] = DEFAULT_CONFIG["api_keys"].copy()
            else:
                # Ensure all expected keys exist in api_keys
                for key in DEFAULT_CONFIG["api_keys"]:
                    if key not in config["api_keys"]:
                        config["api_keys"][key] = DEFAULT_CONFIG["api_keys"][key]

            # Ensure ollama config exists
            if "ollama" not in config:
                config["ollama"] = DEFAULT_CONFIG["ollama"].copy()
            elif not isinstance(config["ollama"], dict):
                config["ollama"] = DEFAULT_CONFIG["ollama"].copy()
            else:
                # Ensure all expected keys exist in ollama
                for key in DEFAULT_CONFIG["ollama"]:
                    if key not in config["ollama"]:
                        config["ollama"][key] = DEFAULT_CONFIG["ollama"][key]

            # Ensure default provider and model exist
            if "default_llm_provider" not in config:
                config["default_llm_provider"] = DEFAULT_CONFIG["default_llm_provider"]
            if "default_llm_model" not in config:
                config["default_llm_model"] = DEFAULT_CONFIG["default_llm_model"]

            return config
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            return DEFAULT_CONFIG.copy()

    @staticmethod
    def save_config(config: Dict[str, Any]) -> bool:
        """Save configuration to file with secure permissions."""
        ConfigurationService.ensure_config_dir()

        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump(config, f, indent=2)

            # Set secure permissions (owner read/write only)
            os.chmod(CONFIG_FILE, 0o600)

            # Update environment variables
            ConfigurationService.update_environment_variables(config)

            return True
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            return False

    @staticmethod
    def update_environment_variables(config: Dict[str, Any]):
        """Update environment variables based on configuration."""
        # Update API keys
        if "api_keys" in config:
            api_keys = config["api_keys"]
            if "openai" in api_keys and api_keys["openai"]:
                os.environ["OPENAI_API_KEY"] = api_keys["openai"]
            if "anthropic" in api_keys and api_keys["anthropic"]:
                os.environ["ANTHROPIC_API_KEY"] = api_keys["anthropic"]
            if "google" in api_keys and api_keys["google"]:
                os.environ["GOOGLE_API_KEY"] = api_keys["google"]
            if "openrouter" in api_keys and api_keys["openrouter"]:
                os.environ["OPENROUTER_API_KEY"] = api_keys["openrouter"]

        # Update default provider and model
        if "default_llm_provider" in config:
            os.environ["DEFAULT_LLM_PROVIDER"] = config["default_llm_provider"]
        if "default_llm_model" in config:
            os.environ["DEFAULT_LLM_MODEL"] = config["default_llm_model"]

        # Update Ollama host
        if "ollama" in config and "host" in config["ollama"]:
            os.environ["OLLAMA_BASE_URL"] = config["ollama"]["host"]

    @staticmethod
    def get_api_key(provider: str) -> str:
        """Get the API key for a specific provider."""
        config = ConfigurationService.load_config()

        # Special case for ollama which has a nested structure
        if provider == "ollama":
            if "ollama" in config and isinstance(config["ollama"], dict):
                return config["ollama"].get("api_key", "")
            return ""

        # Check if the key is in the config file
        if "api_keys" in config and provider in config["api_keys"]:
            return config["api_keys"].get(provider, "")

        return ""

    @staticmethod
    def set_api_key(provider: str, api_key: str) -> bool:
        """Set the API key for a specific provider."""
        config = ConfigurationService.load_config()

        # Special case for ollama which has a nested structure
        if provider == "ollama":
            if "ollama" not in config or not isinstance(config["ollama"], dict):
                config["ollama"] = DEFAULT_CONFIG["ollama"].copy()
            config["ollama"]["api_key"] = api_key
        else:
            # Ensure api_keys exists
            if "api_keys" not in config:
                config["api_keys"] = DEFAULT_CONFIG["api_keys"].copy()

            # Update the API key
            config["api_keys"][provider] = api_key

        return ConfigurationService.save_config(config)

    @staticmethod
    def get_default_provider() -> str:
        """Get the default LLM provider."""
        config = ConfigurationService.load_config()
        return config.get("default_llm_provider", DEFAULT_CONFIG["default_llm_provider"])

    @staticmethod
    def get_default_model() -> str:
        """Get the default LLM model."""
        config = ConfigurationService.load_config()
        return config.get("default_llm_model", DEFAULT_CONFIG["default_llm_model"])

    @staticmethod
    def set_default_provider(provider: str) -> bool:
        """Set the default LLM provider."""
        config = ConfigurationService.load_config()
        config["default_llm_provider"] = provider
        return ConfigurationService.save_config(config)

    @staticmethod
    def set_default_model(model: str) -> bool:
        """Set the default LLM model."""
        config = ConfigurationService.load_config()
        config["default_llm_model"] = model
        return ConfigurationService.save_config(config)

    @staticmethod
    def get_ollama_host() -> str:
        """Get the Ollama host."""
        config = ConfigurationService.load_config()
        if "ollama" in config and isinstance(config["ollama"], dict):
            return config["ollama"].get("host", DEFAULT_CONFIG["ollama"]["host"])
        return DEFAULT_CONFIG["ollama"]["host"]

    @staticmethod
    def set_ollama_host(host: str) -> bool:
        """Set the Ollama host."""
        config = ConfigurationService.load_config()
        if "ollama" not in config or not isinstance(config["ollama"], dict):
            config["ollama"] = DEFAULT_CONFIG["ollama"].copy()
        config["ollama"]["host"] = host
        return ConfigurationService.save_config(config)

    # MCP Servers methods
    @staticmethod
    def load_mcp_servers() -> List[Dict[str, Any]]:
        """Load MCP servers from file."""
        ConfigurationService.ensure_config_dir()

        if not os.path.exists(MCP_SERVERS_FILE):
            # Create MCP servers file with default servers
            ConfigurationService.save_mcp_servers(DEFAULT_MCP_SERVERS)
            return DEFAULT_MCP_SERVERS.copy()

        try:
            with open(MCP_SERVERS_FILE, "r") as f:
                servers = json.load(f)

            # Check if we need to add any default servers that aren't already in the list
            if isinstance(servers, list):
                existing_ids = {server.get("id") for server in servers if isinstance(server, dict) and "id" in server}
                for default_server in DEFAULT_MCP_SERVERS:
                    if default_server["id"] not in existing_ids:
                        servers.append(default_server)
                        logger.info(f"Added default MCP server: {default_server['name']}")
            else:
                # If servers is not a list, replace it with the default servers
                logger.warning("MCP servers data is not in the expected format, using defaults")
                servers = DEFAULT_MCP_SERVERS.copy()

            return servers
        except Exception as e:
            logger.error(f"Error loading MCP servers: {e}")
            return []

    @staticmethod
    def save_mcp_servers(servers: List[Dict[str, Any]]) -> bool:
        """Save MCP servers to file with secure permissions."""
        ConfigurationService.ensure_config_dir()

        try:
            with open(MCP_SERVERS_FILE, "w") as f:
                json.dump(servers, f, indent=2)

            # Set secure permissions (owner read/write only)
            os.chmod(MCP_SERVERS_FILE, 0o600)

            return True
        except Exception as e:
            logger.error(f"Error saving MCP servers: {e}")
            return False

    @staticmethod
    def add_mcp_server(server: Dict[str, Any]) -> bool:
        """Add a new MCP server."""
        servers = ConfigurationService.load_mcp_servers()
        servers.append(server)
        return ConfigurationService.save_mcp_servers(servers)

    @staticmethod
    def update_mcp_server(server_id: str, server_data: Dict[str, Any]) -> bool:
        """Update an existing MCP server."""
        servers = ConfigurationService.load_mcp_servers()
        for i, server in enumerate(servers):
            if server.get("id") == server_id:
                # Update server data
                servers[i] = server_data
                return ConfigurationService.save_mcp_servers(servers)

        return False

    @staticmethod
    def delete_mcp_server(server_id: str) -> bool:
        """Delete an MCP server."""
        servers = ConfigurationService.load_mcp_servers()
        for i, server in enumerate(servers):
            if server.get("id") == server_id:
                # Remove server
                servers.pop(i)
                return ConfigurationService.save_mcp_servers(servers)

        return False

    # General settings methods
    @staticmethod
    def load_general_settings() -> Dict[str, Any]:
        """Load general settings from file."""
        ConfigurationService.ensure_config_dir()

        if not os.path.exists(GENERAL_SETTINGS_FILE):
            # Create default general settings file
            ConfigurationService.save_general_settings(DEFAULT_GENERAL_SETTINGS)
            return DEFAULT_GENERAL_SETTINGS.copy()

        try:
            with open(GENERAL_SETTINGS_FILE, "r") as f:
                settings = json.load(f)

            # Ensure all expected keys exist
            for key, value in DEFAULT_GENERAL_SETTINGS.items():
                if key not in settings:
                    settings[key] = value

            return settings
        except Exception as e:
            logger.error(f"Error loading general settings: {e}")
            return DEFAULT_GENERAL_SETTINGS.copy()

    @staticmethod
    def save_general_settings(settings: Dict[str, Any]) -> bool:
        """Save general settings to file with secure permissions."""
        ConfigurationService.ensure_config_dir()

        try:
            with open(GENERAL_SETTINGS_FILE, "w") as f:
                json.dump(settings, f, indent=2)

            # Set secure permissions (owner read/write only)
            os.chmod(GENERAL_SETTINGS_FILE, 0o600)

            return True
        except Exception as e:
            logger.error(f"Error saving general settings: {e}")
            return False
