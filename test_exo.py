#!/usr/bin/env python3
"""
Simple test script for the exo Multi-Agent Framework
"""

import logging
import sys
from exo.core.system import ExoSystem
from exo.agents.software_engineer import SoftwareEngineerAgent
from exo.agents.mcp_server import MCPServerAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Test the exo system."""
    logger.info("Testing exo Multi-Agent Framework")

    # Initialize the system
    exo_system = ExoSystem()

    # Register domain agents
    logger.info("Registering domain agents")

    # Register Software Engineer Agent
    software_engineer_agent = exo_system.register_domain_agent(
        agent_class=SoftwareEngineerAgent,
        domain="software_engineering",
        capabilities=[]
    )

    # Register MCP Server Agent
    mcp_server_agent = exo_system.register_domain_agent(
        agent_class=MCPServerAgent,
        domain="mcp_server",
        capabilities=[]
    )

    logger.info("Domain agents registered")

    # Start the system
    exo_system.start()

    logger.info("exo system started")

    # Test a simple task with the Software Engineer Agent
    logger.info("Testing Software Engineer Agent")
    task = "Generate a simple calculator function in Python"
    result = software_engineer_agent.handle_task(task)
    logger.info(f"Task ID: {result}")

    # Get the result
    task_result = software_engineer_agent.get_result(result)
    logger.info(f"Task result: {task_result}")

    # Stop the system
    exo_system.stop()

    logger.info("exo system stopped")

if __name__ == "__main__":
    main()
