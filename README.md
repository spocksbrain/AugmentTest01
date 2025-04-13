# exo Multi-Agent Framework

"exo" is an advanced multi-agent AI system designed to provide seamless interaction with users through a minimalist yet powerful interface. The system consists of a hierarchical arrangement of specialized AI agents working in concert to handle complex tasks across multiple domains.

## Project Structure

The project is organized into the following components:

- **Core**: The main system components and orchestration
- **Agents**: Specialized agents for different domains
- **UI**: User interface components (Web-based UI with Flask and WebSockets)
- **Knowledge**: Knowledge storage and retrieval
- **Desktop**: Desktop context and control

## Getting Started

### Prerequisites

- Python 3.10 or higher
- Flask, Flask-SocketIO, and websockets Python packages (automatically installed by the `install_dependencies.sh` script)

**Note:** The system uses a web-based UI that works in any modern browser, making it compatible with all environments including containers. When running in a container environment, the system will automatically bind to all interfaces (0.0.0.0) to allow external connections.

### Onboarding Process

The system includes an onboarding process that helps you set up the required environment variables and connections for LLM and MCP server integration. When you run the system for the first time, it will automatically start the onboarding process if no configuration is found.

You can also manually run the onboarding process at any time with:

```bash
python run_exo.py --onboard
```

The onboarding process will:

1. Prompt for LLM API keys (OpenAI, Anthropic, Google, OpenRouter, Ollama)
2. Prompt for MCP server connection details
3. Validate connections to ensure everything works
4. Store the configuration securely for future use

### LLM Integration

The system supports multiple LLM providers:

- **OpenAI**: GPT models (requires API key)
- **Anthropic**: Claude models (requires API key)
- **Google**: Gemini models (requires API key)
- **OpenRouter**: Access to multiple providers through a single API (requires API key)
- **Ollama**: Run models locally (requires Ollama to be installed)

You can configure the default provider and model during onboarding, or set them using environment variables:

```bash
export DEFAULT_LLM_PROVIDER="openai"  # Options: openai, anthropic, google, openrouter, ollama
export DEFAULT_LLM_MODEL="gpt-3.5-turbo"  # Model name for the selected provider
```

Each agent in the system can use a different LLM provider and model, while still having access to the centralized API keys. This allows for flexibility in choosing the right model for each task.

### Native Desktop UI (Electron)

The system can be launched with a native desktop UI using Electron, which provides a true native application experience. This is the recommended approach for desktop environments.

To run the system with the Electron UI:

```bash
python run_exo.py --electron
```

The Electron UI provides several advantages:

- True native application experience
- Better system integration
- Improved performance
- Automatic container detection and connection
- Seamless integration with the backend

The Electron UI is automatically detected and used if available, unless the `--no-electron` flag is specified.

### App Mode (Standalone Window)

Alternatively, the system can be launched in app mode, which opens the UI in a standalone window without browser UI elements, making it appear like a native desktop application. This is especially useful for container environments where you want a more integrated experience.

To run the system in app mode:

```bash
python run_exo.py --app-mode
```

In container environments, the system will detect that it's running in a container and provide instructions for manually opening the UI in app mode. You can use the provided script to open the UI in app mode from your host machine:

```bash
./open_in_app_mode.sh [host] [port]
```

This script will attempt to open the UI in app mode using various browsers (Chrome, Chromium, Edge, Brave) depending on what's available on your system.

### Voice Interaction

The system includes a voice assistant that allows you to interact with the PIA using voice commands. The voice assistant uses speech recognition and text-to-speech to provide a natural interface for interacting with the system.

To enable the voice assistant, use the `--voice` flag when starting the system:

```bash
python run_exo.py --voice
```

By default, the voice assistant uses "exo" as the wake word. You can customize the wake word using the `--wake-word` option:

```bash
python run_exo.py --voice --wake-word "assistant"
```

The voice assistant requires the following Python packages:

- `speech_recognition` - For speech-to-text functionality
- `pyttsx3` or `gtts` + `pygame` - For text-to-speech functionality
- `pyaudio` - For audio recording and playback

These packages will be automatically installed when you run the system with the `--voice` flag for the first time.

### MCP Server Integration

#### Discovering MCP Server Solutions

The system includes an MCP Server Agent that can help you discover existing MCP server solutions based on your requirements. You can ask the agent to find MCP servers for specific use cases, and it will present you with a list of options, including:

- Official MCP servers from the Model Context Protocol repository
- Community-built MCP servers
- Custom MCP server implementation option

For each option, the agent will provide information about:

