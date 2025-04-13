"""
Tests for the LLM manager module
"""

import pytest
from unittest.mock import patch, MagicMock
from exo.agents.llm_manager import LLMManager

class TestLLMManager:
    """Tests for the LLMManager class."""
    
    @pytest.fixture
    def mock_onboarding(self):
        """Create a mock onboarding instance with specific API keys."""
        mock = MagicMock()
        # Set up API keys
        mock.get_env_var.side_effect = lambda key, default=None: {
            "OPENAI_API_KEY": "mock_openai_key",
            "ANTHROPIC_API_KEY": "mock_anthropic_key",
            "GOOGLE_API_KEY": "mock_google_key",
            "OPENROUTER_API_KEY": "mock_openrouter_key",
            "OLLAMA_BASE_URL": "http://localhost:11434",
            "DEFAULT_LLM_PROVIDER": "openai",
            "DEFAULT_LLM_MODEL": "gpt-3.5-turbo"
        }.get(key, default)
        return mock
    
    def test_init(self, mock_onboarding):
        """Test initialization of the LLMManager class."""
        llm_manager = LLMManager(onboarding=mock_onboarding)
        
        # Check that the API keys were loaded
        assert llm_manager.openai_api_key == "mock_openai_key"
        assert llm_manager.anthropic_api_key == "mock_anthropic_key"
        assert llm_manager.google_api_key == "mock_google_key"
        assert llm_manager.openrouter_api_key == "mock_openrouter_key"
        assert llm_manager.ollama_base_url == "http://localhost:11434"
        
        # Check that the default provider and model were loaded
        assert llm_manager.default_provider == "openai"
        assert llm_manager.default_model == "gpt-3.5-turbo"
    
    @patch('requests.post')
    def test_chat_openai(self, mock_post, mock_onboarding):
        """Test the OpenAI chat method."""
        # Set up the mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "Mock response from OpenAI"
                    }
                }
            ]
        }
        mock_post.return_value = mock_response
        
        # Create the LLM manager
        llm_manager = LLMManager(onboarding=mock_onboarding)
        
        # Call the chat method
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello, how are you?"}
        ]
        success, response = llm_manager._chat_openai(messages, "gpt-3.5-turbo", 100, 0.7)
        
        # Check the result
        assert success is True
        assert response == "Mock response from OpenAI"
        
        # Check that the API was called with the correct parameters
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert args[0] == "https://api.openai.com/v1/chat/completions"
        assert kwargs["headers"]["Authorization"] == "Bearer mock_openai_key"
        assert kwargs["json"]["model"] == "gpt-3.5-turbo"
        assert kwargs["json"]["messages"] == messages
        assert kwargs["json"]["max_tokens"] == 100
        assert kwargs["json"]["temperature"] == 0.7
    
    @patch('requests.post')
    def test_chat_openai_error(self, mock_post, mock_onboarding):
        """Test the OpenAI chat method with an error response."""
        # Set up the mock response
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = '{"error": {"message": "Invalid API key"}}'
        mock_post.return_value = mock_response
        
        # Create the LLM manager
        llm_manager = LLMManager(onboarding=mock_onboarding)
        
        # Call the chat method
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello, how are you?"}
        ]
        success, response = llm_manager._chat_openai(messages, "gpt-3.5-turbo", 100, 0.7)
        
        # Check the result
        assert success is False
        assert "Error: OpenAI API request failed" in response
    
    def test_chat_no_api_key(self, mock_onboarding):
        """Test the chat method with no API key."""
        # Modify the mock to return None for the API key
        mock_onboarding.get_env_var.side_effect = lambda key, default=None: None if key == "OPENAI_API_KEY" else "mock_value"
        
        # Create the LLM manager
        llm_manager = LLMManager(onboarding=mock_onboarding)
        
        # Call the chat method
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello, how are you?"}
        ]
        success, response = llm_manager._chat_openai(messages, "gpt-3.5-turbo", 100, 0.7)
        
        # Check the result
        assert success is False
        assert response == "Error: OpenAI API key not set"
    
    @patch('exo.agents.llm_manager.LLMManager._chat_openai')
    def test_chat(self, mock_chat_openai, mock_onboarding):
        """Test the chat method."""
        # Set up the mock response
        mock_chat_openai.return_value = (True, "Mock response from OpenAI")
        
        # Create the LLM manager
        llm_manager = LLMManager(onboarding=mock_onboarding)
        
        # Call the chat method
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello, how are you?"}
        ]
        success, response = llm_manager.chat(messages)
        
        # Check the result
        assert success is True
        assert response == "Mock response from OpenAI"
        
        # Check that the OpenAI chat method was called
        mock_chat_openai.assert_called_once_with(messages, "gpt-3.5-turbo", 1000, 0.7)
