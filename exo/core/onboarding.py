"""
Onboarding module for the exo Multi-Agent Framework

This module handles the onboarding process for the exo Multi-Agent Framework,
including gathering required environment variables, validating connections,
and storing configuration for future use.
"""

import os
import json
import logging
import getpass
import requests
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

logger = logging.getLogger(__name__)

# Define required environment variables for different services
REQUIRED_ENV_VARS = {
    "llm": [
        {"name": "OPENAI_API_KEY", "description": "OpenAI API key for LLM services", "secret": True, "required": False},
        {"name": "ANTHROPIC_API_KEY", "description": "Anthropic API key for Claude models", "secret": True, "required": False},
        {"name": "GOOGLE_API_KEY", "description": "Google API key for Gemini models", "secret": True, "required": False},
        {"name": "OPENROUTER_API_KEY", "description": "OpenRouter API key for accessing multiple LLM providers", "secret": True, "required": False},
        {"name": "OLLAMA_BASE_URL", "description": "Base URL for Ollama (default: http://localhost:11434)", "secret": False, "required": False, "default": "http://localhost:11434"},
        {"name": "DEFAULT_LLM_PROVIDER", "description": "Default LLM provider to use (openai, anthropic, google, openrouter, ollama)", "secret": False, "required": False, "default": "openai"},
        {"name": "DEFAULT_LLM_MODEL", "description": "Default LLM model to use", "secret": False, "required": False, "default": "gpt-3.5-turbo"},
    ],
    "mcp": [
        {"name": "MCP_SERVER_URL", "description": "URL of the MCP server", "secret": False, "required": True},
        {"name": "MCP_API_KEY", "description": "API key for the MCP server", "secret": True, "required": True},
    ],
}

