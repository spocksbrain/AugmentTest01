"""
Web Server for the exo Multi-Agent Framework

This module provides a web-based UI for the exo Multi-Agent Framework,
allowing users to interact with the system through a web browser.
"""

import asyncio
import json
import logging
import os
import threading
import uuid
import webbrowser
from typing import Dict, List, Optional, Any, Callable

import requests

import websockets
from flask import Flask, render_template, send_from_directory, request, jsonify
from flask_socketio import SocketIO

logger = logging.getLogger(__name__)

class WebServer:
    """
    Web Server for the exo Multi-Agent Framework.

    This class provides a web-based UI for the exo Multi-Agent Framework,
    allowing users to interact with the system through a web browser.
    """

    def __init__(self, host: str = "localhost", port: int = 8080, websocket_port: int = 8765, app_mode: bool = False):
        """
        Initialize the web server.

        Args:
            host: The host to bind to
            port: The port to bind to
            websocket_port: The port for the WebSocket server
            app_mode: Whether to launch the browser in app mode (standalone window)
        """
        self.host = host
        self.port = port
        self.websocket_port = websocket_port
        self.app_mode = app_mode
        self.app = Flask(__name__,
                         template_folder=os.path.join(os.path.dirname(__file__), "web", "templates"),
                         static_folder=os.path.join(os.path.dirname(__file__), "web", "static"))
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        self.websocket_server = None
        self.websocket_connections = set()
        self.message_handlers = {}
        self.running = False
        self.server_thread = None
        self.websocket_thread = None

        # Settings storage
        self.settings_dir = os.path.join(os.path.expanduser("~"), ".exo")
        os.makedirs(self.settings_dir, exist_ok=True)
        self.llm_settings_path = os.path.join(self.settings_dir, "llm_settings.json")
        self.mcp_servers_path = os.path.join(self.settings_dir, "mcp_servers.json")
        self.general_settings_path = os.path.join(self.settings_dir, "general_settings.json")

        # Set up routes
        self._setup_routes()

        # Set up SocketIO events
        self._setup_socketio_events()

        logger.info(f"Web server initialized with host: {host}, port: {port}, websocket_port: {websocket_port}")

    def _setup_routes(self):
        """Set up the Flask routes."""

        @self.app.route("/")
        def index():
            """Render the index page."""
            return render_template("index.html",
                                  host=self.host,
                                  port=self.port,
                                  websocket_port=self.websocket_port)

        @self.app.route("/favicon.ico")
        def favicon():
            """Serve the favicon."""
            return send_from_directory(
                os.path.join(self.app.static_folder, "img"),
                "favicon.ico",
                mimetype="image/vnd.microsoft.icon"
            )

        # API endpoints for settings
        @self.app.route("/api/settings/llm", methods=["GET", "POST"])
        def llm_settings():
            """Get or update LLM settings."""
            if request.method == "GET":
                return jsonify(self._load_llm_settings())
            else:
                data = request.json
                success = self._save_llm_settings(data)
                return jsonify({"success": success})

        @self.app.route("/api/settings/mcp-servers", methods=["GET", "POST"])
        def mcp_servers():
            """Get all MCP servers or add a new one."""
            if request.method == "GET":
                return jsonify({"servers": self._load_mcp_servers()})
            else:
                data = request.json
                # Generate a new ID if not provided
                if not data.get("id"):
                    data["id"] = str(uuid.uuid4())
                success = self._add_mcp_server(data)
                return jsonify({"success": success, "id": data["id"]})

        @self.app.route("/api/settings/mcp-servers/<server_id>", methods=["PUT", "DELETE"])
        def mcp_server(server_id):
            """Update or delete an MCP server."""
            if request.method == "PUT":
                data = request.json
                success = self._update_mcp_server(server_id, data)
                return jsonify({"success": success})
            else:
                success = self._delete_mcp_server(server_id)
                return jsonify({"success": success})

        @self.app.route("/api/settings/general", methods=["GET", "POST"])
        def general_settings():
            """Get or update general settings."""
            if request.method == "GET":
                return jsonify(self._load_general_settings())
            else:
                data = request.json
                success = self._save_general_settings(data)
                return jsonify({"success": success})

    def _setup_socketio_events(self):
        """Set up the SocketIO events."""

        @self.socketio.on("connect")
        def handle_connect():
            """Handle a client connection."""
            logger.info("Client connected to SocketIO")

        @self.socketio.on("disconnect")
        def handle_disconnect():
            """Handle a client disconnection."""
            logger.info("Client disconnected from SocketIO")

        @self.socketio.on("message")
        def handle_message(data):
            """
            Handle a message from the client.

            Args:
                data: The message data
            """
            logger.info(f"Received message from client: {data}")

            # Forward the message to the WebSocket clients
            try:
                # Try to get the existing event loop
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    # If there's no event loop in this thread, create a new one
                    logger.debug("No event loop in current thread, creating a new one")
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)

                # Run the coroutine in the event loop
                asyncio.run_coroutine_threadsafe(
                    self._broadcast_message(data),
                    loop
                )
            except Exception as e:
                logger.error(f"Error broadcasting message: {e}")

            # Call the appropriate handler
            message_type = data.get("type")
            if message_type in self.message_handlers:
                for handler in self.message_handlers[message_type]:
                    try:
                        handler(data)
                    except Exception as e:
                        logger.error(f"Error in message handler: {e}")

    def start(self, open_browser: bool = True):
        """
        Start the web server.

        Args:
            open_browser: Whether to open a browser window
        """
        logger.info("Starting web server")
        self.running = True

        # Start the WebSocket server
        self.websocket_thread = threading.Thread(target=self._run_websocket_server)
        self.websocket_thread.daemon = True
        self.websocket_thread.start()

        # Start the Flask server
        self.server_thread = threading.Thread(target=self._run_flask_server)
        self.server_thread.daemon = True
        self.server_thread.start()

        # Open a browser window
        if open_browser:
            self._open_browser()

    def stop(self):
        """Stop the web server."""
        logger.info("Stopping web server")
        self.running = False

        # Stop the WebSocket server
        if self.websocket_server:
            asyncio.run_coroutine_threadsafe(
                self.websocket_server.close(),
                asyncio.get_event_loop()
            )

        # Wait for the threads to finish
        if self.server_thread:
            self.server_thread.join(timeout=1.0)

        if self.websocket_thread:
            self.websocket_thread.join(timeout=1.0)

    def _run_flask_server(self):
        """Run the Flask server in a separate thread."""
        logger.info(f"Starting Flask server on {self.host}:{self.port}")
        self.socketio.run(self.app, host=self.host, port=self.port, debug=False, use_reloader=False)

    def _run_websocket_server(self):
        """Run the WebSocket server in a separate thread."""
        logger.info(f"Starting WebSocket server on port {self.websocket_port}")

        # Create a new event loop for the thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Define the coroutine to start the server
        async def start_server():
            self.websocket_server = await websockets.serve(
                self._handle_websocket,
                self.host,
                self.websocket_port
            )
            # Keep the server running
            while self.running:
                await asyncio.sleep(1)

        # Run the coroutine
        loop.run_until_complete(start_server())

    async def _handle_websocket(self, websocket):
        """
        Handle a WebSocket connection.

        Args:
            websocket: The WebSocket connection
        """
        logger.info(f"WebSocket client connected: {websocket.remote_address}")

        # Add the connection to the set
        self.websocket_connections.add(websocket)

        try:
            # Handle messages
            async for message in websocket:
                try:
                    data = json.loads(message)
                    logger.info(f"Received message from WebSocket: {data}")

                    # Forward the message to the SocketIO clients
                    self.socketio.emit("message", data)

                    # Call the appropriate handler
                    message_type = data.get("type")

                    # Special handling for voice messages
                    if message_type == "voice_message":
                        self.handle_voice_message(data)
                    elif message_type in self.message_handlers:
                        for handler in self.message_handlers[message_type]:
                            try:
                                handler(data)
                            except Exception as e:
                                logger.error(f"Error in message handler: {e}")
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON message: {message}")
                except Exception as e:
                    logger.error(f"Error handling message: {e}")
        finally:
            # Remove the connection from the set
            self.websocket_connections.remove(websocket)
            logger.info(f"WebSocket client disconnected: {websocket.remote_address}")

    async def _broadcast_message(self, message: Dict):
        """
        Broadcast a message to all WebSocket clients.

        Args:
            message: The message to broadcast
        """
        if not self.websocket_connections:
            logger.warning("No WebSocket connections, cannot broadcast message")
            return

        # Convert the message to JSON
        message_json = json.dumps(message)

        # Send the message to all clients
        websockets_to_remove = set()
        for websocket in self.websocket_connections:
            try:
                await websocket.send(message_json)
            except websockets.exceptions.ConnectionClosed:
                websockets_to_remove.add(websocket)
            except Exception as e:
                logger.error(f"Error sending message to WebSocket: {e}")
                websockets_to_remove.add(websocket)

        # Remove closed connections
        for websocket in websockets_to_remove:
            self.websocket_connections.remove(websocket)

    def send_message(self, message: Dict):
        """
        Send a message to all clients.

        Args:
            message: The message to send
        """
        logger.info(f"Sending message to clients: {message}")

        # Send the message to SocketIO clients
        self.socketio.emit("message", message)

        # Send the message to WebSocket clients
        asyncio.run_coroutine_threadsafe(
            self._broadcast_message(message),
            asyncio.get_event_loop()
        )

    def register_message_handler(self, message_type: str, handler: Callable[[Dict], None]):
        """
        Register a handler for a specific message type.

        Args:
            message_type: The message type to handle
            handler: The handler function
        """
        logger.info(f"Registering handler for message type: {message_type}")

        if message_type not in self.message_handlers:
            self.message_handlers[message_type] = []

        self.message_handlers[message_type].append(handler)

    def unregister_message_handler(self, message_type: str, handler: Callable[[Dict], None]):
        """
        Unregister a handler for a specific message type.

        Args:
            message_type: The message type
            handler: The handler function
        """
        logger.info(f"Unregistering handler for message type: {message_type}")

        if message_type in self.message_handlers:
            if handler in self.message_handlers[message_type]:
                self.message_handlers[message_type].remove(handler)

    def send_chat_message(self, message: Dict):
        """
        Send a chat message to the UI.

        Args:
            message: The message to send
        """
        self.send_message({
            "type": "chat_message",
            "data": message
        })

    def handle_voice_message(self, message_data: Dict):
        """
        Handle a voice message from the UI.

        Args:
            message_data: The message data containing the audio
        """
        try:
            import base64
            import tempfile
            import os
            from exo.ui.voice_interface import VoiceInterface

            # Extract the base64 audio data
            audio_data = message_data.get("data", {}).get("audio")
            if not audio_data:
                logger.error("No audio data in voice message")
                return

            # Decode the base64 audio data
            audio_bytes = base64.b64decode(audio_data)

            # Save to a temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_path = temp_file.name
                temp_file.write(audio_bytes)

            logger.info(f"Saved voice message to temporary file: {temp_path}")

            # Process the audio file using the voice interface
            # This will be handled by the voice assistant agent
            if "voice_message_handler" in self.message_handlers:
                for handler in self.message_handlers["voice_message"]:
                    try:
                        handler({
                            "audio_path": temp_path,
                            "timestamp": message_data.get("data", {}).get("timestamp")
                        })
                    except Exception as e:
                        logger.error(f"Error in voice message handler: {e}")
            else:
                logger.warning("No handler registered for voice messages")

        except Exception as e:
            logger.error(f"Error handling voice message: {e}")

    def set_dot_state(self, state: str):
        """
        Set the state of the animated dot.

        Args:
            state: The new state
        """
        self.send_message({
            "type": "dot_state",
            "data": {
                "state": state
            }
        })

    def _open_browser(self):
        """Open a browser window."""
        url = f"http://{self.host}:{self.port}"
        logger.info(f"Opening browser at {url}")

        # Wait a moment for the server to start
        if self.app_mode:
            # Check if we're in a container environment
            in_container = os.path.exists('/.dockerenv') or os.environ.get('CONTAINER_ENV')

            if in_container:
                logger.info("Detected container environment. Browser app mode not available.")
                logger.info(f"Please manually open {url} in app mode.")
                # Just return without opening browser
                return
            else:
                # Try to use Chrome in app mode
                try:
                    # Set browser path based on OS
                    if os.name == 'nt':  # Windows
                        chrome_path = 'C:/Program Files/Google/Chrome/Application/chrome.exe %s'
                    else:  # Linux/Mac
                        chrome_path = 'google-chrome %s'

                    browser = webbrowser.get(chrome_path)
                    logger.info("Launching browser in app mode (standalone window)")
                    threading.Timer(1.5, lambda: browser.open(f'--app={url}')).start()
                except Exception as e:
                    logger.warning(f"Failed to launch browser in app mode: {e}")
                    logger.info("Falling back to regular browser window")
                    threading.Timer(1.5, lambda: webbrowser.open(url)).start()
        else:
            # Regular browser window
            threading.Timer(1.5, lambda: webbrowser.open(url)).start()

    # Settings management methods
    def _load_llm_settings(self):
        """Load LLM settings from file."""
        if os.path.exists(self.llm_settings_path):
            try:
                with open(self.llm_settings_path, "r") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading LLM settings: {e}")

        # Default settings
        return {
            "default_provider": "openai",
            "default_model": "gpt-3.5-turbo",
            "api_keys": {
                "openai": "",
                "anthropic": "",
                "google": "",
                "openrouter": ""
            },
            "ollama_host": "http://localhost:11434"
        }

    def _save_llm_settings(self, settings):
        """Save LLM settings to file."""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.llm_settings_path), exist_ok=True)

            # Save settings
            with open(self.llm_settings_path, "w") as f:
                json.dump(settings, f, indent=2)

            # Update environment variables
            if "api_keys" in settings:
                if "openai" in settings["api_keys"] and settings["api_keys"]["openai"]:
                    os.environ["OPENAI_API_KEY"] = settings["api_keys"]["openai"]
                if "anthropic" in settings["api_keys"] and settings["api_keys"]["anthropic"]:
                    os.environ["ANTHROPIC_API_KEY"] = settings["api_keys"]["anthropic"]
                if "google" in settings["api_keys"] and settings["api_keys"]["google"]:
                    os.environ["GOOGLE_API_KEY"] = settings["api_keys"]["google"]
                if "openrouter" in settings["api_keys"] and settings["api_keys"]["openrouter"]:
                    os.environ["OPENROUTER_API_KEY"] = settings["api_keys"]["openrouter"]

            # Update default provider and model
            if "default_provider" in settings:
                os.environ["DEFAULT_LLM_PROVIDER"] = settings["default_provider"]
            if "default_model" in settings:
                os.environ["DEFAULT_LLM_MODEL"] = settings["default_model"]

            # Update Ollama host
            if "ollama_host" in settings:
                os.environ["OLLAMA_BASE_URL"] = settings["ollama_host"]

            return True
        except Exception as e:
            logger.error(f"Error saving LLM settings: {e}")
            return False

    def _load_mcp_servers(self):
        """Load MCP servers from file."""
        if os.path.exists(self.mcp_servers_path):
            try:
                with open(self.mcp_servers_path, "r") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading MCP servers: {e}")

        return []

    def _save_mcp_servers(self, servers):
        """Save MCP servers to file."""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.mcp_servers_path), exist_ok=True)

            # Save servers
            with open(self.mcp_servers_path, "w") as f:
                json.dump(servers, f, indent=2)

            return True
        except Exception as e:
            logger.error(f"Error saving MCP servers: {e}")
            return False

    def _add_mcp_server(self, server):
        """Add a new MCP server."""
        servers = self._load_mcp_servers()
        servers.append(server)
        return self._save_mcp_servers(servers)

    def _update_mcp_server(self, server_id, server_data):
        """Update an existing MCP server."""
        servers = self._load_mcp_servers()
        for i, server in enumerate(servers):
            if server.get("id") == server_id:
                # Update server data
                servers[i] = server_data
                return self._save_mcp_servers(servers)

        return False

    def _delete_mcp_server(self, server_id):
        """Delete an MCP server."""
        servers = self._load_mcp_servers()
        for i, server in enumerate(servers):
            if server.get("id") == server_id:
                # Remove server
                servers.pop(i)
                return self._save_mcp_servers(servers)

        return False

    def _load_general_settings(self):
        """Load general settings from file."""
        if os.path.exists(self.general_settings_path):
            try:
                with open(self.general_settings_path, "r") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading general settings: {e}")

        # Default settings
        return {
            "theme": "system",
            "auto_scroll": True
        }

    def _save_general_settings(self, settings):
        """Save general settings to file."""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.general_settings_path), exist_ok=True)

            # Save settings
            with open(self.general_settings_path, "w") as f:
                json.dump(settings, f, indent=2)

            return True
        except Exception as e:
            logger.error(f"Error saving general settings: {e}")
            return False
