"""
Tests for MCP server integration
"""

import pytest
from unittest.mock import patch, MagicMock, call
from exo.core.mcp_server_manager import MCPServerManager
from exo.agents.mcp_manager import MCPManager
from exo.core.service_registry import ServiceNames, register_service

class TestMCPIntegration:
    """Tests for MCP server integration."""
    
    def test_mcp_server_manager_initialization(self):
        """Test that the MCP server manager initializes correctly."""
        # Create an MCP server manager instance
        manager = MCPServerManager()
        
        # Check that the manager was initialized
        assert isinstance(manager.local_servers, dict)
        
    @patch('exo.core.mcp_server_manager.ConfigurationService')
    def test_initialize_servers(self, mock_config_service):
        """Test initialization of MCP servers."""
        # Set up mock configuration
        mock_config_service.load_mcp_servers.return_value = [
            {
                "id": "filesystem",
                "name": "Filesystem MCP Server",
                "url": "http://localhost:8090",
                "local": True,
                "default": True
            },
            {
                "id": "brave_search",
                "name": "Brave Search MCP Server",
                "url": "https://mcp.brave.com",
                "local": False,
                "default": True
            }
        ]
        
        # Create an MCP server manager instance
        manager = MCPServerManager()
        
        # Mock the ensure_local_server_running method
        manager.ensure_local_server_running = MagicMock()
        
        # Initialize servers
        manager.initialize_servers()
        
        # Check that local default servers were started
        mock_config_service.load_mcp_servers.assert_called_once()
        manager.ensure_local_server_running.assert_called_once()
        
        # Check that the filesystem server was started
        filesystem_server = mock_config_service.load_mcp_servers.return_value[0]
        manager.ensure_local_server_running.assert_called_with(filesystem_server)
        
    @patch('exo.agents.mcp_manager.requests')
    def test_mcp_manager_send_request(self, mock_requests):
        """Test sending requests through the MCP manager."""
        # Set up mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": "success"}
        mock_requests.request.return_value = mock_response
        
        # Create an MCP manager instance
        mock_onboarding = MagicMock()
        mock_onboarding.list_mcp_servers.return_value = [
            {
                "id": "brave_search",
                "name": "Brave Search MCP Server",
                "url": "https://mcp.brave.com",
                "api_key": "test_key"
            }
        ]
        
        manager = MCPManager(onboarding=mock_onboarding)
        
        # Send a request
        success, response = manager.send_request(
            endpoint="/search",
            method="GET",
            data={"q": "python tutorials"},
            server_id="brave_search"
        )
        
        # Check the result
        assert success is True
        assert response == {"result": "success"}
        
        # Check that the request was sent correctly
        mock_requests.request.assert_called_once()
        call_args = mock_requests.request.call_args[1]
        assert call_args["method"] == "GET"
        assert call_args["url"] == "https://mcp.brave.com/search"
        assert "q=python+tutorials" in call_args["params"]
        assert call_args["headers"]["Authorization"] == "Bearer test_key"
        
    def test_mcp_manager_registration(self, mock_service_registry):
        """Test that the MCP manager registers itself with the service registry."""
        # Create an MCP manager instance
        manager = MCPManager()
        
        # Register the manager with the service registry
        register_service(ServiceNames.MCP_MANAGER, manager)
        
        # Check that the manager was registered
        assert mock_service_registry.get(ServiceNames.MCP_MANAGER) == manager
        
    @patch('exo.agents.primary.get_service')
    def test_brave_search_mcp_integration(self, mock_get_service):
        """Test integration with the Brave Search MCP server from the PIA."""
        from exo.agents.primary import PrimaryInterfaceAgent
        
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
        
        # Create a PIA instance
        agent = PrimaryInterfaceAgent()
        
        # Handle a search query
        response = agent._handle_brave_search("search for python tutorials")
        
        # Check the response
        assert "Here are the search results for 'python tutorials'" in response
        assert "Python Tutorial" in response
        assert "Learn Python programming" in response
        
        # Check that the appropriate methods were called
        mock_get_service.assert_called_once_with(ServiceNames.MCP_MANAGER)
        mock_mcp_manager.send_request.assert_called_once_with(
            endpoint="/search",
            method="GET",
            data={"q": "python tutorials", "count": 5},
            server_id="brave_search"
        )
        
    @patch('exo.agents.primary.get_service')
    def test_filesystem_mcp_integration(self, mock_get_service):
        """Test integration with the Filesystem MCP server from the PIA."""
        from exo.agents.primary import PrimaryInterfaceAgent
        
        # Set up mocks
        mock_mcp_manager = MagicMock()
        mock_mcp_manager.send_request.return_value = (True, {
            "files": [
                {"name": "test.txt", "is_directory": False, "size": 100},
                {"name": "docs", "is_directory": True, "size": 0}
            ]
        })
        mock_get_service.return_value = mock_mcp_manager
        
        # Create a PIA instance
        agent = PrimaryInterfaceAgent()
        
        # Mock the path extraction
        agent._extract_path_from_query = MagicMock(return_value="/home/user")
        
        # Handle a filesystem query
        response = agent._handle_filesystem("list files in /home/user")
        
        # Check the response
        assert "Contents of '/home/user'" in response
        assert "test.txt" in response
        assert "docs" in response
        
        # Check that the appropriate methods were called
        mock_get_service.assert_called_once_with(ServiceNames.MCP_MANAGER)
        agent._extract_path_from_query.assert_called_once_with("list files in /home/user")
        mock_mcp_manager.send_request.assert_called_once()
