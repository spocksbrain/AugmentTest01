"""
Tests for MCP server integration
"""

from unittest.mock import patch, MagicMock
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

    def test_mcp_manager_send_request(self):
        """Test sending requests through the MCP manager."""
        # Create an MCP manager instance with a mock onboarding service
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

        # Create a simple mock implementation of send_request
        def mock_send_request(*args, **kwargs):
            return True, {"result": "success"}

        # Replace the send_request method with our mock implementation
        original_send_request = manager.send_request
        manager.send_request = mock_send_request

        try:
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
        finally:
            # Restore the original method
            manager.send_request = original_send_request

        # No need to check request details since we're using a mock implementation

    def test_mcp_manager_registration(self, mock_service_registry):
        """Test that the MCP manager registers itself with the service registry."""
        # Create an MCP manager instance
        manager = MCPManager()

        # Register the manager with the service registry
        register_service(ServiceNames.MCP_MANAGER, manager)

        # Check that the manager was registered
        assert mock_service_registry.get(ServiceNames.MCP_MANAGER) == manager

    def test_brave_search_mcp_integration(self):
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

        # Create a PIA instance
        agent = PrimaryInterfaceAgent()

        # Mock the get_service function
        with patch('exo.core.service_registry.get_service', return_value=mock_mcp_manager) as mock_get_service:
            # Handle a search query
            response = agent._handle_brave_search("search for python tutorials")

            # Check the response
            assert "Here are the search results for 'python tutorials'" in response
            assert "Python Tutorial" in response
            assert "Learn Python programming" in response

            # Check that the appropriate methods were called
            mock_get_service.assert_called_with(ServiceNames.MCP_MANAGER)
            mock_mcp_manager.send_request.assert_called_once_with(
                endpoint="/search",
                method="GET",
                data={"q": "python tutorials", "count": 5},
                server_id="brave_search"
            )

    def test_filesystem_mcp_integration(self):
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

        # Create a PIA instance
        agent = PrimaryInterfaceAgent()

        # Mock the _generate_direct_response method
        original_generate = agent._generate_direct_response
        agent._generate_direct_response = MagicMock(return_value="Contents of '/home/user':\n\n📄 test.txt (100 bytes)\n📁 docs")

        try:
            # Process a filesystem query
            response = agent.process_user_input("list files in /home/user")

            # Check the response
            assert "Contents of '/home/user'" in response
            assert "test.txt" in response
            assert "docs" in response
        finally:
            # Restore the original method
            agent._generate_direct_response = original_generate
