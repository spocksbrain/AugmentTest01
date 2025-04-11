"""
Test the MCP Server Agent discovery functionality
"""

import unittest
from unittest.mock import patch, MagicMock
import json

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from exo.agents.mcp_server import MCPServerAgent


class TestMCPServerDiscovery(unittest.TestCase):
    """Test the MCP Server Agent discovery functionality."""

    def setUp(self):
        """Set up the test environment."""
        self.agent = MCPServerAgent()

    def test_determine_task_type_discovery(self):
        """Test that discovery-related tasks are correctly identified."""
        # Test discovery-related tasks
        discovery_tasks = [
            "Find existing MCP server solutions",
            "What MCP servers are available?",
            "Search for MCP servers for GitHub",
            "Discover MCP server options for file system access",
            "What are the alternatives to building a custom MCP server?",
            "Show me available MCP server solutions"
        ]

        for task in discovery_tasks:
            task_type = self.agent._determine_task_type(task)
            self.assertEqual(task_type, "mcp_server_discovery", f"Failed for task: {task}")

        # Test non-discovery tasks
        non_discovery_tasks = [
            "Build a custom MCP server",
            "Create documentation for my MCP server",
            "Implement security for my MCP server"
        ]

        for task in non_discovery_tasks:
            task_type = self.agent._determine_task_type(task)
            self.assertNotEqual(task_type, "mcp_server_discovery", f"Failed for task: {task}")

    @patch('requests.get')
    @patch('exo.core.service_registry.get_service')
    def test_discover_mcp_servers(self, mock_get_service, mock_requests_get):
        """Test the discovery of MCP servers."""
        # Mock the MCP Manager service
        mock_get_service.return_value = MagicMock()

        # Mock the response from the official repository
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "new-server": {
                "name": "New MCP Server",
                "description": "A new MCP server for testing",
                "repository": "https://github.com/example/new-server",
                "features": ["Feature 1", "Feature 2"],
                "requirements": ["Requirement 1"],
                "installation": "pip install new-server"
            }
        }
        mock_requests_get.return_value = mock_response

        # Test with a specific task
        result = self.agent._discover_mcp_servers("Find an MCP server for GitHub")

        # Verify the result
        self.assertIn("message", result)
        self.assertIn("servers", result)
        self.assertIn("can_install", result)
        self.assertIn("recommendation", result)

        # Verify that the GitHub server is recommended (should be most relevant)
        github_found = False
        for server in result["servers"]:
            if server["id"] == "github-mcp":
                github_found = True
                break
        self.assertTrue(github_found, "GitHub MCP server not found in results")

        # Test with a generic task
        result = self.agent._discover_mcp_servers("Show me available MCP servers")

        # Verify that all servers are returned
        self.assertGreaterEqual(len(result["servers"]), len(self.agent.known_mcp_servers))

        # Verify that the custom option is always included
        custom_found = False
        for server in result["servers"]:
            if server["id"] == "custom":
                custom_found = True
                break
        self.assertTrue(custom_found, "Custom MCP server option not found in results")

    @patch('requests.get')
    def test_discover_mcp_servers_with_error(self, mock_requests_get):
        """Test the discovery of MCP servers when the request fails."""
        # Mock the response to raise an exception
        mock_requests_get.side_effect = Exception("Connection error")

        # Test with a specific task
        result = self.agent._discover_mcp_servers("Find an MCP server for GitHub")

        # Verify the result still contains the known servers
        self.assertIn("message", result)
        self.assertIn("servers", result)
        self.assertGreaterEqual(len(result["servers"]), len(self.agent.known_mcp_servers))


if __name__ == '__main__':
    unittest.main()
