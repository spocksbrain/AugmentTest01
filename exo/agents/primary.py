"""
Primary Interface & Management Agent (PIA) implementation
"""

import logging
import uuid
from typing import Dict, List, Optional, Any

from exo.ui.animated_dot import AnimatedDot
from exo.ui.chat_window import ChatWindow
from exo.desktop.context import DesktopContext

logger = logging.getLogger(__name__)

class PrimaryInterfaceAgent:
    """
    Primary Interface & Management Agent (PIA)

    The PIA serves as the user's primary point of contact with the entire system.
    It manages the UI, processes user input, and delegates tasks to other agents.
    """

    def __init__(self, cnc_agent=None):
        """
        Initialize the Primary Interface Agent.

        Args:
            cnc_agent: The Command & Control Agent
        """
        self.wake_word = "exo"
        self.voice_mode_active = False
        self.ui_elements = {
            "animated_dot": AnimatedDot(),
            "chat_window": ChatWindow()
        }
        self.cnc_agent = cnc_agent
        self.domain_agents = {}
        self.conversation_history = []
        self.desktop_context = DesktopContext()

        # Agent properties
        self.name = "Primary Interface Agent"
        self.agent_type = "pia"
        self.agent_id = "pia_agent"
        self.llm_provider = None
        self.llm_model = None

        logger.info("Primary Interface Agent initialized")

    def process_user_input(self, input_data: str, input_type: str = "text") -> str:
        """
        Process user input (text, voice, or multimodal).

        Args:
            input_data: The user input data
            input_type: The type of input (text, voice, multimodal)

        Returns:
            The system response
        """
        logger.info(f"Processing user input: {input_data[:50]}... (type: {input_type})")

        # Add to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": input_data,
            "type": input_type,
            "timestamp": uuid.uuid4().hex
        })

        # Capture desktop context if needed
        if "screenshot" in input_data.lower() or "screen" in input_data.lower():
            self.capture_desktop_context()

        # Determine if this is a simple task or needs delegation
        if self._is_complex_task(input_data):
            response = self.delegate_to_cnc(input_data)
        else:
            # Check if this is a domain-specific task
            domain = self._identify_domain(input_data)
            if domain and domain in self.domain_agents:
                response = self.delegate_to_domain_agent(domain, input_data)
            else:
                # Handle directly
                response = self._generate_direct_response(input_data)

        # Add response to conversation history
        self.conversation_history.append({
            "role": "assistant",
            "content": response,
            "timestamp": uuid.uuid4().hex
        })

        return response

    def _is_complex_task(self, task: str) -> bool:
        """
        Determine if a task is complex and requires multiple domain agents.

        Args:
            task: The task description

        Returns:
            True if the task is complex, False otherwise
        """
        # This is a placeholder implementation
        # In a real system, this would use NLP to analyze the task
        complex_indicators = [
            "and then",
            "followed by",
            "multiple",
            "complex",
            "series of",
            "pipeline"
        ]
        return any(indicator in task.lower() for indicator in complex_indicators)

    def _identify_domain(self, task: str) -> Optional[str]:
        """
        Identify the domain for a task.

        Args:
            task: The task description

        Returns:
            The domain name or None if no specific domain is identified
        """
        # Convert task to lowercase for case-insensitive matching
        task_lower = task.lower()

        # Check for web search queries
        web_search_indicators = [
            "search for", "find information", "look up", "search the web",
            "search online", "find out about", "what is", "who is",
            "when did", "where is", "how to", "why does"
        ]

        if any(indicator in task_lower for indicator in web_search_indicators):
            return "brave_search"

        # Check for filesystem operations
        filesystem_indicators = [
            "file", "directory", "folder", "create file", "read file",
            "write file", "delete file", "list files", "find files"
        ]

        if any(indicator in task_lower for indicator in filesystem_indicators):
            return "filesystem"

        # Check for software engineering tasks
        software_engineering_indicators = [
            "code", "program", "develop", "bug", "function", "class",
            "method", "variable", "algorithm", "debug", "refactor",
            "optimize", "implement", "software", "application", "app"
        ]

        if any(indicator in task_lower for indicator in software_engineering_indicators):
            return "software_engineering"

        # Check for MCP server tasks
        mcp_server_indicators = [
            "mcp", "server", "api", "endpoint", "protocol", "service",
            "integration", "connect", "interface", "data source"
        ]

        if any(indicator in task_lower for indicator in mcp_server_indicators):
            return "mcp_server"

        # No specific domain identified
        return None

    def _generate_direct_response(self, input_data: str) -> str:
        """
        Generate a direct response for simple queries using the LLM.

        Args:
            input_data: The user input

        Returns:
            The generated response
        """
        from exo.core.service_registry import get_service, ServiceNames
        from exo.core.system_prompts import get_system_prompt

        # Get the LLM manager from the service registry
        llm_manager = get_service(ServiceNames.LLM_MANAGER)
        if not llm_manager:
            logger.error("LLM manager service not available")
            return "I'm sorry, I'm having trouble accessing my language model. Please try again later."

        try:
            # Get the system prompt for the PIA
            system_prompt = get_system_prompt("pia")

            # Create a messages array for the chat API
            messages = [
                {"role": "system", "content": system_prompt}
            ]

            # Add conversation history for context (last 5 messages)
            history_limit = 5
            history = self.conversation_history[-history_limit:] if len(self.conversation_history) > 0 else []

            for entry in history:
                messages.append({
                    "role": entry.get("role", "user"),
                    "content": entry.get("content", "")
                })

            # Add the current user input if it's not already in the history
            if not history or history[-1].get("role") != "user" or history[-1].get("content") != input_data:
                messages.append({"role": "user", "content": input_data})

            # Call the LLM
            logger.info(f"Generating response using LLM for input: {input_data[:50]}...")
            success, response = llm_manager.chat(messages)

            if success:
                return response
            else:
                logger.error(f"LLM chat failed: {response}")
                return "I'm sorry, I'm having trouble generating a response. Please try again later."

        except Exception as e:
            logger.error(f"Error generating response with LLM: {e}")
            return "I'm sorry, an error occurred while processing your message."

    def capture_desktop_context(self) -> Dict:
        """
        Capture screenshot or other desktop context.

        Returns:
            A dictionary containing the captured context
        """
        logger.info("Capturing desktop context")
        context = self.desktop_context.capture()
        return context

    def control_desktop(self, action: Dict[str, Any]) -> bool:
        """
        Execute desktop control actions directly.

        Args:
            action: The action to perform

        Returns:
            True if the action was successful, False otherwise
        """
        logger.info(f"Controlling desktop: {action}")
        return self.desktop_context.perform_action(action)

    def delegate_to_cnc(self, task: str) -> str:
        """
        Delegate complex multi-domain tasks to CNC agent.

        Args:
            task: The task description

        Returns:
            The response from the CNC agent
        """
        logger.info(f"Delegating to CNC: {task[:50]}...")
        if self.cnc_agent:
            task_id = self.cnc_agent.handle_complex_task(task)
            return f"I'm working on your request. Task ID: {task_id}"
        else:
            return "I'm sorry, but I can't process complex tasks at the moment."

    def delegate_to_domain_agent(self, domain: str, task: str) -> str:
        """
        Delegate single-domain tasks directly to a specialized agent.

        Args:
            domain: The domain name
            task: The task description

        Returns:
            The response from the domain agent
        """
        logger.info(f"Delegating to domain agent ({domain}): {task[:50]}...")

        # Handle MCP server domains (brave_search, filesystem)
        if domain == "brave_search":
            return self._handle_brave_search(task)
        elif domain == "filesystem":
            return self._handle_filesystem(task)

        # Handle regular domain agents
        if domain in self.domain_agents:
            agent = self.domain_agents[domain]
            return agent.handle_task(task)
        else:
            return f"I don't have a specialized agent for {domain} yet."

    def register_domain_agent(self, domain: str, agent) -> None:
        """
        Register a domain agent with the PIA.

        Args:
            domain: The domain name
            agent: The domain agent instance
        """
        logger.info(f"Registering domain agent: {domain}")
        self.domain_agents[domain] = agent

    def start_ui(self) -> None:
        """Start the UI components."""
        logger.info("Starting UI components")
        self.ui_elements["animated_dot"].start()
        self.ui_elements["chat_window"].start()

    def stop_ui(self) -> None:
        """Stop the UI components."""
        logger.info("Stopping UI components")
        self.ui_elements["animated_dot"].stop()
        self.ui_elements["chat_window"].stop()

    def _handle_filesystem(self, query: str) -> str:
        """
        Handle a filesystem operation using the Filesystem MCP server.

        Args:
            query: The filesystem operation query

        Returns:
            The operation result as a formatted string
        """
        from exo.core.service_registry import get_service, ServiceNames

        logger.info(f"Handling Filesystem operation: {query[:50]}...")

        # Get the MCP manager from the service registry
        mcp_manager = get_service(ServiceNames.MCP_MANAGER)
        if not mcp_manager:
            logger.error("MCP manager service not available")
            return "I'm sorry, I'm having trouble accessing the filesystem. Please try again later."

        try:
            # Determine the type of filesystem operation
            query_lower = query.lower()

            if "list" in query_lower and ("files" in query_lower or "directory" in query_lower or "folder" in query_lower):
                # Extract the directory path from the query
                path = self._extract_path_from_query(query)
                return self._list_files(path, mcp_manager)

            elif "read" in query_lower and "file" in query_lower:
                # Extract the file path from the query
                path = self._extract_path_from_query(query)
                return self._read_file(path, mcp_manager)

            elif ("write" in query_lower or "create" in query_lower) and "file" in query_lower:
                # This is more complex and would require content extraction
                # For now, provide a helpful message
                return "I can help you write or create files. Please specify the file path and content you want to write."

            elif "delete" in query_lower and "file" in query_lower:
                # Extract the file path from the query
                path = self._extract_path_from_query(query)
                return self._delete_file(path, mcp_manager)

            else:
                return "I can help with filesystem operations like listing files, reading files, creating files, and deleting files. Please specify what you'd like to do."

        except Exception as e:
            logger.error(f"Error handling Filesystem operation: {e}")
            return "I'm sorry, an error occurred while processing your filesystem request."

    def _list_files(self, path: str, mcp_manager) -> str:
        """
        List files in a directory using the Filesystem MCP server.

        Args:
            path: The directory path to list
            mcp_manager: The MCP manager service

        Returns:
            The directory contents as a formatted string
        """
        logger.info(f"Listing files in {path}")

        try:
            # Send the list request to the Filesystem MCP server
            success, response = mcp_manager.send_request(
                endpoint="/list",
                method="GET",
                data={"path": path},
                server_id="filesystem"
            )

            if not success or "files" not in response:
                logger.error(f"Error listing files: {response}")
                return f"I'm sorry, I couldn't list the contents of '{path}'."

            # Format the directory contents
            files = response["files"]
            if not files:
                return f"The directory '{path}' is empty."

            # Build the response
            response_text = f"Contents of '{path}':\n\n"
            for file in files:
                name = file.get("name", "Unknown")
                is_directory = file.get("is_directory", False)
                size = file.get("size", 0)

                if is_directory:
                    response_text += f"📁 {name}\n"
                else:
                    response_text += f"📄 {name} ({size} bytes)\n"

            return response_text

        except Exception as e:
            logger.error(f"Error listing files: {e}")
            return f"I'm sorry, an error occurred while listing the contents of '{path}'."

    def _read_file(self, path: str, mcp_manager) -> str:
        """
        Read a file using the Filesystem MCP server.

        Args:
            path: The file path to read
            mcp_manager: The MCP manager service

        Returns:
            The file contents as a formatted string
        """
        logger.info(f"Reading file {path}")

        try:
            # Send the read request to the Filesystem MCP server
            success, response = mcp_manager.send_request(
                endpoint="/read",
                method="GET",
                data={"path": path},
                server_id="filesystem"
            )

            if not success or "content" not in response:
                logger.error(f"Error reading file: {response}")
                return f"I'm sorry, I couldn't read the file '{path}'."

            # Format the file contents
            content = response["content"]
            if not content:
                return f"The file '{path}' is empty."

            # Build the response
            response_text = f"Contents of '{path}':\n\n```\n{content}\n```"

            return response_text

        except Exception as e:
            logger.error(f"Error reading file: {e}")
            return f"I'm sorry, an error occurred while reading the file '{path}'."

    def _delete_file(self, path: str, mcp_manager) -> str:
        """
        Delete a file using the Filesystem MCP server.

        Args:
            path: The file path to delete
            mcp_manager: The MCP manager service

        Returns:
            The result as a formatted string
        """
        logger.info(f"Deleting file {path}")

        try:
            # Send the delete request to the Filesystem MCP server
            success, response = mcp_manager.send_request(
                endpoint="/delete",
                method="DELETE",
                data={"path": path},
                server_id="filesystem"
            )

            if not success or "success" not in response:
                logger.error(f"Error deleting file: {response}")
                return f"I'm sorry, I couldn't delete the file '{path}'."

            # Check if the deletion was successful
            if response["success"]:
                return f"Successfully deleted '{path}'."
            else:
                return f"Failed to delete '{path}'."

        except Exception as e:
            logger.error(f"Error deleting file: {e}")
            return f"I'm sorry, an error occurred while deleting the file '{path}'."

    def _extract_path_from_query(self, query: str) -> str:
        """
        Extract a file or directory path from a query.

        Args:
            query: The query containing a path

        Returns:
            The extracted path, or '.' if no path is found
        """
        # This is a simple implementation that looks for quoted paths or paths with slashes
        import re

        # Try to find a quoted path
        quoted_path_match = re.search(r'["\'](.+?)["\']', query)
        if quoted_path_match:
            return quoted_path_match.group(1)

        # Try to find a path with slashes
        path_match = re.search(r'\b(/(?:home/)?(?:[\w\-\.]+/)*[\w\-\.]+)\b', query)
        if path_match:
            return path_match.group(1)

        # Try to find a single filename or directory name
        name_match = re.search(r'\b(\w+\.\w+)\b', query)  # Look for something like file.txt
        if name_match:
            return name_match.group(1)

        # Default to current directory
        return "."

    def _handle_brave_search(self, query: str) -> str:
        """
        Handle a web search query using the Brave Search MCP server.

        Args:
            query: The search query

        Returns:
            The search results as a formatted string
        """
        from exo.core.service_registry import get_service, ServiceNames

        logger.info(f"Handling Brave Search query: {query[:50]}...")

        # Extract the actual search query from the user's request
        search_terms = query.lower()
        for prefix in ["search for", "find information about", "look up", "search the web for",
                      "search online for", "find out about", "what is", "who is",
                      "when did", "where is", "how to", "why does"]:
            if search_terms.startswith(prefix):
                search_terms = search_terms[len(prefix):].strip()
                break

        # Get the MCP manager from the service registry
        mcp_manager = get_service(ServiceNames.MCP_MANAGER)
        if not mcp_manager:
            logger.error("MCP manager service not available")
            return "I'm sorry, I'm having trouble accessing the search service. Please try again later."

        try:
            # Send the search request to the Brave Search MCP server
            success, response = mcp_manager.send_request(
                endpoint="/search",
                method="GET",
                data={"q": search_terms, "count": 5},
                server_id="brave_search"
            )

            if success and isinstance(response, dict):
                # Format the search results
                results = response.get("results", [])
                if not results:
                    return f"I searched for '{search_terms}' but couldn't find any relevant results."

                formatted_results = f"Here are the search results for '{search_terms}':\n\n"
                for i, result in enumerate(results, 1):
                    title = result.get("title", "No title")
                    url = result.get("url", "#")
                    description = result.get("description", "No description available")
                    formatted_results += f"{i}. **{title}**\n   {description}\n   [Link]({url})\n\n"

                return formatted_results
            else:
                logger.error(f"Brave Search MCP request failed: {response}")
                return f"I tried to search for '{search_terms}' but encountered an error. Please try again later."

        except Exception as e:
            logger.error(f"Error handling Brave Search query: {e}")
            return "I'm sorry, an error occurred while processing your search request."
