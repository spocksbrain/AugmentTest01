"""
Tests for the web server module
"""

import pytest
import json
from unittest.mock import patch, MagicMock, AsyncMock
from exo.ui.web_server import WebServer

class TestWebServer:
    """Tests for the WebServer class."""
    
    @pytest.fixture
    def web_server(self):
        """Create a web server instance."""
        with patch('flask.Flask') as mock_flask, \
             patch('flask_socketio.SocketIO') as mock_socketio:
            server = WebServer(host="localhost", port=8080, websocket_port=8765)
            yield server
    
    def test_init(self):
        """Test initialization of the WebServer class."""
        with patch('flask.Flask') as mock_flask, \
             patch('flask_socketio.SocketIO') as mock_socketio:
            server = WebServer(host="test_host", port=1234, websocket_port=5678, app_mode=True)
            
            # Check that the server properties were set
            assert server.host == "test_host"
            assert server.port == 1234
            assert server.websocket_port == 5678
            assert server.app_mode is True
            
            # Check that Flask and SocketIO were initialized
            mock_flask.assert_called_once()
            mock_socketio.assert_called_once()
    
    def test_register_message_handler(self, web_server):
        """Test registering a message handler."""
        # Create a mock handler
        mock_handler = MagicMock()
        
        # Register the handler
        web_server.register_message_handler("test_type", mock_handler)
        
        # Check that the handler was registered
        assert "test_type" in web_server.message_handlers
        assert mock_handler in web_server.message_handlers["test_type"]
    
    def test_send_message(self, web_server):
        """Test sending a message."""
        # Mock the SocketIO emit method
        web_server.socketio.emit = MagicMock()
        
        # Create a test message
        message = {"type": "test", "data": {"content": "Test message"}}
        
        # Send the message
        web_server.send_message(message)
        
        # Check that SocketIO.emit was called
        web_server.socketio.emit.assert_called_once_with("message", message)
    
    @patch('asyncio.new_event_loop')
    @patch('asyncio.set_event_loop')
    @patch('threading.Thread')
    def test_start_websocket_server(self, mock_thread, mock_set_event_loop, mock_new_event_loop, web_server):
        """Test starting the WebSocket server."""
        # Mock the event loop
        mock_loop = MagicMock()
        mock_new_event_loop.return_value = mock_loop
        
        # Start the WebSocket server
        web_server._start_websocket_server()
        
        # Check that a new event loop was created and set
        mock_new_event_loop.assert_called_once()
        mock_set_event_loop.assert_called_once_with(mock_loop)
        
        # Check that a thread was started
        mock_thread.assert_called_once()
        mock_thread.return_value.start.assert_called_once()
    
    @patch('webbrowser.open')
    def test_start(self, mock_webbrowser_open, web_server):
        """Test starting the web server."""
        # Mock the methods
        web_server._setup_routes = MagicMock()
        web_server._setup_socketio_events = MagicMock()
        web_server._start_websocket_server = MagicMock()
        web_server.socketio.run = MagicMock()
        
        # Start the server with open_browser=True
        web_server.start(open_browser=True)
        
        # Check that the methods were called
        web_server._setup_routes.assert_called_once()
        web_server._setup_socketio_events.assert_called_once()
        web_server._start_websocket_server.assert_called_once()
        web_server.socketio.run.assert_called_once()
        
        # Check that the browser was opened
        mock_webbrowser_open.assert_called_once()
    
    @patch('webbrowser.open')
    def test_start_no_browser(self, mock_webbrowser_open, web_server):
        """Test starting the web server without opening a browser."""
        # Mock the methods
        web_server._setup_routes = MagicMock()
        web_server._setup_socketio_events = MagicMock()
        web_server._start_websocket_server = MagicMock()
        web_server.socketio.run = MagicMock()
        
        # Start the server with open_browser=False
        web_server.start(open_browser=False)
        
        # Check that the browser was not opened
        mock_webbrowser_open.assert_not_called()
    
    @patch('asyncio.get_event_loop')
    @patch('asyncio.new_event_loop')
    @patch('asyncio.set_event_loop')
    @patch('asyncio.run_coroutine_threadsafe')
    def test_handle_message(self, mock_run_coroutine_threadsafe, mock_set_event_loop, 
                           mock_new_event_loop, mock_get_event_loop, web_server):
        """Test handling a message."""
        # Mock the event loop
        mock_loop = MagicMock()
        mock_get_event_loop.side_effect = RuntimeError("No event loop")
        mock_new_event_loop.return_value = mock_loop
        
        # Create a mock handler
        mock_handler = MagicMock()
        web_server.register_message_handler("test_type", mock_handler)
        
        # Create a test message
        message = {"type": "test_type", "data": {"content": "Test message"}}
        
        # Handle the message
        web_server.handle_message(message)
        
        # Check that a new event loop was created when get_event_loop failed
        mock_new_event_loop.assert_called_once()
        mock_set_event_loop.assert_called_once_with(mock_loop)
        
        # Check that run_coroutine_threadsafe was called
        mock_run_coroutine_threadsafe.assert_called_once()
        
        # Check that the handler was called
        mock_handler.assert_called_once_with(message)
