"""
Configuration for pytest
"""

import os
import sys
import pytest
import logging
from unittest.mock import MagicMock

# Add the parent directory to the path so we can import exo modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Configure logging for tests
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

@pytest.fixture
def mock_onboarding():
    """Create a mock onboarding instance."""
    mock = MagicMock()
    # Set up common mock methods
    mock.get_env_var.return_value = "mock_value"
    mock.list_mcp_servers.return_value = {}
    return mock

@pytest.fixture
def mock_llm_manager():
    """Create a mock LLM manager instance."""
    mock = MagicMock()
    # Set up common mock methods
    mock.chat.return_value = (True, "Mock response from LLM")
    mock.generate.return_value = (True, "Mock generated text")
    return mock

@pytest.fixture
def mock_mcp_manager():
    """Create a mock MCP manager instance."""
    mock = MagicMock()
    # Set up common mock methods
    mock.send_request.return_value = (True, {"result": "success"})
    mock.list_servers.return_value = []
    return mock

@pytest.fixture
def mock_service_registry(mock_onboarding, mock_llm_manager, mock_mcp_manager):
    """Create a mock service registry with common services."""
    from exo.core.service_registry import ServiceRegistry, ServiceNames
    
    # Clear the registry singleton for testing
    ServiceRegistry._instance = None
    registry = ServiceRegistry()
    
    # Register mock services
    registry.register(ServiceNames.ONBOARDING, mock_onboarding)
    registry.register(ServiceNames.LLM_MANAGER, mock_llm_manager)
    registry.register(ServiceNames.MCP_MANAGER, mock_mcp_manager)
    
    return registry
