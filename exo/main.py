"""
Main entry point for the exo Multi-Agent Framework
"""

import argparse
import logging
import os
import sys
import time
import threading

from exo.ui.web_server import WebServer
from exo.ui.electron_ui import ElectronUI

from exo.core.system import ExoSystem
from exo.core.onboarding import Onboarding
from exo.core.service_registry import ServiceRegistry, ServiceNames, register_service
from exo.agents.software_engineer import SoftwareEngineerAgent
from exo.agents.mcp_server import MCPServerAgent
from exo.agents.voice_assistant import VoiceAssistantAgent
from exo.agents.mcp_manager import MCPManager
from exo.agents.llm_manager import LLMManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def register_domain_agents(exo_system):
    """
    Register the initial domain agents with the system.

    Args:
        exo_system: The ExoSystem instance
    """
    logger.info("Registering domain agents")

    # Register Software Engineer Agent
    exo_system.register_domain_agent(
        agent_class=SoftwareEngineerAgent,
        domain="software_engineering",
        capabilities=[]
    )

    # Register MCP Server Agent
    exo_system.register_domain_agent(
        agent_class=MCPServerAgent,
        domain="mcp_server",
        capabilities=[]
    )

    logger.info("Domain agents registered")

def handle_ui_message(message):
    """Handle a message from the UI."""
    logger.info(f"Handling UI message: {message}")

    # Extract message data
    message_type = message.get("type")

    if message_type == "message":
        # Handle chat message
        chat_message = message.get("message", {})
        content = chat_message.get("content", "")

        # Process the message through the PIA
        # In a real implementation, this would be handled by the PIA
        logger.info(f"Processing message: {content}")

