"""
Voice Interface for the exo Multi-Agent Framework

This module provides voice interaction capabilities for the exo system,
including speech-to-text and text-to-speech functionality.
"""

import os
import sys
import time
import queue
import logging
import threading
import tempfile
from typing import Optional, Callable, Dict, Any, List, Tuple

import numpy as np

logger = logging.getLogger(__name__)

# Try to import optional dependencies
STT_AVAILABLE = False
TTS_AVAILABLE = False
AUDIO_AVAILABLE = False

try:
    import speech_recognition as sr
    STT_AVAILABLE = True
except ImportError:
    logger.warning("speech_recognition not found. Speech-to-text will not be available.")

try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    try:
        from gtts import gTTS
        import pygame
        TTS_AVAILABLE = True
    except ImportError:
        logger.warning("Neither pyttsx3 nor gtts+pygame found. Text-to-speech will not be available.")

try:
    import pyaudio
    import wave
    # Create a dummy audio device for testing
    try:
        p = pyaudio.PyAudio()
        # Check if we can open a stream
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=1024)
        stream.close()
        p.terminate()
        AUDIO_AVAILABLE = True
    except Exception as e:
        logger.warning(f"Audio device not available: {e}")
        # Use a dummy device
        AUDIO_AVAILABLE = False
except ImportError:
    logger.warning("pyaudio not found. Audio recording will not be available.")
    AUDIO_AVAILABLE = False


