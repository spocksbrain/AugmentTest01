# exo Multi-Agent Framework User Guide

Welcome to the exo Multi-Agent Framework! This guide will help you get started and make the most of the system.

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Getting Started](#getting-started)
4. [User Interface Options](#user-interface-options)
5. [Voice Interaction](#voice-interaction)
6. [LLM Integration](#llm-integration)
7. [MCP Server Integration](#mcp-server-integration)
8. [Advanced Usage](#advanced-usage)
9. [Troubleshooting](#troubleshooting)

## Introduction

The exo Multi-Agent Framework is an advanced AI system designed to provide seamless interaction with users through a minimalist yet powerful interface. The system consists of a hierarchical arrangement of specialized AI agents working in concert to handle complex tasks across multiple domains.

## Installation

### Prerequisites

- Python 3.10 or higher
- Git (for cloning the repository)

### Installation Steps

1. Clone the repository:
```bash
git clone https://github.com/yourusername/exo.git
cd exo
```

2. Install the package:
```bash
pip install -e .
```

This will install all the required dependencies.

## Getting Started

### First Run and Onboarding

When you run the system for the first time, it will automatically start the onboarding process to help you set up the required configuration:

```bash
python run_exo.py
```

The onboarding process will:

1. Prompt for LLM API keys (OpenAI, Anthropic, OpenRouter, Ollama)
2. Prompt for MCP server connection details
3. Validate connections to ensure everything works
4. Store the configuration securely for future use

You can also manually run the onboarding process at any time:

```bash
python run_exo.py --onboard
```

### Basic Usage

Once the onboarding process is complete, you can start using the system:

1. Start the system:
```bash
python run_exo.py
```

2. A web browser will open automatically with the exo interface.

3. Type your message in the input field and press Enter or click the Send button.

4. The system will process your message and respond accordingly.

## User Interface Options

The exo Multi-Agent Framework offers several user interface options to suit your preferences and environment.

### Web UI

The default interface is a web-based UI that works in any modern browser:

```bash
python run_exo.py
```

You can customize the web UI with the following options:

- `--port`: Specify the port for the web server (default: 8080)
- `--websocket-port`: Specify the port for the WebSocket server (default: 8765)
- `--host`: Specify the host to bind to (default: localhost)
- `--no-browser`: Don't open a browser window automatically

### App Mode

You can run the web UI in app mode, which opens the UI in a standalone window without browser UI elements:

```bash
python run_exo.py --app-mode
```

This makes the web UI appear like a native desktop application.

### Electron UI

For a true native desktop experience, you can use the Electron UI:

```bash
python run_exo.py --electron
```

The Electron UI provides several advantages:

- Better system integration
- Improved performance
- Automatic container detection and connection
- Seamless integration with the backend

## Voice Interaction

The exo Multi-Agent Framework includes a voice assistant that allows you to interact with the system using voice commands.

### Enabling Voice Interaction

To enable voice interaction:

```bash
python run_exo.py --voice
```

By default, the voice assistant uses "exo" as the wake word. You can customize the wake word:

```bash
python run_exo.py --voice --wake-word "assistant"
```

### Voice Commands

Once the voice assistant is enabled, you can:

1. Activate it by saying the wake word (e.g., "exo")
2. Speak your command or question
3. The system will process your voice input and respond with synthesized speech

### Voice Options

The voice assistant offers several options:

- `--simulate-voice`: Use simulated voice commands for testing
- `--direct-mic`: Use direct microphone access instead of web-based voice input

## LLM Integration

The exo Multi-Agent Framework supports multiple LLM providers:

- **OpenAI**: GPT models (requires API key)
- **Anthropic**: Claude models (requires API key)
- **OpenRouter**: Access to multiple providers through a single API (requires API key)
- **Ollama**: Run models locally (requires Ollama to be installed)

### Configuring LLM Providers

You can configure the default provider and model during onboarding, or set them using environment variables:

```bash
export DEFAULT_LLM_PROVIDER="openai"  # Options: openai, anthropic, openrouter, ollama
export DEFAULT_LLM_MODEL="gpt-3.5-turbo"  # Model name for the selected provider
```

Each agent in the system can use a different LLM provider and model, while still having access to the centralized API keys.

## MCP Server Integration

The exo Multi-Agent Framework can connect to MCP servers for enhanced capabilities.

### Adding MCP Servers

You can add new MCP servers at any time:

```bash
python run_exo.py --add-mcp-server
```

This will guide you through the process of adding a new remote MCP server.

### Local MCP Servers

You can also install and add a local MCP server:

```bash
python run_exo.py --add-local-mcp
```

This will guide you through the process of installing a local MCP server on your machine.

## Advanced Usage

### Running Without UI

You can run the system without a UI for headless environments:

```bash
python run_exo.py --no-ui
```

### Container Environments

When running in a container environment, the system will automatically detect it and bind to all interfaces (0.0.0.0) to allow external connections.

For container environments, you can use the following options:

- `--no-browser`: Don't try to open a browser window
- `--host 0.0.0.0`: Bind to all interfaces (done automatically in containers)

### Command Line Options

The exo Multi-Agent Framework offers many command line options:

```
usage: run_exo.py [-h] [--no-ui] [--no-browser] [--auto-install] [--host HOST] [--port PORT] [--websocket-port WEBSOCKET_PORT] [--skip-onboarding] [--add-mcp-server]
                  [--add-local-mcp] [--onboard] [--voice] [--wake-word WAKE_WORD] [--app-mode] [--simulate-voice] [--direct-mic] [--electron] [--no-electron]

Run the exo Multi-Agent Framework

options:
  -h, --help            show this help message and exit
  --no-ui               Run without UI
  --no-browser          Don't open browser automatically
  --auto-install        Automatically install missing dependencies without asking
  --host HOST           Host to bind the web server to
  --port PORT           Port for the web server
  --websocket-port WEBSOCKET_PORT
                        Port for the WebSocket server
  --skip-onboarding     Skip the onboarding process
  --add-mcp-server      Add a new MCP server
  --add-local-mcp       Install and add a local MCP server
  --onboard             Run the onboarding process
  --voice               Enable voice assistant
  --wake-word WAKE_WORD
                        Wake word for voice assistant
  --app-mode            Launch browser in app mode (standalone window)
  --simulate-voice      Use simulated voice commands (for testing)
  --direct-mic          Use direct microphone access instead of web-based voice input
  --electron            Use Electron UI instead of web UI
  --no-electron         Disable Electron UI even if available
```

## Troubleshooting

If you encounter issues with the exo Multi-Agent Framework, please refer to the [Troubleshooting Guide](troubleshooting.md) for solutions to common problems.

For more detailed information, check the [Developer Guide](developer_guide.md) or visit the [GitHub repository](https://github.com/yourusername/exo).
