"""
LLM Manager for the exo Multi-Agent Framework

This module handles the integration with Language Model providers,
including OpenAI, Anthropic, Google, OpenRouter, and Ollama.
"""

import os
import json
import logging
import requests
from typing import Dict, List, Optional, Any, Tuple

from exo.core.onboarding import Onboarding

logger = logging.getLogger(__name__)

class LLMManager:
    """
    LLM Manager for the exo Multi-Agent Framework

    This class handles the integration with Language Model providers,
    including OpenAI, Anthropic, Google, OpenRouter, and Ollama.
    """

    def __init__(self, onboarding: Optional[Onboarding] = None):
        """
        Initialize the LLM Manager.

        Args:
            onboarding: Onboarding instance to use for configuration
        """
        self.onboarding = onboarding or Onboarding()

        # Get API keys and configuration
        self.openai_api_key = self.onboarding.get_env_var("OPENAI_API_KEY")
        self.anthropic_api_key = self.onboarding.get_env_var("ANTHROPIC_API_KEY")
        self.google_api_key = self.onboarding.get_env_var("GOOGLE_API_KEY")
        self.openrouter_api_key = self.onboarding.get_env_var("OPENROUTER_API_KEY")
        self.ollama_base_url = self.onboarding.get_env_var("OLLAMA_BASE_URL") or "http://localhost:11434"

        # Get default provider and model
        self.default_provider = self.onboarding.get_env_var("DEFAULT_LLM_PROVIDER") or "openai"
        self.default_model = self.onboarding.get_env_var("DEFAULT_LLM_MODEL") or "gpt-3.5-turbo"

        # Track available models
        self.available_models = {
            "openai": [],
            "anthropic": [],
            "google": [],
            "openrouter": [],
            "ollama": []
        }

        # Load available models
        self._load_available_models()

    def _load_available_models(self):
        """Load available models from the API providers."""
        # Try OpenAI API
        if self.openai_api_key:
            try:
                headers = {
                    "Authorization": f"Bearer {self.openai_api_key}",
                    "Content-Type": "application/json"
                }
                response = requests.get(
                    "https://api.openai.com/v1/models",
                    headers=headers,
                    timeout=5
                )
                if response.status_code == 200:
                    data = response.json()
                    self.available_models["openai"] = [model["id"] for model in data["data"]]
                    logger.info("Loaded %d OpenAI models", len(self.available_models["openai"]))
                else:
                    logger.warning("Failed to load OpenAI models: %s", response.text)
            except Exception as e:
                logger.warning("Error loading OpenAI models: %s", e)

        # Try Anthropic API
        if self.anthropic_api_key:
            try:
                headers = {
                    "x-api-key": self.anthropic_api_key,
                    "Content-Type": "application/json",
                    "anthropic-version": "2023-06-01"
                }
                response = requests.get(
                    "https://api.anthropic.com/v1/models",
                    headers=headers,
                    timeout=5
                )
                if response.status_code == 200:
                    data = response.json()
                    self.available_models["anthropic"] = [model["id"] for model in data["models"]]
                    logger.info("Loaded %d Anthropic models", len(self.available_models["anthropic"]))
                else:
                    logger.warning("Failed to load Anthropic models: %s", response.text)
            except Exception as e:
                logger.warning("Error loading Anthropic models: %s", e)

        # Try Google API
        if self.google_api_key:
            try:
                headers = {
                    "x-goog-api-key": self.google_api_key,
                    "Content-Type": "application/json"
                }
                response = requests.get(
                    "https://generativelanguage.googleapis.com/v1beta/models",
                    headers=headers,
                    timeout=5
                )
                if response.status_code == 200:
                    data = response.json()
                    self.available_models["google"] = [model["name"].split("/")[-1] for model in data["models"]]
                    logger.info("Loaded %d Google models", len(self.available_models["google"]))
                else:
                    logger.warning("Failed to load Google models: %s", response.text)
            except Exception as e:
                logger.warning("Error loading Google models: %s", e)

        # Try OpenRouter API
        if self.openrouter_api_key:
            try:
                headers = {
                    "Authorization": f"Bearer {self.openrouter_api_key}",
                    "Content-Type": "application/json"
                }
                response = requests.get(
                    "https://openrouter.ai/api/v1/models",
                    headers=headers,
                    timeout=5
                )
                if response.status_code == 200:
                    data = response.json()
                    self.available_models["openrouter"] = [model["id"] for model in data["data"]]
                    logger.info("Loaded %d OpenRouter models", len(self.available_models["openrouter"]))
                else:
                    logger.warning("Failed to load OpenRouter models: %s", response.text)
            except Exception as e:
                logger.warning("Error loading OpenRouter models: %s", e)

        # Try Ollama API
        try:
            response = requests.get(
                f"{self.ollama_base_url}/api/tags",
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                self.available_models["ollama"] = [model["name"] for model in data["models"]]
                logger.info("Loaded %d Ollama models", len(self.available_models["ollama"]))
            else:
                logger.warning("Failed to load Ollama models: %s", response.text)
        except Exception as e:
            logger.warning("Error loading Ollama models: %s", e)

    def get_available_models(self) -> Dict[str, List[str]]:
        """
        Get available models from all providers.

        Returns:
            Dictionary of provider to list of model IDs
        """
        return self.available_models

    def validate_connection(self) -> bool:
        """
        Validate connection to LLM providers.

        Returns:
            True if at least one provider is available
        """
        return self.onboarding.validate_llm_connection()

    def generate_text(self, prompt: str, model: str = None,
                     max_tokens: int = 1000, temperature: float = 0.7,
                     provider: Optional[str] = None) -> Tuple[bool, str]:
        """
        Generate text using a language model.

        Args:
            prompt: Prompt to generate text from
            model: Model to use (if None, uses default model)
            max_tokens: Maximum number of tokens to generate
            temperature: Temperature for generation
            provider: Provider to use (if None, uses default provider)

        Returns:
            Tuple of (success, generated_text)
        """
        # Use default provider and model if not specified
        if provider is None:
            provider = self.default_provider

        if model is None:
            model = self.default_model

        # Auto-select provider based on model if not specified
        if provider is None:
            if model.startswith("gpt-") or model.startswith("text-davinci-"):
                provider = "openai"
            elif model.startswith("claude-"):
                provider = "anthropic"
            elif model.startswith("gemini-") or model.startswith("models/gemini"):
                provider = "google"
            elif model.startswith("anthropic/") or model.startswith("openai/") or model.startswith("meta/"):
                provider = "openrouter"
            else:
                # Try Ollama as a fallback
                provider = "ollama"

        # Generate text using the appropriate provider
        if provider == "openai":
            return self._generate_openai(prompt, model, max_tokens, temperature)
        elif provider == "anthropic":
            return self._generate_anthropic(prompt, model, max_tokens, temperature)
        elif provider == "google":
            return self._generate_google(prompt, model, max_tokens, temperature)
        elif provider == "openrouter":
            return self._generate_openrouter(prompt, model, max_tokens, temperature)
        elif provider == "ollama":
            return self._generate_ollama(prompt, model, max_tokens, temperature)
        else:
            logger.warning("Unsupported provider: %s", provider)
            return False, f"Error: Unsupported provider: {provider}"

    def _generate_openai(self, prompt: str, model: str,
                        max_tokens: int, temperature: float) -> Tuple[bool, str]:
        """
        Generate text using OpenAI API.

        Args:
            prompt: Prompt to generate text from
            model: Model to use
            max_tokens: Maximum number of tokens to generate
            temperature: Temperature for generation

        Returns:
            Tuple of (success, generated_text)
        """
        if not self.openai_api_key:
            logger.warning("OpenAI API key not set")
            return False, "Error: OpenAI API key not set"

        try:
            headers = {
                "Authorization": f"Bearer {self.openai_api_key}",
                "Content-Type": "application/json"
            }

            # Check if using a chat model
            is_chat_model = model.startswith("gpt-") or model.startswith("o3-") or model == "o3"

            if is_chat_model:
                # Check if the model is a newer OpenAI model that requires max_completion_tokens
                if model == "o3-mini" or model == "o3" or model.startswith("o3-"):
                    data = {
                        "model": model,
                        "messages": [{"role": "user", "content": prompt}],
                        "max_completion_tokens": max_tokens,
                        "temperature": temperature
                    }
                else:
                    # Use max_tokens for other models
                    data = {
                        "model": model,
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": max_tokens,
                        "temperature": temperature
                    }
                url = "https://api.openai.com/v1/chat/completions"
            else:
                data = {
                    "model": model,
                    "prompt": prompt,
                    "max_tokens": max_tokens,
                    "temperature": temperature
                }
                url = "https://api.openai.com/v1/completions"

            response = requests.post(
                url,
                headers=headers,
                json=data,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                if is_chat_model:
                    return True, data["choices"][0]["message"]["content"]
                else:
                    return True, data["choices"][0]["text"]
            else:
                logger.warning("OpenAI API request failed: %s", response.text)
                return False, f"Error: OpenAI API request failed: {response.text}"
        except Exception as e:
            logger.error("Error generating text with OpenAI: %s", e)
            return False, f"Error generating text with OpenAI: {e}"

    def _generate_anthropic(self, prompt: str, model: str,
                           max_tokens: int, temperature: float) -> Tuple[bool, str]:
        """
        Generate text using Anthropic API.

        Args:
            prompt: Prompt to generate text from
            model: Model to use
            max_tokens: Maximum number of tokens to generate
            temperature: Temperature for generation

        Returns:
            Tuple of (success, generated_text)
        """
        if not self.anthropic_api_key:
            logger.warning("Anthropic API key not set")
            return False, "Error: Anthropic API key not set"

        try:
            headers = {
                "x-api-key": self.anthropic_api_key,
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            }

            data = {
                "model": model,
                "prompt": f"Human: {prompt}\n\nAssistant:",
                "max_tokens_to_sample": max_tokens,
                "temperature": temperature
            }

            response = requests.post(
                "https://api.anthropic.com/v1/complete",
                headers=headers,
                json=data,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                return True, data["completion"]
            else:
                logger.warning("Anthropic API request failed: %s", response.text)
                return False, f"Error: Anthropic API request failed: {response.text}"
        except Exception as e:
            logger.error("Error generating text with Anthropic: %s", e)
            return False, f"Error generating text with Anthropic: {e}"

    def _generate_google(self, prompt: str, model: str,
                         max_tokens: int, temperature: float) -> Tuple[bool, str]:
        """
        Generate text using Google Gemini API.

        Args:
            prompt: Prompt to generate text from
            model: Model to use
            max_tokens: Maximum number of tokens to generate
            temperature: Temperature for generation

        Returns:
            Tuple of (success, generated_text)
        """
        if not self.google_api_key:
            logger.warning("Google API key not set")
            return False, "Error: Google API key not set"

        try:
            # Clean up model name if it includes the full path
            if "/" in model:
                model = model.split("/")[-1]

            headers = {
                "x-goog-api-key": self.google_api_key,
                "Content-Type": "application/json"
            }

            data = {
                "contents": [
                    {
                        "role": "user",
                        "parts": [{"text": prompt}]
                    }
                ],
                "generationConfig": {
                    "maxOutputTokens": max_tokens,
                    "temperature": temperature
                }
            }

            response = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
                headers=headers,
                json=data,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                # Extract the generated text from the response
                if "candidates" in data and len(data["candidates"]) > 0:
                    candidate = data["candidates"][0]
                    if "content" in candidate and "parts" in candidate["content"]:
                        parts = candidate["content"]["parts"]
                        if len(parts) > 0 and "text" in parts[0]:
                            return True, parts[0]["text"]

                logger.warning("Unexpected response format from Google API")
                return False, "Error: Unexpected response format from Google API"
            else:
                logger.warning("Google API request failed: %s", response.text)
                return False, f"Error: Google API request failed: {response.text}"
        except Exception as e:
            logger.error("Error generating text with Google: %s", e)
            return False, f"Error generating text with Google: {e}"

    def _generate_openrouter(self, prompt: str, model: str,
                           max_tokens: int, temperature: float) -> Tuple[bool, str]:
        """
        Generate text using OpenRouter API.

        Args:
            prompt: Prompt to generate text from
            model: Model to use
            max_tokens: Maximum number of tokens to generate
            temperature: Temperature for generation

        Returns:
            Tuple of (success, generated_text)
        """
        if not self.openrouter_api_key:
            logger.warning("OpenRouter API key not set")
            return False, "Error: OpenRouter API key not set"

        try:
            headers = {
                "Authorization": f"Bearer {self.openrouter_api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://exo.ai",  # Required by OpenRouter
                "X-Title": "Exo Multi-Agent Framework"  # Optional but recommended
            }

            # OpenRouter uses the ChatGPT-like format
            data = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens,
                "temperature": temperature
            }

            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                return True, data["choices"][0]["message"]["content"]
            else:
                logger.warning("OpenRouter API request failed: %s", response.text)
                return False, f"Error: OpenRouter API request failed: {response.text}"
        except Exception as e:
            logger.error("Error generating text with OpenRouter: %s", e)
            return False, f"Error generating text with OpenRouter: {e}"

    def _generate_ollama(self, prompt: str, model: str,
                        max_tokens: int, temperature: float) -> Tuple[bool, str]:
        """
        Generate text using Ollama API.

        Args:
            prompt: Prompt to generate text from
            model: Model to use
            max_tokens: Maximum number of tokens to generate
            temperature: Temperature for generation

        Returns:
            Tuple of (success, generated_text)
        """
        try:
            headers = {
                "Content-Type": "application/json"
            }

            data = {
                "model": model,
                "prompt": prompt,
                "options": {
                    "num_predict": max_tokens,
                    "temperature": temperature
                }
            }

            response = requests.post(
                f"{self.ollama_base_url}/api/generate",
                headers=headers,
                json=data,
                timeout=60  # Ollama can be slower, especially on first run
            )

            if response.status_code == 200:
                data = response.json()
                return True, data["response"]
            else:
                logger.warning("Ollama API request failed: %s", response.text)
                return False, f"Error: Ollama API request failed: {response.text}"
        except Exception as e:
            logger.error("Error generating text with Ollama: %s", e)
            return False, f"Error generating text with Ollama: {e}"

    def chat(self, messages: List[Dict[str, str]], model: str = None,
            max_tokens: int = 1000, temperature: float = 0.7,
            provider: Optional[str] = None) -> Tuple[bool, str]:
        """
        Chat with a language model.

        Args:
            messages: List of messages in the conversation
            model: Model to use
            max_tokens: Maximum number of tokens to generate
            temperature: Temperature for generation

        Returns:
            Tuple of (success, response_text)
        """
        # Use default provider and model if not specified
        if provider is None:
            provider = self.default_provider

        if model is None:
            model = self.default_model

        # Auto-select provider based on model if not specified
        if provider is None:
            if model.startswith("gpt-") or model.startswith("text-davinci-"):
                provider = "openai"
            elif model.startswith("claude-"):
                provider = "anthropic"
            elif model.startswith("gemini-") or model.startswith("models/gemini"):
                provider = "google"
            elif model.startswith("anthropic/") or model.startswith("openai/") or model.startswith("meta/"):
                provider = "openrouter"
            else:
                # Try Ollama as a fallback
                provider = "ollama"

        # Generate text using the appropriate provider
        if provider == "openai":
            return self._chat_openai(messages, model, max_tokens, temperature)
        elif provider == "anthropic":
            return self._chat_anthropic(messages, model, max_tokens, temperature)
        elif provider == "google":
            return self._chat_google(messages, model, max_tokens, temperature)
        elif provider == "openrouter":
            return self._chat_openrouter(messages, model, max_tokens, temperature)
        elif provider == "ollama":
            return self._chat_ollama(messages, model, max_tokens, temperature)
        else:
            logger.warning("Unsupported provider for chat: %s", provider)
            return False, f"Error: Unsupported provider for chat: {provider}"

    def _chat_openai(self, messages: List[Dict[str, str]], model: str,
                    max_tokens: int, temperature: float) -> Tuple[bool, str]:
        """
        Chat with OpenAI API.

        Args:
            messages: List of messages in the conversation
            model: Model to use
            max_tokens: Maximum number of tokens to generate
            temperature: Temperature for generation

        Returns:
            Tuple of (success, response_text)
        """
        if not self.openai_api_key:
            logger.warning("OpenAI API key not set")
            return False, "Error: OpenAI API key not set"

        try:
            headers = {
                "Authorization": f"Bearer {self.openai_api_key}",
                "Content-Type": "application/json"
            }

            # Check if the model is a newer OpenAI model that requires max_completion_tokens
            if model == "o3-mini" or model == "o3" or model.startswith("o3-"):
                data = {
                    "model": model,
                    "messages": messages,
                    "max_completion_tokens": max_tokens,
                    "temperature": temperature
                }
            else:
                # Use max_tokens for other models
                data = {
                    "model": model,
                    "messages": messages,
                    "max_tokens": max_tokens,
                    "temperature": temperature
                }

            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                return True, data["choices"][0]["message"]["content"]
            else:
                logger.warning("OpenAI API request failed: %s", response.text)
                return False, f"Error: OpenAI API request failed: {response.text}"
        except Exception as e:
            logger.error("Error chatting with OpenAI: %s", e)
            return False, f"Error chatting with OpenAI: {e}"

    def _chat_google(self, messages: List[Dict[str, str]], model: str,
                       max_tokens: int, temperature: float) -> Tuple[bool, str]:
        """
        Chat with Google Gemini API.

        Args:
            messages: List of messages in the conversation
            model: Model to use
            max_tokens: Maximum number of tokens to generate
            temperature: Temperature for generation

        Returns:
            Tuple of (success, response_text)
        """
        if not self.google_api_key:
            logger.warning("Google API key not set")
            return False, "Error: Google API key not set"

        try:
            # Clean up model name if it includes the full path
            if "/" in model:
                model = model.split("/")[-1]

            headers = {
                "x-goog-api-key": self.google_api_key,
                "Content-Type": "application/json"
            }

            # Convert messages to Google Gemini format
            contents = []
            for message in messages:
                role = message.get("role", "user")
                content = message.get("content", "")

                # Map OpenAI roles to Google roles
                if role == "system":
                    # Add system message as a user message with a special prefix
                    contents.append({
                        "role": "user",
                        "parts": [{"text": f"[System Instructions]: {content}"}]
                    })
                elif role == "assistant":
                    contents.append({
                        "role": "model",
                        "parts": [{"text": content}]
                    })
                else:  # user or default
                    contents.append({
                        "role": "user",
                        "parts": [{"text": content}]
                    })

            data = {
                "contents": contents,
                "generationConfig": {
                    "maxOutputTokens": max_tokens,
                    "temperature": temperature
                }
            }

            response = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
                headers=headers,
                json=data,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                # Extract the generated text from the response
                if "candidates" in data and len(data["candidates"]) > 0:
                    candidate = data["candidates"][0]
                    if "content" in candidate and "parts" in candidate["content"]:
                        parts = candidate["content"]["parts"]
                        if len(parts) > 0 and "text" in parts[0]:
                            return True, parts[0]["text"]

                logger.warning("Unexpected response format from Google API")
                return False, "Error: Unexpected response format from Google API"
            else:
                logger.warning("Google API request failed: %s", response.text)
                return False, f"Error: Google API request failed: {response.text}"
        except Exception as e:
            logger.error("Error chatting with Google: %s", e)
            return False, f"Error chatting with Google: {e}"

    def _chat_openrouter(self, messages: List[Dict[str, str]], model: str,
                          max_tokens: int, temperature: float) -> Tuple[bool, str]:
        """
        Chat with OpenRouter API.

        Args:
            messages: List of messages in the conversation
            model: Model to use
            max_tokens: Maximum number of tokens to generate
            temperature: Temperature for generation

        Returns:
            Tuple of (success, response_text)
        """
        if not self.openrouter_api_key:
            logger.warning("OpenRouter API key not set")
            return False, "Error: OpenRouter API key not set"

        try:
            headers = {
                "Authorization": f"Bearer {self.openrouter_api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://exo.ai",  # Required by OpenRouter
                "X-Title": "Exo Multi-Agent Framework"  # Optional but recommended
            }

            data = {
                "model": model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature
            }

            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                return True, data["choices"][0]["message"]["content"]
            else:
                logger.warning("OpenRouter API request failed: %s", response.text)
                return False, f"Error: OpenRouter API request failed: {response.text}"
        except Exception as e:
            logger.error("Error chatting with OpenRouter: %s", e)
            return False, f"Error chatting with OpenRouter: {e}"

    def _chat_ollama(self, messages: List[Dict[str, str]], model: str,
                     max_tokens: int, temperature: float) -> Tuple[bool, str]:
        """
        Chat with Ollama API.

        Args:
            messages: List of messages in the conversation
            model: Model to use
            max_tokens: Maximum number of tokens to generate
            temperature: Temperature for generation

        Returns:
            Tuple of (success, response_text)
        """
        try:
            headers = {
                "Content-Type": "application/json"
            }

            # Convert messages to Ollama format
            prompt = ""
            for message in messages:
                role = message.get("role", "user")
                content = message.get("content", "")

                if role == "system":
                    prompt += f"System: {content}\n\n"
                elif role == "user":
                    prompt += f"User: {content}\n\n"
                elif role == "assistant":
                    prompt += f"Assistant: {content}\n\n"

            data = {
                "model": model,
                "prompt": prompt,
                "options": {
                    "num_predict": max_tokens,
                    "temperature": temperature
                }
            }

            response = requests.post(
                f"{self.ollama_base_url}/api/generate",
                headers=headers,
                json=data,
                timeout=60  # Ollama can be slower, especially on first run
            )

            if response.status_code == 200:
                data = response.json()
                return True, data["response"]
            else:
                logger.warning("Ollama API request failed: %s", response.text)
                return False, f"Error: Ollama API request failed: {response.text}"
        except Exception as e:
            logger.error("Error chatting with Ollama: %s", e)
            return False, f"Error chatting with Ollama: {e}"

    def _chat_anthropic(self, messages: List[Dict[str, str]], model: str,
                       max_tokens: int, temperature: float) -> Tuple[bool, str]:
        """
        Chat with Anthropic API.

        Args:
            messages: List of messages in the conversation
            model: Model to use
            max_tokens: Maximum number of tokens to generate
            temperature: Temperature for generation

        Returns:
            Tuple of (success, response_text)
        """
        if not self.anthropic_api_key:
            logger.warning("Anthropic API key not set")
            return False, "Error: Anthropic API key not set"

        try:
            headers = {
                "x-api-key": self.anthropic_api_key,
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            }

            # Convert messages to Anthropic format
            prompt = ""
            for message in messages:
                role = message["role"]
                content = message["content"]

                if role == "user":
                    prompt += f"Human: {content}\n\n"
                elif role == "assistant":
                    prompt += f"Assistant: {content}\n\n"
                elif role == "system":
                    # Prepend system messages to the first user message
                    continue

            # Add final assistant prompt
            prompt += "Assistant:"

            data = {
                "model": model,
                "prompt": prompt,
                "max_tokens_to_sample": max_tokens,
                "temperature": temperature
            }

            response = requests.post(
                "https://api.anthropic.com/v1/complete",
                headers=headers,
                json=data,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                return True, data["completion"]
            else:
                logger.warning("Anthropic API request failed: %s", response.text)
                return False, f"Error: Anthropic API request failed: {response.text}"
        except Exception as e:
            logger.error("Error chatting with Anthropic: %s", e)
            return False, f"Error chatting with Anthropic: {e}"
