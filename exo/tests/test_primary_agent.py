"""
Tests for the Primary Interface Agent
"""

import pytest
import re
from unittest.mock import patch, MagicMock, call
from exo.agents.primary import PrimaryInterfaceAgent
from exo.core.service_registry import ServiceNames

class TestPrimaryInterfaceAgent:
    """Tests for the PrimaryInterfaceAgent class."""
    
    def test_init(self):
        """Test initialization of the PrimaryInterfaceAgent class."""
        mock_cnc = MagicMock()
        agent = PrimaryInterfaceAgent(cnc_agent=mock_cnc)
        
        # Check that the agent properties were set correctly
        assert agent.name == "Primary Interface Agent"
        assert agent.agent_type == "pia"
        assert agent.wake_word == "exo"
        assert agent.cnc_agent == mock_cnc
        assert isinstance(agent.domain_agents, dict)
        assert isinstance(agent.conversation_history, list)
        
    def test_process_user_input(self):
        """Test processing user input."""
        # Create a PIA with mocked methods
        agent = PrimaryInterfaceAgent()
        agent._is_complex_task = MagicMock(return_value=False)
        agent._identify_domain = MagicMock(return_value=None)
        agent._generate_direct_response = MagicMock(return_value="Test response")
        
        # Process a simple input
        response = agent.process_user_input("Hello")
        
        # Check that the conversation history was updated
        assert len(agent.conversation_history) == 2
        assert agent.conversation_history[0]["role"] == "user"
        assert agent.conversation_history[0]["content"] == "Hello"
        assert agent.conversation_history[1]["role"] == "assistant"
        assert agent.conversation_history[1]["content"] == "Test response"
        
        # Check that the appropriate methods were called
        agent._is_complex_task.assert_called_once_with("Hello")
        agent._identify_domain.assert_called_once_with("Hello")
        agent._generate_direct_response.assert_called_once_with("Hello")
        
    def test_process_user_input_complex_task(self):
        """Test processing a complex user input."""
        # Create a PIA with mocked methods
        mock_cnc = MagicMock()
        agent = PrimaryInterfaceAgent(cnc_agent=mock_cnc)
        agent._is_complex_task = MagicMock(return_value=True)
        agent.delegate_to_cnc = MagicMock(return_value="Complex task response")
        
        # Process a complex input
        response = agent.process_user_input("Do this complex task and then do that")
        
        # Check the response
        assert response == "Complex task response"
        
        # Check that the appropriate methods were called
        agent._is_complex_task.assert_called_once()
        agent.delegate_to_cnc.assert_called_once()
        
    def test_process_user_input_domain_specific(self):
        """Test processing a domain-specific user input."""
        # Create a PIA with mocked methods
        agent = PrimaryInterfaceAgent()
        agent._is_complex_task = MagicMock(return_value=False)
        agent._identify_domain = MagicMock(return_value="software_engineering")
        agent.delegate_to_domain_agent = MagicMock(return_value="Domain response")
        
        # Add a mock domain agent
        mock_domain_agent = MagicMock()
        agent.domain_agents["software_engineering"] = mock_domain_agent
        
        # Process a domain-specific input
        response = agent.process_user_input("Write a function to calculate factorial")
        
        # Check the response
        assert response == "Domain response"
        
        # Check that the appropriate methods were called
        agent._is_complex_task.assert_called_once()
        agent._identify_domain.assert_called_once()
        agent.delegate_to_domain_agent.assert_called_once_with("software_engineering", "Write a function to calculate factorial")
        
    def test_is_complex_task(self):
        """Test the _is_complex_task method."""
        agent = PrimaryInterfaceAgent()
        
        # Test with complex tasks
        assert agent._is_complex_task("Do this and then do that") is True
        assert agent._is_complex_task("This is a complex task") is True
        assert agent._is_complex_task("Perform a series of operations") is True
        
        # Test with simple tasks
        assert agent._is_complex_task("Hello") is False
        assert agent._is_complex_task("What time is it?") is False
        
    def test_identify_domain(self):
        """Test the _identify_domain method."""
        agent = PrimaryInterfaceAgent()
        
        # Test web search domain
        assert agent._identify_domain("search for python tutorials") == "brave_search"
        assert agent._identify_domain("what is machine learning") == "brave_search"
        assert agent._identify_domain("find information about climate change") == "brave_search"
        
        # Test filesystem domain
        assert agent._identify_domain("list files in the directory") == "filesystem"
        assert agent._identify_domain("read the file test.txt") == "filesystem"
        assert agent._identify_domain("create a new file") == "filesystem"
        
        # Test software engineering domain
        assert agent._identify_domain("write a function to calculate factorial") == "software_engineering"
        assert agent._identify_domain("debug this code") == "software_engineering"
        assert agent._identify_domain("optimize this algorithm") == "software_engineering"
        
        # Test MCP server domain
        assert agent._identify_domain("create an MCP server") == "mcp_server"
        assert agent._identify_domain("configure the API endpoint") == "mcp_server"
        assert agent._identify_domain("set up a new data source") == "mcp_server"
        
        # Test with no specific domain
        assert agent._identify_domain("Hello") is None
        assert agent._identify_domain("How are you?") is None
        
    @patch('exo.agents.primary.get_service')
    @patch('exo.agents.primary.get_system_prompt')
    def test_generate_direct_response(self, mock_get_system_prompt, mock_get_service):
        """Test the _generate_direct_response method."""
        # Set up mocks
        mock_llm_manager = MagicMock()
        mock_llm_manager.chat.return_value = (True, "Test LLM response")
        mock_get_service.return_value = mock_llm_manager
        mock_get_system_prompt.return_value = "You are a helpful assistant."
        
        # Create a PIA
        agent = PrimaryInterfaceAgent()
        
        # Add some conversation history
        agent.conversation_history = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"}
        ]
        
        # Generate a response
        response = agent._generate_direct_response("How are you?")
        
        # Check the response
        assert response == "Test LLM response"
        
        # Check that the appropriate methods were called
        mock_get_service.assert_called_once_with(ServiceNames.LLM_MANAGER)
        mock_get_system_prompt.assert_called_once_with("pia")
        mock_llm_manager.chat.assert_called_once()
        
        # Check that the messages were constructed correctly
        messages_arg = mock_llm_manager.chat.call_args[0][0]
        assert messages_arg[0]["role"] == "system"
        assert messages_arg[0]["content"] == "You are a helpful assistant."
        assert messages_arg[1]["role"] == "user"
        assert messages_arg[1]["content"] == "Hello"
        assert messages_arg[2]["role"] == "assistant"
        assert messages_arg[2]["content"] == "Hi there!"
        assert messages_arg[3]["role"] == "user"
        assert messages_arg[3]["content"] == "How are you?"
        
    def test_delegate_to_domain_agent(self):
        """Test the delegate_to_domain_agent method."""
        # Create a PIA
        agent = PrimaryInterfaceAgent()
        
        # Add mock domain agents
        mock_software_agent = MagicMock()
        mock_software_agent.handle_task.return_value = "Software task handled"
        agent.domain_agents["software_engineering"] = mock_software_agent
        
        # Mock MCP server handlers
        agent._handle_brave_search = MagicMock(return_value="Search results")
        agent._handle_filesystem = MagicMock(return_value="Filesystem operation result")
        
        # Test delegation to a regular domain agent
        response = agent.delegate_to_domain_agent("software_engineering", "Write a function")
        assert response == "Software task handled"
        mock_software_agent.handle_task.assert_called_once_with("Write a function")
        
        # Test delegation to Brave Search MCP
        response = agent.delegate_to_domain_agent("brave_search", "Search for python")
        assert response == "Search results"
        agent._handle_brave_search.assert_called_once_with("Search for python")
        
        # Test delegation to Filesystem MCP
        response = agent.delegate_to_domain_agent("filesystem", "List files")
        assert response == "Filesystem operation result"
        agent._handle_filesystem.assert_called_once_with("List files")
        
        # Test delegation to unknown domain
        response = agent.delegate_to_domain_agent("unknown_domain", "Do something")
        assert "I don't have a specialized agent for unknown_domain" in response
        
    @patch('exo.agents.primary.get_service')
    def test_handle_brave_search(self, mock_get_service):
        """Test the _handle_brave_search method."""
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
        
        # Create a PIA
        agent = PrimaryInterfaceAgent()
        
        # Handle a search query
        response = agent._handle_brave_search("search for python tutorials")
        
        # Check the response
        assert "Here are the search results for 'python tutorials'" in response
        assert "Python Tutorial" in response
        assert "Learn Python programming" in response
        assert "https://example.com/python" in response
        
        # Check that the appropriate methods were called
        mock_get_service.assert_called_once_with(ServiceNames.MCP_MANAGER)
        mock_mcp_manager.send_request.assert_called_once_with(
            endpoint="/search",
            method="GET",
            data={"q": "python tutorials", "count": 5},
            server_id="brave_search"
        )
        
    def test_extract_path_from_query(self):
        """Test the _extract_path_from_query method."""
        agent = PrimaryInterfaceAgent()
        
        # Test with quoted paths
        assert agent._extract_path_from_query('read the file "test.txt"') == "test.txt"
        assert agent._extract_path_from_query("list files in '/home/user'") == "/home/user"
        
        # Test with paths containing slashes
        assert agent._extract_path_from_query("read /home/user/test.txt") == "/home/user/test.txt"
        assert agent._extract_path_from_query("check the file in src/main/app.py") == "src/main/app.py"
        
        # Test with simple filenames
        assert agent._extract_path_from_query("read test.txt") == "test.txt"
        
        # Test with no path
        assert agent._extract_path_from_query("list all files") == "."
        
    @patch('exo.agents.primary.get_service')
    def test_list_files(self, mock_get_service):
        """Test the _list_files method."""
        # Set up mocks
        mock_mcp_manager = MagicMock()
        mock_mcp_manager.send_request.return_value = (True, {
            "files": [
                {"name": "test.txt", "is_directory": False, "size": 100},
                {"name": "docs", "is_directory": True, "size": 0}
            ]
        })
        
        # Create a PIA
        agent = PrimaryInterfaceAgent()
        
        # List files
        response = agent._list_files("/home/user", mock_mcp_manager)
        
        # Check the response
        assert "Contents of '/home/user'" in response
        assert "📄 test.txt (100 bytes)" in response
        assert "📁 docs" in response
        
        # Check that the appropriate methods were called
        mock_mcp_manager.send_request.assert_called_once_with(
            endpoint="/list",
            method="GET",
            data={"path": "/home/user"},
            server_id="filesystem"
        )
        
    @patch('exo.agents.primary.get_service')
    def test_read_file(self, mock_get_service):
        """Test the _read_file method."""
        # Set up mocks
        mock_mcp_manager = MagicMock()
        mock_mcp_manager.send_request.return_value = (True, {
            "content": "This is the content of the file."
        })
        
        # Create a PIA
        agent = PrimaryInterfaceAgent()
        
        # Read a file
        response = agent._read_file("test.txt", mock_mcp_manager)
        
        # Check the response
        assert "Contents of 'test.txt'" in response
        assert "This is the content of the file." in response
        
        # Check that the appropriate methods were called
        mock_mcp_manager.send_request.assert_called_once_with(
            endpoint="/read",
            method="GET",
            data={"path": "test.txt"},
            server_id="filesystem"
        )
        
    @patch('exo.agents.primary.get_service')
    def test_delete_file(self, mock_get_service):
        """Test the _delete_file method."""
        # Set up mocks
        mock_mcp_manager = MagicMock()
        mock_mcp_manager.send_request.return_value = (True, {
            "success": True
        })
        
        # Create a PIA
        agent = PrimaryInterfaceAgent()
        
        # Delete a file
        response = agent._delete_file("test.txt", mock_mcp_manager)
        
        # Check the response
        assert "Successfully deleted 'test.txt'" in response
        
        # Check that the appropriate methods were called
        mock_mcp_manager.send_request.assert_called_once_with(
            endpoint="/delete",
            method="DELETE",
            data={"path": "test.txt"},
            server_id="filesystem"
        )
