# exo Multi-Agent Framework Troubleshooting Guide

This guide provides solutions for common issues you might encounter when using the exo Multi-Agent Framework.

## Installation Issues

### Python Version Compatibility

**Issue**: Error messages related to Python version compatibility.

**Solution**: Ensure you're using Python 3.10 or higher:
```bash
python --version
```

If you need to install a newer version of Python, visit the [Python downloads page](https://www.python.org/downloads/).

### Dependency Installation Failures

**Issue**: Errors when installing dependencies.

**Solution**: 
1. Make sure you have the latest version of pip:
```bash
pip install --upgrade pip
```

2. Install dependencies with verbose output to identify the specific issue:
```bash
pip install -e . -v
```

3. If you encounter issues with specific packages, try installing them individually:
```bash
pip install flask flask-socketio websockets
```

### Missing System Dependencies

**Issue**: Errors about missing system libraries.

**Solution**:
- On Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install -y python3-dev build-essential libasound2-dev portaudio19-dev
```

- On Fedora/RHEL/CentOS:
```bash
sudo dnf install -y python3-devel gcc alsa-lib-devel portaudio-devel
```

- On Arch Linux:
```bash
sudo pacman -S python-pip gcc alsa-lib portaudio
```

## Configuration Issues

### API Key Problems

**Issue**: Error messages about missing or invalid API keys.

**Solution**:
1. Run the onboarding process to set up your API keys:
```bash
python run_exo.py --onboard
```

2. Manually check your configuration file:
```bash
cat ~/.exo/config.json
```

3. If you need to reset your configuration:
```bash
python fix_onboarding.py
```

### MCP Server Connection Issues

**Issue**: Unable to connect to MCP servers.

**Solution**:
1. Check your MCP server configuration:
```bash
cat ~/.exo/mcp_servers.json
```

2. Verify that the server is running and accessible:
```bash
curl -I <server_url>
```

3. Add a new MCP server:
```bash
python run_exo.py --add-mcp-server
```

## Runtime Issues

### Web Server Fails to Start

**Issue**: The web server fails to start or is not accessible.

**Solution**:
1. Check if the port is already in use:
```bash
lsof -i :<port_number>
```

2. Try using a different port:
```bash
python run_exo.py --port 8081
```

3. Make sure you have the necessary permissions to bind to the port.

### WebSocket Connection Issues

**Issue**: WebSocket connection fails or disconnects frequently.

**Solution**:
1. Check if the WebSocket port is available:
```bash
lsof -i :<websocket_port>
```

2. Try using a different WebSocket port:
```bash
python run_exo.py --websocket-port 8766
```

3. Check for firewall or proxy issues that might be blocking WebSocket connections.

### LLM API Errors

**Issue**: Errors when calling LLM APIs.

**Solution**:
1. Verify that your API keys are correct and have sufficient quota.

2. Check the specific error message for details:
   - 401 errors indicate authentication issues
   - 429 errors indicate rate limiting
   - 500 errors indicate server issues

3. Try using a different LLM provider:
```bash
export DEFAULT_LLM_PROVIDER="anthropic"  # or "openrouter", "ollama"
```

### Voice Assistant Issues

**Issue**: Voice assistant not working or producing errors.

**Solution**:
1. Check if the required dependencies are installed:
```bash
pip install speech_recognition pyttsx3 pyaudio
```

2. Verify that your audio devices are properly configured:
```bash
python -c "import pyaudio; p = pyaudio.PyAudio(); print([p.get_device_info_by_index(i)['name'] for i in range(p.get_device_count())])"
```

3. Try using the simulation mode for testing:
```bash
python run_exo.py --voice --simulate-voice
```

## Container Environment Issues

### Binding to Interfaces

**Issue**: The web server is not accessible from outside the container.

**Solution**:
1. Make sure the server is binding to all interfaces:
```bash
python run_exo.py --host 0.0.0.0
```

2. Verify that the container port is properly mapped to the host:
```bash
docker run -p 8080:8080 -p 8765:8765 ...
```

### Audio Device Access

**Issue**: Unable to access audio devices in a container.

**Solution**:
1. Use the web-based voice input instead of direct microphone access:
```bash
python run_exo.py --voice --no-direct-mic
```

2. If you need direct audio access, make sure to pass the audio devices to the container:
```bash
docker run --device /dev/snd ...
```

## Electron UI Issues

### Electron UI Not Starting

**Issue**: The Electron UI fails to start.

**Solution**:
1. Check if Node.js and npm are installed:
```bash
node --version
npm --version
```

2. Install the required dependencies:
```bash
cd exo/ui/electron
npm install
```

3. Try running with the web UI instead:
```bash
python run_exo.py --no-electron
```

### Electron UI Not Connecting to Backend

**Issue**: The Electron UI starts but cannot connect to the backend.

**Solution**:
1. Make sure the backend is running and accessible.

2. Check the ports used by the backend:
```bash
python run_exo.py --port 8080 --websocket-port 8765
```

3. Verify that the Electron UI is configured to use the correct ports.

## Logging and Debugging

### Enabling Debug Logging

To get more detailed logs for troubleshooting:

1. Set the log level to DEBUG in your code:
```python
logging.basicConfig(level=logging.DEBUG)
```

2. Or set the environment variable:
```bash
export LOGLEVEL=DEBUG
```

### Checking Logs

Log files are stored in the following locations:

- Application logs: `~/.exo/logs/`
- Web server logs: Check the console output
- Electron UI logs: Check the Electron developer console (Ctrl+Shift+I)

## Getting Help

If you're still experiencing issues:

1. Check the [GitHub Issues](https://github.com/yourusername/exo/issues) for similar problems and solutions.

2. Create a new issue with:
   - A detailed description of the problem
   - Steps to reproduce
   - Error messages and logs
   - Your environment details (OS, Python version, etc.)

3. Join the community Discord server for real-time help.
