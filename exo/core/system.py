"""
Core system class for the exo Multi-Agent Framework
"""

import logging
from typing import Dict, Optional

from exo.agents.primary import PrimaryInterfaceAgent
from exo.agents.command_control import CommandControlAgent
from exo.agents.domain import DomainAgent

logger = logging.getLogger(__name__)

class ExoSystem:
    """
    Main system class for the exo Multi-Agent Framework.

    This class initializes and manages all components of the exo system,
    including the Primary Interface Agent, Command & Control Agent,
    and Domain Agents.
    """

    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the exo system.

        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        logger.info("Initializing exo Multi-Agent Framework")

        # Initialize the Command & Control Agent
        self.cnc_agent = CommandControlAgent()

        # Initialize the Primary Interface Agent
        self.pia = PrimaryInterfaceAgent(cnc_agent=self.cnc_agent)

        # List to track all agents in the system
        self.agents = [self.cnc_agent, self.pia]

        # Register initial domain agents
        self._register_initial_domain_agents()

        logger.info("exo system initialized")

    def _register_initial_domain_agents(self):
        """Register the initial set of domain agents with the system."""
        # This will be implemented as we create the domain agents
        pass

    def start(self):
        """Start the exo system."""
        logger.info("Starting exo system")
        # Start the UI
        self.pia.start_ui()
        logger.info("exo system started")

    def stop(self):
        """Stop the exo system."""
        logger.info("Stopping exo system")
        # Cleanup resources
        self.pia.stop_ui()
        logger.info("exo system stopped")

    def register_domain_agent(self, agent_class, domain, capabilities):
        """
        Register a new domain agent with the system.

        Args:
            agent_class: The domain agent class
            domain: The domain name
            capabilities: The agent's capabilities

        Returns:
            The registered domain agent instance
        """
        # Create an instance of the agent class
        # Note: The agent classes already have their domain and capabilities set in their __init__ methods
        agent = agent_class()
        self.cnc_agent.register_domain_agent(domain, agent)
        self.pia.register_domain_agent(domain, agent)

        # Add to the list of all agents
        self.agents.append(agent)

        return agent
