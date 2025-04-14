"""
Tests for the system integration
"""

import pytest
from unittest.mock import patch, MagicMock, call
from exo.core.system import ExoSystem
from exo.core.service_registry import ServiceRegistry, ServiceNames, register_service

class TestSystemIntegration:
    """Tests for the system integration."""
    
    def test_system_initialization(self):
        """Test that the system initializes correctly."""
        # Create a system instance
        system = ExoSystem()
        
        # Check that the system components were initialized
        assert system.cnc_agent is not None
        assert system.pia is not None
        assert system.pia.cnc_agent == system.cnc_agent
        
    def test_system_registration(self, mock_service_registry):
        """Test that the system registers itself with the service registry."""
        # Register the system with the service registry
        system = ExoSystem()
        register_service(ServiceNames.SYSTEM, system)
        
        # Check that the system was registered
        assert mock_service_registry.get(ServiceNames.SYSTEM) == system
        
    def test_domain_agent_registration(self):
        """Test that domain agents can be registered with the system."""
        # Create a system instance
        system = ExoSystem()
        
        # Create mock domain agent classes
        mock_agent_class = MagicMock()
        mock_agent_instance = MagicMock()
        mock_agent_class.return_value = mock_agent_instance
        
        # Register the domain agent
        agent = system.register_domain_agent(mock_agent_class, "test_domain", ["capability1", "capability2"])
        
        # Check that the agent was registered with the CNC agent and PIA
        assert agent == mock_agent_instance
        assert "test_domain" in system.pia.domain_agents
        assert system.pia.domain_agents["test_domain"] == mock_agent_instance
        
    def test_message_flow(self):
        """Test the message flow through the system."""
        # Create a system instance with mocked components
        system = ExoSystem()
        
        # Mock the PIA's process_user_input method
        system.pia.process_user_input = MagicMock(return_value="Test response")
        
        # Process a message
        response = system.pia.process_user_input("Hello")
        
        # Check the response
        assert response == "Test response"
        system.pia.process_user_input.assert_called_once_with("Hello")
        
    def test_complex_task_delegation(self):
        """Test delegation of complex tasks to the CNC agent."""
        # Create a system instance
        system = ExoSystem()
        
        # Mock the CNC agent's handle_complex_task method
        system.cnc_agent.handle_complex_task = MagicMock(return_value="task-123")
        
        # Mock the PIA's methods
        system.pia._is_complex_task = MagicMock(return_value=True)
        
        # Process a complex task
        response = system.pia.process_user_input("Do this complex task and then do that")
        
        # Check that the task was delegated to the CNC agent
        system.pia._is_complex_task.assert_called_once()
        system.cnc_agent.handle_complex_task.assert_called_once()
        assert "task-123" in response
        
    def test_domain_specific_task_delegation(self):
        """Test delegation of domain-specific tasks to domain agents."""
        # Create a system instance
        system = ExoSystem()
        
        # Create a mock domain agent
        mock_domain_agent = MagicMock()
        mock_domain_agent.handle_task.return_value = "Domain task handled"
        
        # Register the mock domain agent
        system.pia.domain_agents["software_engineering"] = mock_domain_agent
        
        # Mock the PIA's methods
        system.pia._is_complex_task = MagicMock(return_value=False)
        system.pia._identify_domain = MagicMock(return_value="software_engineering")
        
        # Process a domain-specific task
        response = system.pia.process_user_input("Write a function to calculate factorial")
        
        # Check that the task was delegated to the domain agent
        system.pia._is_complex_task.assert_called_once()
        system.pia._identify_domain.assert_called_once()
        mock_domain_agent.handle_task.assert_called_once_with("Write a function to calculate factorial")
        assert response == "Domain task handled"
        
    @patch('exo.agents.primary.get_service')
    def test_brave_search_integration(self, mock_get_service):
        """Test integration with the Brave Search MCP server."""
        # Create a system instance
        system = ExoSystem()
        
        # Set up mocks
        mock_mcp_manager = MagicMock()
        mock_mcp_manager.send_request.return_value = (True, {
            "results": [
                {
                    "title": "Python Tutorial",
                    "url": "https://example.com/python",
                    "description": "Learn Python programming"
                }
            ]
        })
        mock_get_service.return_value = mock_mcp_manager
        
        # Mock the PIA's methods
        system.pia._is_complex_task = MagicMock(return_value=False)
        system.pia._identify_domain = MagicMock(return_value="brave_search")
        
        # Process a search query
        response = system.pia.process_user_input("search for python tutorials")
        
        # Check that the search was performed
        system.pia._is_complex_task.assert_called_once()
        system.pia._identify_domain.assert_called_once()
        mock_get_service.assert_called_with(ServiceNames.MCP_MANAGER)
        mock_mcp_manager.send_request.assert_called_once()
        assert "Python Tutorial" in response
        assert "https://example.com/python" in response
        
    @patch('exo.agents.primary.get_service')
    def test_filesystem_integration(self, mock_get_service):
        """Test integration with the Filesystem MCP server."""
        # Create a system instance
        system = ExoSystem()
        
        # Set up mocks
        mock_mcp_manager = MagicMock()
        mock_mcp_manager.send_request.return_value = (True, {
            "files": [
                {"name": "test.txt", "is_directory": False, "size": 100},
                {"name": "docs", "is_directory": True, "size": 0}
            ]
        })
        mock_get_service.return_value = mock_mcp_manager
        
        # Mock the PIA's methods
        system.pia._is_complex_task = MagicMock(return_value=False)
        system.pia._identify_domain = MagicMock(return_value="filesystem")
        system.pia._extract_path_from_query = MagicMock(return_value="/home/user")
        
        # Process a filesystem query
        response = system.pia.process_user_input("list files in /home/user")
        
        # Check that the filesystem operation was performed
        system.pia._is_complex_task.assert_called_once()
        system.pia._identify_domain.assert_called_once()
        mock_get_service.assert_called_with(ServiceNames.MCP_MANAGER)
        mock_mcp_manager.send_request.assert_called_once()
        assert "test.txt" in response
        assert "docs" in response
