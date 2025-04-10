"""
Base Agent for the exo Multi-Agent Framework

This module provides the base agent class for all agents in the system.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple

from exo.core.service_registry import get_service, ServiceNames

logger = logging.getLogger(__name__)

class BaseAgent:
    """
    Base Agent for the exo Multi-Agent Framework

    This class provides the base functionality for all agents in the system.
    """

    def __init__(self, name: str, agent_type: str,
                 llm_provider: Optional[str] = None,
                 llm_model: Optional[str] = None):
        """
        Initialize the base agent.

        Args:
            name: Name of the agent
            agent_type: Type of the agent
            llm_provider: LLM provider to use (if None, uses default)
            llm_model: LLM model to use (if None, uses default)
        """
        self.name = name
        self.agent_type = agent_type
        self.logger = logging.getLogger(f"{__name__}.{agent_type}.{name}")

        # LLM preferences
        self.llm_provider = llm_provider
        self.llm_model = llm_model

        # Initialize service references
        self._mcp_manager = None
        self._llm_manager = None
        self._system = None

    @property
    def mcp_manager(self):
        """Get the MCP manager service."""
        if self._mcp_manager is None:
            self._mcp_manager = get_service(ServiceNames.MCP_MANAGER)
            if self._mcp_manager is None:
                self.logger.warning("MCP manager service not found")
        return self._mcp_manager

    @property
    def llm_manager(self):
        """Get the LLM manager service."""
        if self._llm_manager is None:
            self._llm_manager = get_service(ServiceNames.LLM_MANAGER)
            if self._llm_manager is None:
                self.logger.warning("LLM manager service not found")
        return self._llm_manager

    @property
    def system(self):
        """Get the system service."""
        if self._system is None:
            self._system = get_service(ServiceNames.SYSTEM)
            if self._system is None:
                self.logger.warning("System service not found")
        return self._system

    def initialize(self) -> bool:
        """
        Initialize the agent.

        Returns:
            True if initialization was successful, False otherwise
        """
        self.logger.info(f"Initializing agent: {self.name} ({self.agent_type})")
        return True

    def shutdown(self) -> bool:
        """
        Shutdown the agent.

        Returns:
            True if shutdown was successful, False otherwise
        """
        self.logger.info(f"Shutting down agent: {self.name} ({self.agent_type})")
        return True

    def process_message(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Process a message.

        Args:
            message: Message to process

        Returns:
            Response message, or None if no response
        """
        self.logger.debug(f"Processing message: {message}")
        return None

    def send_mcp_request(self, endpoint: str, method: str = "GET",
                        data: Optional[Dict[str, Any]] = None,
                        server_id: Optional[str] = None) -> Tuple[bool, Any]:
        """
        Send a request to an MCP server.

        Args:
            endpoint: API endpoint to call
            method: HTTP method to use
            data: Data to send with the request
            server_id: ID of the MCP server to use, or None for default

        Returns:
            Tuple of (success, response_data)
        """
        if self.mcp_manager is None:
            self.logger.error("MCP manager not available")
            return False, {"error": "MCP manager not available"}

        return self.mcp_manager.send_request(endpoint, method, data, server_id)

    def generate_text(self, prompt: str, model: str = None,
                     max_tokens: int = 1000, temperature: float = 0.7,
                     provider: Optional[str] = None) -> Tuple[bool, str]:
        """
        Generate text using a language model.

        Args:
            prompt: Prompt to generate text from
            model: Model to use (if None, uses agent's default or system default)
            max_tokens: Maximum number of tokens to generate
            temperature: Temperature for generation
            provider: Provider to use (if None, uses agent's default or system default)

        Returns:
            Tuple of (success, generated_text)
        """
        if self.llm_manager is None:
            self.logger.error("LLM manager not available")
            return False, "Error: LLM manager not available"

        # Use agent's default provider and model if not specified
        if provider is None:
            provider = self.llm_provider

        if model is None:
            model = self.llm_model

        return self.llm_manager.generate_text(prompt, model, max_tokens, temperature, provider)
