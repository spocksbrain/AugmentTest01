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
        # This is a placeholder implementation
        # In a real system, this would use NLP to analyze the task
        domain_keywords = {
            "software_engineering": ["code", "program", "develop", "bug", "function"],
            "mcp_server": ["mcp", "server", "api", "endpoint", "protocol"]
        }

        for domain, keywords in domain_keywords.items():
            if any(keyword in task.lower() for keyword in keywords):
                return domain

        return None

    def _generate_direct_response(self, input_data: str) -> str:
        """
        Generate a direct response for simple queries.

        Args:
            input_data: The user input

        Returns:
            The generated response
        """
        # This is a placeholder implementation
        # In a real system, this would use an LLM to generate responses
        if "hello" in input_data.lower() or "hi" in input_data.lower():
            return "Hello! I'm exo, your personal assistant. How can I help you today?"
        elif "help" in input_data.lower():
            return "I can help with various tasks including software development, creating MCP servers, and more. Just let me know what you need!"
        else:
            return "I understand you're asking about something, but I'm not sure how to help with that specific request yet. Could you provide more details or ask in a different way?"

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
