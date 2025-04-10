"""
Voice Assistant Agent for the exo Multi-Agent Framework

This module provides a voice assistant agent that can interact with the user
through voice commands and respond with synthesized speech.
"""

import os
import time
import logging
import threading
from typing import Dict, List, Optional, Any, Tuple, Callable

from exo.agents.base_agent import BaseAgent
from exo.ui.voice_interface import VoiceInterface

logger = logging.getLogger(__name__)

class VoiceAssistantAgent(BaseAgent):
    """
    Voice Assistant Agent for the exo Multi-Agent Framework

    This agent provides voice interaction capabilities, allowing users to
    interact with the system through voice commands and receive responses
    through synthesized speech.
    """

    def __init__(self, name: str = "Voice Assistant",
                 llm_provider: Optional[str] = None,
                 llm_model: Optional[str] = None,
                 wake_word: str = "exo",
                 language: str = "en-US",
                 use_simulation: bool = False,
                 prefer_web_input: bool = True):
        """
        Initialize the Voice Assistant Agent.

        Args:
            name: Name of the agent
            llm_provider: LLM provider to use (if None, uses default)
            llm_model: LLM model to use (if None, uses default)
            wake_word: Wake word to activate the assistant
            language: Language code to use
            use_simulation: Whether to use simulation mode when audio is not available
            prefer_web_input: Whether to prefer web-based voice input over direct microphone access
        """
        super().__init__(name, "voice_assistant", llm_provider, llm_model)

        self.wake_word = wake_word
        self.language = language
        self.use_simulation = use_simulation
        self.prefer_web_input = prefer_web_input

        # Initialize voice interface
        self.voice = VoiceInterface(
            wake_word=wake_word,
            language=language,
            use_simulation=use_simulation,
            prefer_web_input=prefer_web_input
        )

        # State
        self.is_active = False
        self.listening_thread = None
        self.command_handlers = {}

        # Register default command handlers
        self._register_default_handlers()

        # Capabilities
        self.capabilities = [
            "voice_interaction",
            "speech_recognition",
            "text_to_speech",
            "command_processing"
        ]

        logger.info(f"Voice Assistant Agent initialized (wake word: {wake_word})")

    def _register_default_handlers(self):
        """Register default command handlers."""
        self.register_command("help", self._handle_help)
        self.register_command("stop", self._handle_stop)
        self.register_command("quit", self._handle_stop)
        self.register_command("exit", self._handle_stop)

    def register_command(self, command: str, handler: Callable[[str], str]) -> None:
        """
        Register a command handler.

        Args:
            command: Command to handle (lowercase)
            handler: Function to call when the command is recognized
        """
        self.command_handlers[command.lower()] = handler
        logger.info(f"Registered command handler for '{command}'")

    def start(self) -> bool:
        """
        Start the voice assistant.

        Returns:
            True if started successfully, False otherwise
        """
        if self.is_active:
            logger.warning("Voice assistant is already active")
            return False

        if not self.voice.is_available():
            logger.error("Voice interface is not available")
            return False

        # Start listening for commands if audio recording is available
        self.is_active = True

        # Start listening for commands
        success = self.voice.start_listening(self._process_voice_command)

        if success:
            logger.info("Voice assistant started successfully")
            self.voice.speak(f"Hello, I'm {self.name}. How can I help you?")
            return True
        else:
            logger.error("Failed to start voice assistant")
            self.is_active = False
            return False

    def stop(self) -> bool:
        """
        Stop the voice assistant.

        Returns:
            True if stopped successfully, False otherwise
        """
        if not self.is_active:
            logger.warning("Voice assistant is not active")
            return False

        # Stop listening for commands if we were listening
        self.is_active = False

        # Check if we were listening
        from exo.ui.voice_interface import AUDIO_AVAILABLE

        if AUDIO_AVAILABLE:
            success = self.voice.stop_listening()
            if not success:
                logger.error("Failed to stop voice assistant listening")
                # Continue with shutdown anyway

        logger.info("Voice assistant stopped")
        return True

    def _process_voice_command(self, command: str) -> None:
        """
        Process a voice command.

        Args:
            command: Command to process
        """
        logger.info(f"Processing voice command: {command}")

        # Check for specific commands
        command_lower = command.lower()

        # Find matching command handler
        handler = None
        matched_command = None

        for cmd, hdlr in self.command_handlers.items():
            if command_lower.startswith(cmd):
                # If we already found a handler, use the longer command
                if handler is None or len(cmd) > len(matched_command):
                    handler = hdlr
                    matched_command = cmd

        if handler:
            # Extract arguments (everything after the command)
            args = command[len(matched_command):].strip()

            # Call the handler
            try:
                response = handler(args)
                if response:
                    self.voice.speak(response)
            except Exception as e:
                logger.error(f"Error handling command '{matched_command}': {e}")
                self.voice.speak(f"Sorry, I had a problem processing that command.")
        else:
            # No specific handler, use LLM to generate a response
            self._handle_general_command(command)

    def process_voice_message(self, message_data: Dict) -> None:
        """
        Process a voice message from the web UI.

        Args:
            message_data: Dictionary containing the audio file path
        """
        try:
            audio_path = message_data.get("audio_path")
            if not audio_path or not os.path.exists(audio_path):
                logger.error(f"Invalid audio path: {audio_path}")
                return

            logger.info(f"Processing voice message from file: {audio_path}")

            # Use the voice interface to recognize speech from the file
            text = self.voice.recognize_from_file(audio_path)

            if text:
                logger.info(f"Recognized text from voice message: {text}")
                # Process the recognized text as a voice command
                self._process_voice_command(text)
            else:
                logger.warning("Could not recognize speech from voice message")
                # Inform the user that we couldn't understand the message
                self.voice.speak("I'm sorry, I couldn't understand your voice message.")

            # Clean up the temporary file
            try:
                os.remove(audio_path)
                logger.info(f"Removed temporary audio file: {audio_path}")
            except Exception as e:
                logger.warning(f"Error removing temporary audio file: {e}")

        except Exception as e:
            logger.error(f"Error processing voice message: {e}")
            self.voice.speak("I'm sorry, there was an error processing your voice message.")

    def _handle_general_command(self, command: str) -> None:
        """
        Handle a general command using the LLM.

        Args:
            command: Command to process
        """
        # Generate a prompt for the LLM
        prompt = f"User: {command}\n\nProvide a helpful, concise response:"

        # Generate a response using the LLM
        success, response = self.generate_text(prompt)

        if success:
            # Speak the response
            self.voice.speak(response)
        else:
            logger.error(f"Failed to generate response: {response}")
            self.voice.speak("Sorry, I couldn't generate a response.")

    def _handle_help(self, args: str) -> str:
        """
        Handle the 'help' command.

        Args:
            args: Command arguments

        Returns:
            Response to speak
        """
        commands = list(self.command_handlers.keys())
        return f"Available commands: {', '.join(commands)}. You can also ask me general questions."

    def _handle_stop(self, args: str) -> str:
        """
        Handle the 'stop' command.

        Args:
            args: Command arguments

        Returns:
            Response to speak
        """
        # Schedule stopping after response is spoken
        threading.Timer(1.0, self.stop).start()
        return "Stopping voice assistant. Goodbye!"

    def process_message(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Process a message.

        Args:
            message: Message to process

        Returns:
            Response message, or None if no response
        """
        message_type = message.get("type")
        content = message.get("content")

        if message_type == "command":
            # Process a command
            if content == "start":
                success = self.start()
                return {
                    "type": "response",
                    "success": success,
                    "content": "Voice assistant started" if success else "Failed to start voice assistant"
                }
            elif content == "stop":
                success = self.stop()
                return {
                    "type": "response",
                    "success": success,
                    "content": "Voice assistant stopped" if success else "Failed to stop voice assistant"
                }
            elif content == "status":
                return {
                    "type": "response",
                    "success": True,
                    "content": "Voice assistant is active" if self.is_active else "Voice assistant is not active",
                    "is_active": self.is_active
                }
        elif message_type == "speak":
            # Speak a message
            if content:
                success = self.voice.speak(content)
                return {
                    "type": "response",
                    "success": success,
                    "content": "Message spoken" if success else "Failed to speak message"
                }

        return super().process_message(message)