def main():
    """Main entry point for the exo system."""
    parser = argparse.ArgumentParser(description="exo Multi-Agent Framework")
    parser.add_argument("--config", help="Path to configuration file")
    parser.add_argument("--no-ui", action="store_true", help="Run without UI")
    parser.add_argument("--no-browser", action="store_true", help="Don't open browser automatically")
    parser.add_argument("--host", default="localhost", help="Host to bind the web server to")
    parser.add_argument("--port", type=int, default=8080, help="Port for the web server")
    parser.add_argument("--websocket-port", type=int, default=8765, help="Port for the WebSocket server")
    parser.add_argument("--skip-onboarding", action="store_true", help="Skip the onboarding process")
    parser.add_argument("--add-mcp-server", action="store_true", help="Add a new MCP server")
    parser.add_argument("--add-local-mcp", action="store_true", help="Install and add a local MCP server")
    parser.add_argument("--onboard", action="store_true", help="Run the onboarding process")
    parser.add_argument("--voice", action="store_true", help="Enable voice assistant")
    parser.add_argument("--wake-word", default="exo", help="Wake word for voice assistant")
    parser.add_argument("--simulate-voice", action="store_true", help="Use simulated voice commands (for testing)")
    parser.add_argument("--direct-mic", action="store_true", help="Use direct microphone access instead of web-based voice input")
    parser.add_argument("--app-mode", action="store_true", help="Launch browser in app mode (standalone window)")
    parser.add_argument("--electron", action="store_true", help="Use Electron UI instead of web UI")
    parser.add_argument("--no-electron", action="store_true", help="Disable Electron UI even if available")
    args = parser.parse_args()

    logger.info("Starting exo Multi-Agent Framework")

    # Initialize onboarding and register it as a service
    onboarding = Onboarding()
    register_service(ServiceNames.ONBOARDING, onboarding)

    # Run onboarding process if needed
    config_exists = os.path.exists(os.path.join(os.path.expanduser("~"), ".exo", "config.json"))
    if args.onboard:
        logger.info("Running onboarding process (manual)")
        onboarding.run_onboarding(interactive=True, force=True)
    elif not config_exists and not args.skip_onboarding:
        logger.info("Running onboarding process (automatic)")
        onboarding.run_onboarding(interactive=True)
    elif not args.skip_onboarding:
        # Export environment variables from configuration
        onboarding.export_env_vars()
        logger.info("Configuration loaded from existing file")

    # Initialize LLM and MCP managers and register them as services
    llm_manager = LLMManager(onboarding)
    register_service(ServiceNames.LLM_MANAGER, llm_manager)

    mcp_manager = MCPManager(onboarding)
    register_service(ServiceNames.MCP_MANAGER, mcp_manager)

    # Add MCP server if requested
    if args.add_mcp_server or args.add_local_mcp:
        logger.info("Adding new MCP server")
        if args.add_local_mcp:
            logger.info("Installing local MCP server")
            mcp_manager.onboard_new_server(local=True)
        else:
            mcp_manager.onboard_new_server(local=False)

    # Validate connections
    llm_valid = llm_manager.validate_connection()
    if not llm_valid:
        logger.warning("LLM connection validation failed")

    mcp_valid = mcp_manager.validate_server()
    if not mcp_valid:
        logger.warning("MCP server connection validation failed")

    # Initialize the system and register it as a service
    exo_system = ExoSystem()
    register_service(ServiceNames.SYSTEM, exo_system)

    # Initialize voice assistant if requested
    if args.voice:
        logger.info(f"Initializing voice assistant with wake word: {args.wake_word}")
        voice_assistant = VoiceAssistantAgent(
            wake_word=args.wake_word,
            use_simulation=args.simulate_voice,
            prefer_web_input=not args.direct_mic
        )
        register_service("voice_assistant", voice_assistant)

        # Start the voice assistant
        success = voice_assistant.start()
        if success:
            logger.info("Voice assistant started successfully")
        else:
            logger.warning("Failed to start voice assistant")

    # Register domain agents
    register_domain_agents(exo_system)

    # Initialize UI
    web_server = None
    electron_ui = None

    if not args.no_ui:
        # Check if Electron UI should be used
        use_electron = args.electron

        if not args.no_electron and not use_electron:
            # Check if Electron UI is available
            try:
                electron_ui = ElectronUI(host=args.host, port=args.port, websocket_port=args.websocket_port)
                if electron_ui.is_available():
                    use_electron = True
                    logger.info("Electron UI is available")
                else:
                    logger.info("Electron UI is not available, falling back to web UI")
            except Exception as e:
                logger.warning(f"Error checking Electron UI availability: {e}")
                logger.info("Falling back to web UI")

        # Start the appropriate UI
        if use_electron:
            try:
                logger.info("Starting Electron UI")
                if electron_ui is None:
                    electron_ui = ElectronUI(host=args.host, port=args.port, websocket_port=args.websocket_port)

                # Always start the web server for the Electron UI to connect to
                logger.info(f"Starting web server on {args.host}:{args.port} with WebSocket on port {args.websocket_port}")
                web_server = WebServer(host=args.host, port=args.port, websocket_port=args.websocket_port)
                web_server.register_message_handler("message", handle_ui_message)

                # Register voice message handler if voice assistant is enabled
                if args.voice and 'voice_assistant' in ServiceRegistry.services:
                    voice_assistant = ServiceRegistry.services['voice_assistant']
                    logger.info("Registering voice message handler")
                    web_server.register_message_handler("voice_message", voice_assistant.process_voice_message)

                # Start the web server without opening a browser
                web_server.start(open_browser=False)

                # Start the Electron UI
                electron_ui.start()
            except Exception as e:
                logger.warning(f"Failed to start Electron UI: {e}")
                logger.info("Falling back to web UI")
                electron_ui = None

                # Try to start the web UI as a fallback
                try:
                    logger.info(f"Starting web server on {args.host}:{args.port} with WebSocket on port {args.websocket_port}")
                    web_server = WebServer(host=args.host, port=args.port, websocket_port=args.websocket_port, app_mode=args.app_mode)
                    web_server.register_message_handler("message", handle_ui_message)

                    # Register voice message handler if voice assistant is enabled
                    if args.voice and 'voice_assistant' in ServiceRegistry.services:
                        voice_assistant = ServiceRegistry.services['voice_assistant']
                        logger.info("Registering voice message handler")
                        web_server.register_message_handler("voice_message", voice_assistant.process_voice_message)

                    web_server.start(open_browser=not args.no_browser)
                except Exception as e:
                    logger.warning(f"Failed to start web server: {e}")
                    logger.info("Continuing without UI")
                    web_server = None
        else:
            # Start the web UI
            try:
                logger.info(f"Starting web server on {args.host}:{args.port} with WebSocket on port {args.websocket_port}")
                web_server = WebServer(host=args.host, port=args.port, websocket_port=args.websocket_port, app_mode=args.app_mode)
                web_server.register_message_handler("message", handle_ui_message)

                # Register voice message handler if voice assistant is enabled
                if args.voice and 'voice_assistant' in ServiceRegistry.services:
                    voice_assistant = ServiceRegistry.services['voice_assistant']
                    logger.info("Registering voice message handler")
                    web_server.register_message_handler("voice_message", voice_assistant.process_voice_message)

                web_server.start(open_browser=not args.no_browser)
            except Exception as e:
                logger.warning(f"Failed to start web server: {e}")
                logger.info("Continuing without UI")
                web_server = None

    # Start the system
    exo_system.start()

    # Send a welcome message to the UI
    if web_server:
        try:
            welcome_message = {
                "role": "assistant",
                "content": "Welcome to exo! I'm your personal assistant. How can I help you today?",
                "timestamp": time.time()
            }
            web_server.send_chat_message(welcome_message)
            web_server.set_dot_state("idle")
        except Exception as e:
            logger.warning(f"Failed to send welcome message: {e}")

    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received, shutting down")
        exo_system.stop()
        if web_server:
            web_server.stop()
        if electron_ui:
            electron_ui.stop()

    logger.info("exo system shutdown complete")

if __name__ == "__main__":
    main()
