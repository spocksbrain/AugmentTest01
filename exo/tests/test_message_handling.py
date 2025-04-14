"""
Tests for the message handling flow in main.py
"""

import pytest
import time
from unittest.mock import patch, MagicMock, call

# Import the handle_ui_message function from main.py
from exo.main import handle_ui_message
from exo.core.service_registry import ServiceNames

class TestMessageHandling:
    """Tests for the message handling flow."""

    @patch('exo.main.get_service')
    def test_handle_ui_message_valid(self, mock_get_service):
        """Test handling a valid UI message."""
        # Set up mocks
        mock_system = MagicMock()
        mock_system.pia.process_user_input.return_value = "Test response"

        mock_web_server = MagicMock()

        # Configure the mock_get_service to return different values based on the argument
        def get_service_side_effect(service_name):
            if service_name == ServiceNames.SYSTEM:
                return mock_system
            elif service_name == "web_server":
                return mock_web_server
            return None

        mock_get_service.side_effect = get_service_side_effect

        # Create a test message
        message = {
            "type": "message",
            "data": {
                "content": "Hello",
                "role": "user",
                "timestamp": time.time()
            }
        }

        # Handle the message
        handle_ui_message(message)

        # Check that the appropriate methods were called
        mock_get_service.assert_any_call(ServiceNames.SYSTEM)
        mock_get_service.assert_any_call("web_server")
        mock_system.pia.process_user_input.assert_called_once_with("Hello")

        # Check that the web server was called to send the response
        mock_web_server.send_message.assert_called_once()
        call_args = mock_web_server.send_message.call_args[0][0]
        assert call_args["type"] == "chat_message"
        assert call_args["data"]["role"] == "assistant"
        assert call_args["data"]["content"] == "Test response"

    @patch('exo.main.get_service')
    def test_handle_ui_message_invalid_format(self, mock_get_service):
        """Test handling an invalid UI message format."""
        # Handle an invalid message
        handle_ui_message("not a dict")

        # Check that no services were requested
        mock_get_service.assert_not_called()

    @patch('exo.main.get_service')
    def test_handle_ui_message_missing_type(self, mock_get_service):
        """Test handling a UI message with missing type."""
        # Handle a message with missing type
        handle_ui_message({"data": {"content": "Hello"}})

        # Check that no services were requested
        mock_get_service.assert_not_called()

    @patch('exo.main.get_service')
    def test_handle_ui_message_missing_data(self, mock_get_service):
        """Test handling a UI message with missing data."""
        # Handle a message with missing data
        handle_ui_message({"type": "message"})

        # Check that no services were requested
        mock_get_service.assert_not_called()

    def test_handle_ui_message_missing_content(self):
        """Test handling a UI message with missing content."""
        # Handle a message with missing content
        handle_ui_message({"type": "message", "data": {}})

        # This test just verifies that the function doesn't crash
        # The function should log a warning and return without processing

    @patch('exo.main.get_service')
    def test_handle_ui_message_system_not_available(self, mock_get_service):
        """Test handling a UI message when the system service is not available."""
        # Configure mock_get_service to return None for the system service
        mock_get_service.return_value = None

        # Handle a valid message
        message = {
            "type": "message",
            "data": {
                "content": "Hello",
                "role": "user",
                "timestamp": time.time()
            }
        }

        handle_ui_message(message)

        # Check that the system service was requested but no further processing occurred
        mock_get_service.assert_called_once_with(ServiceNames.SYSTEM)

    @patch('exo.main.get_service')
    def test_handle_ui_message_web_server_not_available(self, mock_get_service):
        """Test handling a UI message when the web server is not available."""
        # Set up mocks
        mock_system = MagicMock()

        # Configure the mock_get_service to return different values based on the argument
        def get_service_side_effect(service_name):
            if service_name == ServiceNames.SYSTEM:
                return mock_system
            elif service_name == "web_server":
                return None
            return None

        mock_get_service.side_effect = get_service_side_effect

        # Handle a valid message
        message = {
            "type": "message",
            "data": {
                "content": "Hello",
                "role": "user",
                "timestamp": time.time()
            }
        }

        handle_ui_message(message)

        # Check that the appropriate services were requested but no processing occurred
        mock_get_service.assert_any_call(ServiceNames.SYSTEM)
        mock_get_service.assert_any_call("web_server")
        mock_system.pia.process_user_input.assert_not_called()

    @patch('exo.main.get_service')
    def test_handle_ui_message_pia_exception(self, mock_get_service):
        """Test handling a UI message when the PIA raises an exception."""
        # Set up mocks
        mock_system = MagicMock()
        mock_system.pia.process_user_input.side_effect = Exception("Test exception")

        mock_web_server = MagicMock()

        # Configure the mock_get_service to return different values based on the argument
        def get_service_side_effect(service_name):
            if service_name == ServiceNames.SYSTEM:
                return mock_system
            elif service_name == "web_server":
                return mock_web_server
            return None

        mock_get_service.side_effect = get_service_side_effect

        # Handle a valid message
        message = {
            "type": "message",
            "data": {
                "content": "Hello",
                "role": "user",
                "timestamp": time.time()
            }
        }

        handle_ui_message(message)

        # Check that the appropriate methods were called
        mock_get_service.assert_any_call(ServiceNames.SYSTEM)
        mock_get_service.assert_any_call("web_server")
        mock_system.pia.process_user_input.assert_called_once_with("Hello")

        # Check that the web server was called to send an error message
        mock_web_server.send_message.assert_called_once()
        call_args = mock_web_server.send_message.call_args[0][0]
        assert call_args["type"] == "chat_message"
        assert call_args["data"]["role"] == "assistant"
        assert "error occurred" in call_args["data"]["content"].lower()

    @patch('exo.main.get_service')
    def test_handle_ui_message_unknown_type(self, mock_get_service):
        """Test handling a UI message with an unknown type."""
        # Handle a message with an unknown type
        handle_ui_message({"type": "unknown", "data": {"content": "Hello"}})

        # Check that no services were requested
        mock_get_service.assert_not_called()