class VoiceInterface:
    """
    Voice Interface for the exo Multi-Agent Framework

    This class provides voice interaction capabilities for the exo system,
    including speech-to-text and text-to-speech functionality.
    """

    def __init__(self,
                 wake_word: str = "exo",
                 stt_engine: str = "google",
                 tts_engine: str = "pyttsx3",
                 language: str = "en-US",
                 use_simulation: bool = True,
                 prefer_web_input: bool = True):
        """
        Initialize the voice interface.

        Args:
            wake_word: Wake word to activate the system
            stt_engine: Speech-to-text engine to use
            tts_engine: Text-to-speech engine to use
            language: Language code to use
            use_simulation: Whether to use simulation mode when audio is not available
            prefer_web_input: Whether to prefer web-based voice input over direct microphone access
        """
        self.wake_word = wake_word.lower()
        self.stt_engine = stt_engine
        self.tts_engine = tts_engine
        self.language = language
        self.use_simulation = use_simulation
        self.prefer_web_input = prefer_web_input

        # Initialize speech recognition
        self.recognizer = None
        if STT_AVAILABLE:
            self.recognizer = sr.Recognizer()
            # Adjust for ambient noise when first created
            self.adjust_for_ambient_noise()

        # Initialize text-to-speech
        self.tts = None
        if TTS_AVAILABLE:
            if tts_engine == "pyttsx3" and "pyttsx3" in sys.modules:
                self.tts = pyttsx3.init()
                # Set properties
                self.tts.setProperty('rate', 150)  # Speed of speech
                self.tts.setProperty('volume', 0.9)  # Volume (0.0 to 1.0)

                # Get available voices and set to a female voice if available
                voices = self.tts.getProperty('voices')
                for voice in voices:
                    if "female" in voice.name.lower():
                        self.tts.setProperty('voice', voice.id)
                        break
            elif "gtts" in sys.modules and "pygame" in sys.modules:
                self.tts = "gtts"  # Just a marker, we'll use gTTS directly

        # Audio recording settings
        self.audio_format = pyaudio.paInt16 if AUDIO_AVAILABLE else None
        self.channels = 1
        self.rate = 16000
        self.chunk = 1024
        self.record_seconds = 5

        # State
        self.is_listening = False
        self.audio_queue = queue.Queue()
        self.listening_thread = None
        self.callback = None

        logger.info("Voice interface initialized")
        logger.info(f"STT available: {STT_AVAILABLE}")
        logger.info(f"TTS available: {TTS_AVAILABLE}")
        logger.info(f"Audio available: {AUDIO_AVAILABLE}")

    def adjust_for_ambient_noise(self, duration: float = 1.0) -> bool:
        """
        Adjust the recognizer for ambient noise.

        Args:
            duration: Duration to listen for ambient noise

        Returns:
            True if successful, False otherwise
        """
        if not STT_AVAILABLE or not AUDIO_AVAILABLE:
            return False

        try:
            with sr.Microphone() as source:
                logger.info(f"Adjusting for ambient noise (duration: {duration}s)")
                self.recognizer.adjust_for_ambient_noise(source, duration=duration)
                logger.info("Ambient noise adjustment complete")
                return True
        except Exception as e:
            logger.error(f"Error adjusting for ambient noise: {e}")
            return False

    def listen_once(self, timeout: Optional[float] = None) -> Optional[str]:
        """
        Listen for speech and convert to text.

        Args:
            timeout: Timeout in seconds, or None for no timeout

        Returns:
            Recognized text, or None if no speech was recognized
        """
        if not STT_AVAILABLE:
            logger.error("Speech recognition not available")
            return None

        # Determine which listening mode to use
        if not AUDIO_AVAILABLE:
            # No audio hardware available
            if self.use_simulation:
                # Use simulation mode
                logger.info("Using simulated speech input (no audio device available)")
                return "hello exo"
            else:
                # Use web-based voice input
                logger.info("Using web-based voice input (no audio device available)")
                return None
        else:
            # Audio hardware is available
            if self.prefer_web_input:
                # Prefer web-based voice input even though hardware is available
                logger.info("Using web-based voice input (hardware available but web input preferred)")
                return None

        try:
            with sr.Microphone() as source:
                logger.info("Listening...")
                audio = self.recognizer.listen(source, timeout=timeout)
                return self._recognize_audio(audio)
        except sr.WaitTimeoutError:
            logger.info("Listening timed out")
            return None
        except sr.UnknownValueError:
            logger.info("Speech not recognized")
            return None
        except sr.RequestError as e:
            logger.error(f"Error with speech recognition service: {e}")
            return None
        except Exception as e:
            logger.error(f"Error listening: {e}")
            return None

    def recognize_from_file(self, file_path: str) -> Optional[str]:
        """
        Recognize speech from an audio file.

        Args:
            file_path: Path to the audio file

        Returns:
            Recognized text, or None if no speech was recognized
        """
        if not STT_AVAILABLE:
            logger.error("Speech recognition not available")
            return None

        try:
            logger.info(f"Recognizing speech from file: {file_path}")
            with sr.AudioFile(file_path) as source:
                audio = self.recognizer.record(source)
                return self._recognize_audio(audio)
        except Exception as e:
            logger.error(f"Error recognizing speech from file: {e}")
            return None

    def _recognize_audio(self, audio) -> Optional[str]:
        """
        Recognize speech from an audio data object.

        Args:
            audio: Audio data from recognizer

        Returns:
            Recognized text, or None if no speech was recognized
        """
        try:
            logger.info("Processing speech...")
            if self.stt_engine == "google":
                text = self.recognizer.recognize_google(audio, language=self.language)
            elif self.stt_engine == "sphinx":
                text = self.recognizer.recognize_sphinx(audio, language=self.language)
            else:
                logger.error(f"Unsupported STT engine: {self.stt_engine}")
                return None

            logger.info(f"Recognized: {text}")
            return text
        except sr.UnknownValueError:
            logger.info("Speech not recognized")
            return None
        except sr.RequestError as e:
            logger.error(f"Error with speech recognition service: {e}")
            return None
        except Exception as e:
            logger.error(f"Error recognizing speech: {e}")
            return None

    def start_listening(self, callback: Callable[[str], None]) -> bool:
        """
        Start listening for speech in the background.

        Args:
            callback: Function to call with recognized text

        Returns:
            True if listening started successfully, False otherwise
        """
        if not STT_AVAILABLE:
            logger.error("Speech recognition not available")
            return False

        if self.is_listening:
            logger.warning("Already listening")
            return False

        self.callback = callback
        self.is_listening = True

        # Determine which listening mode to use
        if not AUDIO_AVAILABLE:
            # No audio hardware available
            if self.use_simulation:
                # Use simulation mode
                logger.info("Using simulated listening (no audio device available)")
                self.listening_thread = threading.Thread(target=self._simulate_listen_loop)
            else:
                # Use web-based voice input
                logger.info("Using web-based voice input (no audio device available)")
                self.listening_thread = threading.Thread(target=self._dummy_listen_loop)
        else:
            # Audio hardware is available
            if self.prefer_web_input:
                # Prefer web-based voice input even though hardware is available
                logger.info("Using web-based voice input (hardware available but web input preferred)")
                self.listening_thread = threading.Thread(target=self._dummy_listen_loop)
            else:
                # Use direct microphone access
                logger.info("Using direct microphone access")
                self.listening_thread = threading.Thread(target=self._listen_loop)

        self.listening_thread.daemon = True
        self.listening_thread.start()

        logger.info("Started listening in background")
        return True

    def stop_listening(self) -> bool:
        """
        Stop listening for speech.

        Returns:
            True if listening was stopped, False otherwise
        """
        if not self.is_listening:
            logger.warning("Not listening")
            return False

        self.is_listening = False
        if self.listening_thread:
            self.listening_thread.join(timeout=1.0)
            self.listening_thread = None

        logger.info("Stopped listening")
        return True

    def _dummy_listen_loop(self) -> None:
        """Dummy listening loop for web-based voice input."""
        # This loop does nothing but keep the thread alive
        # Voice input will come from the web UI through the process_voice_message method
        logger.info("Started dummy listening loop for web-based voice input")

        # Just keep the thread alive until stopped
        while self.is_listening:
            time.sleep(1.0)

    def _simulate_listen_loop(self) -> None:
        """Simulated background listening loop for testing without audio hardware."""
        # Immediately simulate a command when starting
        if self.callback:
            logger.info("Simulating initial voice command: help")
            self.callback("help")

        while self.is_listening:
            try:
                # Simulate hearing the wake word every 3 seconds
                time.sleep(3.0)

                if self.callback:
                    # Simulate different commands for testing
                    commands = [
                        "hello",
                        "what time is it",
                        "tell me a joke",
                        "help"
                    ]
                    # Use the current time to select a command
                    command_index = int(time.time()) % len(commands)
                    command = commands[command_index]
                    logger.info(f"Simulating voice command: {command}")
                    self.callback(command)

            except Exception as e:
                logger.error(f"Error in simulated listening loop: {e}")
                time.sleep(1.0)  # Avoid tight loop on error

    def _listen_loop(self) -> None:
        """Background listening loop."""
        while self.is_listening:
            try:
                text = self.listen_once(timeout=1.0)
                if text:
                    # Check for wake word if specified
                    if not self.wake_word or self.wake_word in text.lower():
                        # Remove wake word from text
                        if self.wake_word:
                            text = text.lower().replace(self.wake_word, "").strip()

                        if text and self.callback:
                            self.callback(text)
            except Exception as e:
                logger.error(f"Error in listening loop: {e}")
                time.sleep(1.0)  # Avoid tight loop on error

    def speak(self, text: str) -> bool:
        """
        Convert text to speech.

        Args:
            text: Text to speak

        Returns:
            True if successful, False otherwise
        """
        if not TTS_AVAILABLE:
            logger.error("Text-to-speech not available")
            return False

        try:
            if isinstance(self.tts, pyttsx3.Engine):
                # Use pyttsx3
                self.tts.say(text)
                self.tts.runAndWait()
                return True
            elif self.tts == "gtts":
                # Use gTTS and pygame
                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
                    temp_filename = temp_file.name

                # Create the gTTS object and save to temp file
                tts = gTTS(text=text, lang=self.language[:2])
                tts.save(temp_filename)

                # Play the audio
                pygame.mixer.init()
                pygame.mixer.music.load(temp_filename)
                pygame.mixer.music.play()

                # Wait for the audio to finish playing
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)

                # Clean up
                pygame.mixer.quit()
                os.unlink(temp_filename)

                return True
            else:
                logger.error("No TTS engine available")
                return False
        except Exception as e:
            logger.error(f"Error speaking: {e}")
            return False

    def record_audio(self, duration: float = 5.0) -> Optional[bytes]:
        """
        Record audio from the microphone.

        Args:
            duration: Duration to record in seconds

        Returns:
            Audio data as bytes, or None if recording failed
        """
        if not AUDIO_AVAILABLE:
            logger.error("Audio recording not available")
            return None

        try:
            p = pyaudio.PyAudio()
            stream = p.open(format=self.audio_format,
                           channels=self.channels,
                           rate=self.rate,
                           input=True,
                           frames_per_buffer=self.chunk)

            logger.info(f"Recording for {duration} seconds...")
            frames = []

            for i in range(0, int(self.rate / self.chunk * duration)):
                data = stream.read(self.chunk)
                frames.append(data)

            logger.info("Recording complete")

            stream.stop_stream()
            stream.close()
            p.terminate()

            # Convert frames to bytes
            audio_data = b''.join(frames)
            return audio_data
        except Exception as e:
            logger.error(f"Error recording audio: {e}")
            return None

    def save_audio(self, audio_data: bytes, filename: str) -> bool:
        """
        Save audio data to a file.

        Args:
            audio_data: Audio data as bytes
            filename: Filename to save to

        Returns:
            True if successful, False otherwise
        """
        if not AUDIO_AVAILABLE:
            logger.error("Audio recording not available")
            return False

        try:
            p = pyaudio.PyAudio()
            wf = wave.open(filename, 'wb')
            wf.setnchannels(self.channels)
            wf.setsampwidth(p.get_sample_size(self.audio_format))
            wf.setframerate(self.rate)
            wf.writeframes(audio_data)
            wf.close()
            p.terminate()

            logger.info(f"Audio saved to {filename}")
            return True
        except Exception as e:
            logger.error(f"Error saving audio: {e}")
            return False

    def is_available(self) -> bool:
        """
        Check if voice interaction is available.

        Returns:
            True if both STT and TTS are available, False otherwise
        """
        # We need at least STT and TTS for basic voice interaction
        # Audio recording is optional for some features
        return STT_AVAILABLE and TTS_AVAILABLE
