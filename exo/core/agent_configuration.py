"""
Agent configuration service for exo.

This module provides functions for managing agent-specific configurations.
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

# Default configuration directory
CONFIG_DIR = os.path.expanduser("~/.exo")
AGENT_CONFIG_FILE = os.path.join(CONFIG_DIR, "agent_config.json")

# Default agent configuration structure
DEFAULT_AGENT_CONFIG = {
    "agents": {}  # Dictionary of agent_id -> agent_config
}


def ensure_config_dir():
    """Ensure the config directory exists."""
    os.makedirs(CONFIG_DIR, exist_ok=True)


def load_agent_configs():
    """Load agent configurations from the config file."""
    ensure_config_dir()
    
    if not os.path.exists(AGENT_CONFIG_FILE):
        # Create default agent config file
        save_agent_configs(DEFAULT_AGENT_CONFIG)
        return DEFAULT_AGENT_CONFIG.copy()
    
    try:
        with open(AGENT_CONFIG_FILE, "r") as f:
            agent_configs = json.load(f)
        
        # Ensure the structure is valid
        if not isinstance(agent_configs, dict) or "agents" not in agent_configs:
            logger.warning("Invalid agent config structure, using default")
            return DEFAULT_AGENT_CONFIG.copy()
        
        return agent_configs
    except Exception as e:
        logger.error(f"Error loading agent configs: {e}")
        return DEFAULT_AGENT_CONFIG.copy()


def save_agent_configs(agent_configs):
    """Save agent configurations to the config file."""
    ensure_config_dir()
    
    try:
        with open(AGENT_CONFIG_FILE, "w") as f:
            json.dump(agent_configs, f, indent=2)
        
        # Set secure permissions
        os.chmod(AGENT_CONFIG_FILE, 0o600)
        
        return True
    except Exception as e:
        logger.error(f"Error saving agent configs: {e}")
        return False


def get_agent_config(agent_id: str) -> Dict[str, Any]:
    """
    Get configuration for a specific agent.
    
    Args:
        agent_id: ID of the agent
        
    Returns:
        Agent configuration dictionary
    """
    agent_configs = load_agent_configs()
    
    if agent_id in agent_configs["agents"]:
        return agent_configs["agents"][agent_id]
    
    # Return empty config if agent not found
    return {}


def set_agent_config(agent_id: str, config: Dict[str, Any]) -> bool:
    """
    Set configuration for a specific agent.
    
    Args:
        agent_id: ID of the agent
        config: Configuration dictionary
        
    Returns:
        True if successful, False otherwise
    """
    agent_configs = load_agent_configs()
    
    agent_configs["agents"][agent_id] = config
    
    return save_agent_configs(agent_configs)


def get_agent_llm_config(agent_id: str) -> Dict[str, Any]:
    """
    Get LLM configuration for a specific agent.
    
    Args:
        agent_id: ID of the agent
        
    Returns:
        Dictionary with provider and model keys, or empty dict if not configured
    """
    agent_config = get_agent_config(agent_id)
    
    if "llm" in agent_config:
        return agent_config["llm"]
    
    return {}


def set_agent_llm_config(agent_id: str, provider: Optional[str] = None, 
                         model: Optional[str] = None) -> bool:
    """
    Set LLM configuration for a specific agent.
    
    Args:
        agent_id: ID of the agent
        provider: LLM provider to use
        model: LLM model to use
        
    Returns:
        True if successful, False otherwise
    """
    agent_config = get_agent_config(agent_id)
    
    if "llm" not in agent_config:
        agent_config["llm"] = {}
    
    if provider is not None:
        agent_config["llm"]["provider"] = provider
    
    if model is not None:
        agent_config["llm"]["model"] = model
    
    return set_agent_config(agent_id, agent_config)


def get_all_agent_configs() -> Dict[str, Dict[str, Any]]:
    """
    Get configurations for all agents.
    
    Returns:
        Dictionary of agent_id -> agent_config
    """
    agent_configs = load_agent_configs()
    return agent_configs["agents"]


def delete_agent_config(agent_id: str) -> bool:
    """
    Delete configuration for a specific agent.
    
    Args:
        agent_id: ID of the agent
        
    Returns:
        True if successful, False otherwise
    """
    agent_configs = load_agent_configs()
    
    if agent_id in agent_configs["agents"]:
        del agent_configs["agents"][agent_id]
        return save_agent_configs(agent_configs)
    
    return True  # Agent not found, so technically it's deleted