class Onboarding:
    """
    Onboarding class for the exo Multi-Agent Framework

    This class handles the onboarding process for the exo Multi-Agent Framework,
    including gathering required environment variables, validating connections,
    and storing configuration for future use.
    """

    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize the onboarding process.

        Args:
            config_dir: Directory to store configuration files
        """
        self.config_dir = config_dir or os.path.join(os.path.expanduser("~"), ".exo")
        self.config_file = os.path.join(self.config_dir, "config.json")
        self.mcp_servers_file = os.path.join(self.config_dir, "mcp_servers.json")
        self.config = {}
        self.mcp_servers = {}

        # Create config directory if it doesn't exist
        os.makedirs(self.config_dir, exist_ok=True)

        # Load existing configuration if available
        self._load_config()
        self._load_mcp_servers()

    def _load_config(self):
        """Load configuration from file."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    self.config = json.load(f)
                logger.info("Configuration loaded from %s", self.config_file)
            except Exception as e:
                logger.error("Error loading configuration: %s", e)
                self.config = {}

    def _save_config(self):
        """Save configuration to file."""
        try:
            with open(self.config_file, "w") as f:
                json.dump(self.config, f, indent=2)
            logger.info("Configuration saved to %s", self.config_file)
        except Exception as e:
            logger.error("Error saving configuration: %s", e)

    def _load_mcp_servers(self):
        """Load MCP servers from file."""
        if os.path.exists(self.mcp_servers_file):
            try:
                with open(self.mcp_servers_file, "r") as f:
                    self.mcp_servers = json.load(f)
                logger.info("MCP servers loaded from %s", self.mcp_servers_file)
            except Exception as e:
                logger.error("Error loading MCP servers: %s", e)
                self.mcp_servers = {}

    def _save_mcp_servers(self):
        """Save MCP servers to file."""
        try:
            with open(self.mcp_servers_file, "w") as f:
                json.dump(self.mcp_servers, f, indent=2)
            logger.info("MCP servers saved to %s", self.mcp_servers_file)
        except Exception as e:
            logger.error("Error saving MCP servers: %s", e)

    def check_env_vars(self, service: str, force: bool = False) -> Tuple[bool, List[str]]:
        """
        Check if required environment variables are set for a service.

        Args:
            service: Service to check environment variables for
            force: Whether to force prompting for all variables, even if they are already set

        Returns:
            Tuple of (all_vars_set, missing_vars)
        """
        if service not in REQUIRED_ENV_VARS:
            logger.warning("Unknown service: %s", service)
            return True, []

        missing_vars = []
        for var in REQUIRED_ENV_VARS[service]:
            var_name = var["name"]
            is_required = var.get("required", True)
            has_default = "default" in var

            # If force is True, consider all variables as missing
            if force:
                missing_vars.append(var_name)
            # Otherwise, only consider it missing if it's required and has no default
            elif is_required and not has_default:
                if var_name not in os.environ and var_name not in self.config:
                    missing_vars.append(var_name)

        return len(missing_vars) == 0, missing_vars

    def gather_env_vars(self, service: str, interactive: bool = True, force: bool = False) -> bool:
        """
        Gather required environment variables for a service.

        Args:
            service: Service to gather environment variables for
            interactive: Whether to prompt for missing variables interactively
            force: Whether to force prompting for all variables, even if they are already set

        Returns:
            True if all variables were gathered successfully
        """
        if service not in REQUIRED_ENV_VARS:
            logger.warning("Unknown service: %s", service)
            return False

        all_vars_set, missing_vars = self.check_env_vars(service, force)
        if all_vars_set and not force:
            logger.info("All required environment variables for %s are set", service)
            return True

        if not interactive:
            logger.warning("Missing required environment variables for %s: %s",
                          service, ", ".join(missing_vars))
            return False

        print(f"\nSetting up {service.upper()} integration:")
        print("----------------------------------------")

        # Track if all required variables are set
        all_required_set = True

        for var in REQUIRED_ENV_VARS[service]:
            var_name = var["name"]
            is_required = var.get("required", True)
            has_default = "default" in var

            if var_name in os.environ and not force:
                # Environment variable is already set
                self.config[var_name] = os.environ[var_name]
                continue

            if var_name in self.config and not force:
                # Variable is already in config
                continue

            # Prompt for the variable
            print(f"\n{var['description']}:")

            # Show default if available
            prompt_suffix = ""
            if has_default:
                prompt_suffix = f" (default: {var['default']})"

            if var.get("secret", False):
                # For secret values like API keys, offer visibility options
                print(f"Enter {var_name}{prompt_suffix}")
                print("(API keys are long and complex. Choose how to enter this value:)")
                print("1. Hidden input (most secure)")
                print("2. Visible input (easier to verify)")
                print("3. Masked input (shows partial key)")

                input_choice = input("Choose option (1-3, default: 1): ").strip()

                if input_choice == "2":
                    # Visible input
                    value = input("Enter value (visible): ")
                elif input_choice == "3":
                    # Masked input that shows part of the key
                    value = input("Enter value (will be partially masked): ")
                    if value:
                        # Show only first 4 and last 4 characters
                        masked = value[:4] + "*" * (len(value) - 8) + value[-4:] if len(value) > 8 else value
                        print(f"You entered: {masked}")
                        confirm = input("Is this correct? (y/n): ").lower()
                        if confirm != "y":
                            value = input("Enter value again: ")
                else:
                    # Default to hidden input
                    value = getpass.getpass("Enter value (hidden): ")
            else:
                value = input(f"Enter {var_name}{prompt_suffix}: ")

            # Use default if no value provided and default exists
            if not value and has_default:
                value = var["default"]
                print(f"Using default value: {value}")

            if value:
                self.config[var_name] = value
            elif is_required:
                print(f"Warning: {var_name} is required but not provided")
                all_required_set = False
            else:
                print(f"Skipping optional variable: {var_name}")

        # Save the configuration
        self._save_config()

        return all_required_set

    def validate_llm_connection(self) -> bool:
        """
        Validate connection to LLM services.

        Returns:
            True if at least one LLM provider connection is valid
        """
        # Check if required environment variables are set
        all_vars_set, _ = self.check_env_vars("llm")
        if not all_vars_set:
            return False

        # Track if any provider is valid
        any_provider_valid = False

        # Try OpenAI API
        if "OPENAI_API_KEY" in self.config:
            try:
                api_key = self.config["OPENAI_API_KEY"]
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }
                response = requests.get(
                    "https://api.openai.com/v1/models",
                    headers=headers,
                    timeout=5
                )
                if response.status_code == 200:
                    logger.info("OpenAI API connection validated")
                    any_provider_valid = True
                else:
                    logger.warning("OpenAI API connection failed: %s", response.text)
            except Exception as e:
                logger.warning("Error validating OpenAI API connection: %s", e)

        # Try Anthropic API
        if "ANTHROPIC_API_KEY" in self.config:
            try:
                api_key = self.config["ANTHROPIC_API_KEY"]
                headers = {
                    "x-api-key": api_key,
                    "Content-Type": "application/json",
                    "anthropic-version": "2023-06-01"
                }
                response = requests.get(
                    "https://api.anthropic.com/v1/models",
                    headers=headers,
                    timeout=5
                )
                if response.status_code == 200:
                    logger.info("Anthropic API connection validated")
                    any_provider_valid = True
                else:
                    logger.warning("Anthropic API connection failed: %s", response.text)
            except Exception as e:
                logger.warning("Error validating Anthropic API connection: %s", e)

        # Try Google API
        if "GOOGLE_API_KEY" in self.config:
            try:
                api_key = self.config["GOOGLE_API_KEY"]
                headers = {
                    "x-goog-api-key": api_key,
                    "Content-Type": "application/json"
                }
                response = requests.get(
                    "https://generativelanguage.googleapis.com/v1beta/models",
                    headers=headers,
                    timeout=5
                )
                if response.status_code == 200:
                    logger.info("Google API connection validated")
                    any_provider_valid = True
                else:
                    logger.warning("Google API connection failed: %s", response.text)
            except Exception as e:
                logger.warning("Error validating Google API connection: %s", e)

        # Try OpenRouter API
        if "OPENROUTER_API_KEY" in self.config:
            try:
                api_key = self.config["OPENROUTER_API_KEY"]
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }
                response = requests.get(
                    "https://openrouter.ai/api/v1/models",
                    headers=headers,
                    timeout=5
                )
                if response.status_code == 200:
                    logger.info("OpenRouter API connection validated")
                    any_provider_valid = True
                else:
                    logger.warning("OpenRouter API connection failed: %s", response.text)
            except Exception as e:
                logger.warning("Error validating OpenRouter API connection: %s", e)

        # Try Ollama API
        if "OLLAMA_BASE_URL" in self.config:
            try:
                base_url = self.config["OLLAMA_BASE_URL"]
                response = requests.get(
                    f"{base_url}/api/tags",
                    timeout=5
                )
                if response.status_code == 200:
                    logger.info("Ollama API connection validated")
                    any_provider_valid = True
                else:
                    logger.warning("Ollama API connection failed: %s", response.text)
            except Exception as e:
                logger.warning("Error validating Ollama API connection: %s", e)

        return any_provider_valid

    def validate_mcp_connection(self, server_id: Optional[str] = None) -> bool:
        """
        Validate connection to MCP server.

        Args:
            server_id: ID of the MCP server to validate

        Returns:
            True if connection is valid
        """
        # If no server ID is provided, use the default server
        if server_id is None:
            # Check if required environment variables are set
            all_vars_set, _ = self.check_env_vars("mcp")
            if not all_vars_set:
                return False

            try:
                url = self.config.get("MCP_SERVER_URL")
                api_key = self.config.get("MCP_API_KEY")

                if not url or not api_key:
                    return False

                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }

                # Make a simple request to the MCP server
                response = requests.get(
                    f"{url}/api/status",
                    headers=headers,
                    timeout=5
                )

                if response.status_code == 200:
                    logger.info("MCP server connection validated")
                    return True
                else:
                    logger.warning("MCP server connection failed: %s", response.text)
                    return False
            except Exception as e:
                logger.warning("Error validating MCP server connection: %s", e)
                return False
        else:
            # Validate a specific MCP server
            if server_id not in self.mcp_servers:
                logger.warning("Unknown MCP server: %s", server_id)
                return False

            server = self.mcp_servers[server_id]
            try:
                url = server.get("url")
                api_key = server.get("api_key")

                if not url or not api_key:
                    return False

                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }

                # Make a simple request to the MCP server
                response = requests.get(
                    f"{url}/api/status",
                    headers=headers,
                    timeout=5
                )

                if response.status_code == 200:
                    logger.info("MCP server connection validated: %s", server_id)
                    return True
                else:
                    logger.warning("MCP server connection failed: %s - %s",
                                  server_id, response.text)
                    return False
            except Exception as e:
                logger.warning("Error validating MCP server connection: %s - %s",
                              server_id, e)
                return False

    def add_mcp_server(self, interactive: bool = True) -> Optional[str]:
        """
        Add a new MCP server.

        Args:
            interactive: Whether to prompt for server details interactively

        Returns:
            Server ID if added successfully, None otherwise
        """
        if not interactive:
            logger.warning("Cannot add MCP server in non-interactive mode")
            return None

        print("\nAdding a new MCP server:")
        print("------------------------")

        # Get server details
        server_name = input("Enter server name: ")
        if not server_name:
            print("Server name is required")
            return None

        server_url = input("Enter server URL: ")
        if not server_url:
            print("Server URL is required")
            return None

        # For API key, offer visibility options
        print("Enter server API key:")
        print("(API keys are long and complex. Choose how to enter this value:)")
        print("1. Hidden input (most secure)")
        print("2. Visible input (easier to verify)")
        print("3. Masked input (shows partial key)")

        input_choice = input("Choose option (1-3, default: 1): ").strip()

        if input_choice == "2":
            # Visible input
            server_api_key = input("Enter server API key (visible): ")
        elif input_choice == "3":
            # Masked input that shows part of the key
            server_api_key = input("Enter server API key (will be partially masked): ")
            if server_api_key:
                # Show only first 4 and last 4 characters
                masked = server_api_key[:4] + "*" * (len(server_api_key) - 8) + server_api_key[-4:] if len(server_api_key) > 8 else server_api_key
                print(f"You entered: {masked}")
                confirm = input("Is this correct? (y/n): ").lower()
                if confirm != "y":
                    server_api_key = input("Enter server API key again: ")
        else:
            # Default to hidden input
            server_api_key = getpass.getpass("Enter server API key (hidden): ")

        if not server_api_key:
            print("Server API key is required")
            return None

        # Generate a unique ID for the server
        server_id = server_name.lower().replace(" ", "_")
        counter = 1
        while server_id in self.mcp_servers:
            server_id = f"{server_name.lower().replace(' ', '_')}_{counter}"
            counter += 1

        # Add the server
        self.mcp_servers[server_id] = {
            "name": server_name,
            "url": server_url,
            "api_key": server_api_key
        }

        # Save the configuration
        self._save_mcp_servers()

        # Validate the connection
        if self.validate_mcp_connection(server_id):
            print(f"MCP server '{server_name}' added successfully")
            return server_id
        else:
            print(f"Warning: Could not validate connection to MCP server '{server_name}'")
            print("The server has been added, but may not be accessible")
            return server_id

    def remove_mcp_server(self, server_id: str) -> bool:
        """
        Remove an MCP server.

        Args:
            server_id: ID of the MCP server to remove

        Returns:
            True if removed successfully
        """
        if server_id not in self.mcp_servers:
            logger.warning("Unknown MCP server: %s", server_id)
            return False

        # Remove the server
        server_name = self.mcp_servers[server_id].get("name", server_id)
        del self.mcp_servers[server_id]

        # Save the configuration
        self._save_mcp_servers()

        logger.info("MCP server removed: %s", server_name)
        return True

    def list_mcp_servers(self) -> Dict[str, Dict[str, str]]:
        """
        List all MCP servers.

        Returns:
            Dictionary of server IDs to server details
        """
        return self.mcp_servers

    def run_onboarding(self, interactive: bool = True, force: bool = False) -> bool:
        """
        Run the onboarding process.

        Args:
            interactive: Whether to prompt for missing variables interactively
            force: Whether to force prompting for all variables, even if they are already set

        Returns:
            True if onboarding was successful
        """
        print("\nWelcome to the exo Multi-Agent Framework!")
        print("=========================================")
        print("This onboarding process will help you set up the required")
        print("environment variables and connections for the system to function.")
        print("\nPress Ctrl+C at any time to cancel the onboarding process.")

        # Gather LLM environment variables
        print("\nSetting up LLM integration...")
        llm_success = self.gather_env_vars("llm", interactive, force)
        if not llm_success:
            print("Warning: LLM integration setup incomplete")
            print("Some features may not work correctly")

        # Ask about MCP server preference
        mcp_success = False
        if interactive:
            print("\nMCP Server Integration:")
            print("----------------------")
            print("You can either use a remote MCP server or install a local one.")
            print("1. Use a remote MCP server (requires API key and URL)")
            print("2. Install a local MCP server on this machine")
            print("3. Skip MCP server setup for now")

            choice = input("\nEnter your choice (1-3): ").strip()

            if choice == "1":
                # Gather MCP environment variables for remote server
                print("\nSetting up remote MCP integration...")
                mcp_success = self.gather_env_vars("mcp", interactive)
                if not mcp_success:
                    print("Warning: MCP integration setup incomplete")
                    print("Some features may not work correctly")
            elif choice == "2":
                # We'll handle local MCP server installation later
                mcp_success = True
                print("\nLocal MCP server will be installed after onboarding.")
            else:
                print("\nSkipping MCP server setup.")
        else:
            # In non-interactive mode, try to gather MCP environment variables
            print("\nSetting up MCP integration...")
            mcp_success = self.gather_env_vars("mcp", interactive=False)
            if not mcp_success:
                print("Warning: MCP integration setup incomplete")
                print("Some features may not work correctly")

        # Validate connections
        print("\nValidating connections...")
        llm_valid = self.validate_llm_connection()
        if not llm_valid:
            print("Warning: Could not validate LLM connection")
            print("Please check your API keys and internet connection")

        mcp_valid = False
        if choice != "2":  # Only validate remote MCP connection if not using local
            mcp_valid = self.validate_mcp_connection()
            if not mcp_valid:
                print("Warning: Could not validate MCP connection")
                print("Please check your server URL and API key")

        # Add MCP servers
        local_mcp_installed = False
        if interactive:
            # If user chose to install a local MCP server
            if choice == "2":
                from exo.agents.mcp_manager import MCPManager
                mcp_manager = MCPManager(self)
                server_id = mcp_manager.onboard_new_server(local=True)
                if server_id:
                    local_mcp_installed = True
                    mcp_valid = True

            # Ask if they want to add more MCP servers
            add_server = input("\nWould you like to add another MCP server? (y/n): ").lower()
            while add_server == "y":
                # Ask if they want to add a local or remote server
                if not local_mcp_installed:
                    print("\n1. Add a remote MCP server")
                    print("2. Install a local MCP server")
                    server_choice = input("Enter your choice (1-2): ").strip()

                    if server_choice == "2":
                        from exo.agents.mcp_manager import MCPManager
                        mcp_manager = MCPManager(self)
                        server_id = mcp_manager.onboard_new_server(local=True)
                        if server_id:
                            local_mcp_installed = True
                    else:
                        self.add_mcp_server(interactive=True)
                else:
                    self.add_mcp_server(interactive=True)

                add_server = input("Would you like to add another MCP server? (y/n): ").lower()

        print("\nOnboarding complete!")
        if not llm_valid or not mcp_valid:
            print("Warning: Some connections could not be validated")
            print("The system will continue to function, but some features may not work correctly")

        return llm_success and mcp_success

    def get_env_var(self, var_name: str) -> Optional[str]:
        """
        Get an environment variable from the system or configuration.

        Args:
            var_name: Name of the environment variable

        Returns:
            Value of the environment variable, or None if not set
        """
        # Check system environment first
        if var_name in os.environ:
            return os.environ[var_name]

        # Check configuration
        if var_name in self.config:
            return self.config[var_name]

        return None

    def get_mcp_server(self, server_id: str) -> Optional[Dict[str, str]]:
        """
        Get details for an MCP server.

        Args:
            server_id: ID of the MCP server

        Returns:
            Dictionary of server details, or None if not found
        """
        return self.mcp_servers.get(server_id)

    def export_env_vars(self):
        """Export configuration as environment variables."""
        for var_name, value in self.config.items():
            # Skip None values or convert them to empty strings
            if value is not None:
                os.environ[var_name] = value
            else:
                # Set to empty string instead of None
                os.environ[var_name] = ""

        logger.info("Environment variables exported from configuration")
