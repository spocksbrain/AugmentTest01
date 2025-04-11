"""
Tests for the base agent module
"""

import pytest
from unittest.mock import patch, MagicMock
from exo.agents.base_agent import BaseAgent
from exo.core.service_registry import ServiceNames

class TestBaseAgent:
    """Tests for the BaseAgent class."""
    
    def test_init(self):
        """Test initialization of the BaseAgent class."""
        agent = BaseAgent("Test Agent", "test_agent", "openai", "gpt-3.5-turbo")
        
        # Check that the agent properties were set
        assert agent.name == "Test Agent"
        assert agent.agent_type == "test_agent"
        assert agent.llm_provider == "openai"
        assert agent.llm_model == "gpt-3.5-turbo"
    
    def test_mcp_manager_property(self, mock_service_registry):
        """Test the mcp_manager property."""
        agent = BaseAgent("Test Agent", "test_agent")
        
        # Get the MCP manager
        mcp_manager = agent.mcp_manager
        
        # Check that the MCP manager was retrieved from the service registry
        assert mcp_manager is not None
        assert mcp_manager is mock_service_registry.get(ServiceNames.MCP_MANAGER)
    
    def test_llm_manager_property(self, mock_service_registry):
        """Test the llm_manager property."""
        agent = BaseAgent("Test Agent", "test_agent")
        
        # Get the LLM manager
        llm_manager = agent.llm_manager
        
        # Check that the LLM manager was retrieved from the service registry
        assert llm_manager is not None
        assert llm_manager is mock_service_registry.get(ServiceNames.LLM_MANAGER)
    
    def test_system_property(self, mock_service_registry):
        """Test the system property."""
        # Add a mock system to the service registry
        mock_system = MagicMock()
        mock_service_registry.register(ServiceNames.SYSTEM, mock_system)
        
        agent = BaseAgent("Test Agent", "test_agent")
        
        # Get the system
        system = agent.system
        
        # Check that the system was retrieved from the service registry
        assert system is not None
        assert system is mock_system
    
    @patch('exo.agents.base_agent.get_service')
    def test_send_mcp_request(self, mock_get_service):
        """Test sending an MCP request."""
        # Set up the mock MCP manager
        mock_mcp_manager = MagicMock()
        mock_mcp_manager.send_request.return_value = (True, {"result": "success"})
        mock_get_service.return_value = mock_mcp_manager
        
        agent = BaseAgent("Test Agent", "test_agent")
        
        # Send an MCP request
        success, response = agent.send_mcp_request("/test/endpoint", {"param": "value"})
        
        # Check the result
        assert success is True
        assert response == {"result": "success"}
        
        # Check that the MCP manager was called
        mock_mcp_manager.send_request.assert_called_once_with(
            "/test/endpoint", 
            {"param": "value"}, 
            server_id=None
        )
    
    @patch('exo.agents.base_agent.get_service')
    def test_generate_text(self, mock_get_service):
        """Test generating text."""
        # Set up the mock LLM manager
        mock_llm_manager = MagicMock()
        mock_llm_manager.generate.return_value = (True, "Generated text")
        mock_get_service.return_value = mock_llm_manager
        
        agent = BaseAgent("Test Agent", "test_agent", "openai", "gpt-3.5-turbo")
        
        # Generate text
        success, text = agent.generate_text("Test prompt")
        
        # Check the result
        assert success is True
        assert text == "Generated text"
        
        # Check that the LLM manager was called with the agent's provider and model
        mock_llm_manager.generate.assert_called_once_with(
            "Test prompt", 
            provider="openai", 
            model="gpt-3.5-turbo"
        )
    
    @patch('exo.agents.base_agent.get_service')
    def test_chat(self, mock_get_service):
        """Test chatting."""
        # Set up the mock LLM manager
        mock_llm_manager = MagicMock()
        mock_llm_manager.chat.return_value = (True, "Chat response")
        mock_get_service.return_value = mock_llm_manager
        
        agent = BaseAgent("Test Agent", "test_agent", "openai", "gpt-3.5-turbo")
        
        # Chat
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello, how are you?"}
        ]
        success, response = agent.chat(messages)
        
        # Check the result
        assert success is True
        assert response == "Chat response"
        
        # Check that the LLM manager was called with the agent's provider and model
        mock_llm_manager.chat.assert_called_once_with(
            messages, 
            provider="openai", 
            model="gpt-3.5-turbo"
        )
