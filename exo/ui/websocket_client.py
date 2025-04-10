"""
WebSocket client for communication with the Electron UI
"""

import asyncio
import json
import logging
import threading
import websockets
from typing import Dict, List, Optional, Any, Callable

logger = logging.getLogger(__name__)

class WebSocketClient:
    """
    WebSocket client for communication with the Electron UI.

    This class provides a bridge between the Python backend and the Electron UI,
    allowing them to communicate via WebSocket.
    """

    def __init__(self, uri: str = "ws://localhost:8765"):
        """
        Initialize the WebSocket client.

        Args:
            uri: The WebSocket server URI
        """
        self.uri = uri
        self.websocket = None
        self.running = False
        self.message_handlers = {}
        self.client_thread = None
        logger.info(f"WebSocket client initialized with URI: {uri}")

    def start(self):
        """Start the WebSocket client."""
        logger.info("Starting WebSocket client")
        self.running = True
        self.client_thread = threading.Thread(target=self._run_client)
        self.client_thread.daemon = True
        self.client_thread.start()

    def stop(self):
        """Stop the WebSocket client."""
        logger.info("Stopping WebSocket client")
        self.running = False
        if self.client_thread:
            self.client_thread.join(timeout=1.0)

    def _run_client(self):
        """Run the WebSocket client in a separate thread."""
        logger.info("WebSocket client thread started")

        # Create a new event loop for the thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Run the client
        try:
            loop.run_until_complete(self._client_loop())
        except Exception as e:
            logger.error(f"WebSocket client error: {e}")
        finally:
            loop.close()
            logger.info("WebSocket client thread stopped")

    async def _client_loop(self):
        """Main client loop."""
        connection_attempts = 0
        max_connection_attempts = 5

        while self.running:
            try:
                # Connect to the WebSocket server
                logger.info(f"Connecting to WebSocket server at {self.uri}")
                async with websockets.connect(self.uri) as websocket:
                    # Reset connection attempts on successful connection
                    connection_attempts = 0

                    self.websocket = websocket
                    logger.info("Connected to WebSocket server")

                    # Handle messages
                    while self.running:
                        try:
                            message = await websocket.recv()
                            await self._handle_message(message)
                        except websockets.exceptions.ConnectionClosed:
                            logger.warning("WebSocket connection closed")
                            break
                        except Exception as e:
                            logger.error(f"Error handling message: {e}")

                self.websocket = None

                # Wait before reconnecting
                await asyncio.sleep(1)
            except Exception as e:
                connection_attempts += 1
                if connection_attempts >= max_connection_attempts:
                    logger.warning(f"Failed to connect after {max_connection_attempts} attempts. Will continue running without WebSocket connection.")
                    # Don't try to reconnect anymore, but keep the client running
                    await asyncio.sleep(60)  # Check again after a minute
                    connection_attempts = 0
                else:
                    logger.error(f"WebSocket connection error: {e} (Attempt {connection_attempts}/{max_connection_attempts})")
                    await asyncio.sleep(5)  # Wait before retrying

    async def _handle_message(self, message: str):
        """
        Handle a message from the WebSocket server.

        Args:
            message: The message to handle
        """
        try:
            data = json.loads(message)
            logger.info(f"Received message: {data}")

            # Get the message type
            message_type = data.get("type")

            # Call the appropriate handler
            if message_type in self.message_handlers:
                for handler in self.message_handlers[message_type]:
                    try:
                        handler(data)
                    except Exception as e:
                        logger.error(f"Error in message handler: {e}")
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON message: {message}")
        except Exception as e:
            logger.error(f"Error handling message: {e}")

    def send_message(self, message: Dict):
        """
        Send a message to the WebSocket server.

        Args:
            message: The message to send
        """
        if not self.websocket:
            logger.warning("WebSocket not connected, cannot send message")
            return

        # Create a task to send the message
        asyncio.run_coroutine_threadsafe(
            self._send_message_async(message),
            asyncio.get_event_loop()
        )

    async def _send_message_async(self, message: Dict):
        """
        Send a message to the WebSocket server asynchronously.

        Args:
            message: The message to send
        """
        try:
            if self.websocket:
                await self.websocket.send(json.dumps(message))
                logger.info(f"Sent message: {message}")
        except Exception as e:
            logger.error(f"Error sending message: {e}")

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
            "type": "message",
            "message": message
        })

    def set_dot_state(self, state: str):
        """
        Set the state of the animated dot.

        Args:
            state: The new state
        """
        self.send_message({
            "type": "dot_state",
            "state": state
        })