- Features and capabilities
- Installation requirements
- API documentation
- Recommended use cases

To discover MCP server solutions, simply ask the agent something like:

- "Find MCP server solutions for GitHub integration"
- "What MCP servers are available for file system access?"
- "Show me options for MCP servers"

The agent will search for relevant solutions and present them to you, along with a recommendation based on your requirements.

#### Adding MCP Servers

You can add new MCP servers at any time. There are two options:

##### Remote MCP Servers

To add a remote MCP server:

```bash
python run_exo.py --add-mcp-server
```

This will guide you through the process of adding a new remote MCP server, including:

1. Entering the server name and URL
2. Providing the API key for authentication
3. Testing the connection to ensure it works
4. Storing the server configuration for future use

##### Local MCP Servers

To install and add a local MCP server:

```bash
python run_exo.py --add-local-mcp
```

This will guide you through the process of installing a local MCP server on your machine, including:

1. Installing required dependencies
2. Setting up the server environment
3. Configuring the server for first use
4. Starting the server automatically
5. Storing the server configuration for future use

Local MCP servers are useful for development and testing, or when you don't have access to a remote MCP server. They run on your local machine and provide the same functionality as remote servers.

### Agent Access to MCP Servers

All agents in the system have access to both local and remote MCP servers through the centralized service registry. The system uses a dependency injection pattern to ensure that all agents have consistent access to shared services.

When new agents are added to the system, they automatically gain access to all configured MCP servers without any additional configuration. This is achieved through the `BaseAgent` class, which provides access to the MCP manager service.

Agents can interact with MCP servers using methods like:

```python
# Send a request to the default MCP server
result = agent.send_mcp_request("/api/endpoint")

# Send a request to a specific MCP server
result = agent.send_mcp_request("/api/endpoint", server_id="my_server_id")
```

This ensures that all agents in the system have consistent access to MCP servers, regardless of whether they are local or remote.

### Supported Platforms

The system supports automatic dependency installation on the following platforms:

- Ubuntu/Debian: Using apt-get
- Fedora/RHEL/CentOS: Using dnf
- Arch Linux: Using pacman

For other platforms, the system will provide instructions for manual installation.

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/exo.git
cd exo
```

2. Install dependencies:

You can use the provided script to automatically install all required dependencies:
```bash
./install_dependencies.sh
```

Or install them manually:
```bash
# For Ubuntu/Debian
# Install Python and pip if not already installed
sudo apt-get install -y python3 python3-pip

# Install required Python packages
pip install flask flask-socketio websockets
```

3. Install Python dependencies:
```bash
pip install -e .
```

### Running the System

1. Run the system with the provided script:
```bash
# Run with web UI (will open a browser automatically)
python run_exo.py

# Run without UI
python run_exo.py --no-ui

# Run with UI but don't open browser automatically
python run_exo.py --no-browser

# Run with UI in app mode (standalone window)
python run_exo.py --app-mode

# Run with Electron UI (native desktop application)
python run_exo.py --electron

# Run without Electron UI even if available
python run_exo.py --no-electron

# Run with UI on a specific host and port
python run_exo.py --host 0.0.0.0 --port 8888

# Run with UI and automatically install missing dependencies without asking
python run_exo.py --auto-install

# Run the onboarding process to set up LLM and MCP server connections
python run_exo.py --onboard

# Add a new remote MCP server
python run_exo.py --add-mcp-server

# Install and add a local MCP server
python run_exo.py --add-local-mcp

# Skip the onboarding process (useful for CI/CD environments)
python run_exo.py --skip-onboarding

# Enable voice assistant with default wake word ("exo")
python run_exo.py --voice

# Enable voice assistant with custom wake word
python run_exo.py --voice --wake-word "assistant"
```

Alternatively, you can start the components separately:

```bash
# Start the Python backend with web UI
python -m exo.main

# Start the Python backend without UI
python -m exo.main --no-ui

# Start the Python backend with UI on a specific host and port
python -m exo.main --host 0.0.0.0 --port 8888

# Run the onboarding process
python -m exo.main --onboard

# Add a new remote MCP server
python -m exo.main --add-mcp-server

# Install and add a local MCP server
python -m exo.main --add-local-mcp

# The web UI is automatically started by the backend
```

## Architecture

The system is built around three main components:

1. **Primary Interface & Management Agent (PIA)**: The user's primary point of contact
2. **Command & Control Agent (CNC)**: Coordinates complex multi-domain tasks
3. **Domain Agents**: Specialized agents for specific tasks

## License

This project is licensed under the MIT License - see the LICENSE file for details.
