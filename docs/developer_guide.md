# exo Multi-Agent Framework Developer Guide

This guide provides detailed information for developers working on the exo Multi-Agent Framework.

## Architecture Overview

The exo Multi-Agent Framework is built around a hierarchical agent architecture:

1. **Primary Interface & Management Agent (PIA)**: The user's primary point of contact
2. **Command & Control Agent (CNC)**: Coordinates complex multi-domain tasks
3. **Domain Agents**: Specialized agents for specific tasks

The system is organized into the following components:

- **Core**: The main system components and orchestration
- **Agents**: Specialized agents for different domains
- **UI**: User interface components (Web-based UI with Flask and WebSockets)
- **Knowledge**: Knowledge storage and retrieval
- **Desktop**: Desktop context and control

## Development Environment Setup

### Prerequisites

- Python 3.10 or higher
- Git
- Node.js and npm (for Electron UI)

### Setting Up the Development Environment

1. Clone the repository:
```bash
git clone https://github.com/yourusername/exo.git
cd exo
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -e .
```

4. Install development dependencies:
```bash
pip install pytest pytest-cov flake8 black
```

## Code Structure

### Core Components

- `exo/core/system.py`: Main system class that initializes and manages all components
- `exo/core/service_registry.py`: Centralized registry for system-wide services
- `exo/core/onboarding.py`: Handles the onboarding process for configuration

### Agent Components

- `exo/agents/base_agent.py`: Base class for all agents
- `exo/agents/primary.py`: Primary Interface Agent
- `exo/agents/command_control.py`: Command & Control Agent
- `exo/agents/domain.py`: Base class for domain agents
- `exo/agents/llm_manager.py`: Manages interactions with Language Model providers
- `exo/agents/mcp_manager.py`: Manages interactions with MCP servers

### UI Components

- `exo/ui/web_server.py`: Web-based UI using Flask and WebSockets
- `exo/ui/electron_ui.py`: Native desktop UI using Electron
- `exo/ui/voice_interface.py`: Voice interaction capabilities

## Coding Standards

### Style Guide

- Follow PEP 8 for Python code
- Use Black for code formatting
- Use type hints for all function parameters and return values
- Use docstrings for all modules, classes, and functions

### Error Handling

- Use try-except blocks for error-prone operations
- Log errors with appropriate severity levels
- Provide meaningful error messages
- Return error status and messages for API calls

### Logging

- Use the Python logging module
- Log at appropriate levels:
  - DEBUG: Detailed information for debugging
  - INFO: Confirmation that things are working as expected
  - WARNING: Something unexpected happened, but the application still works
  - ERROR: The application has failed to perform some function
  - CRITICAL: The application is unable to continue running

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run tests with coverage report
pytest --cov=exo

# Run a specific test file
pytest exo/tests/test_service_registry.py
```

### Writing Tests

- Create a new test file for each module
- Use fixtures from `conftest.py` when possible
- Mock external dependencies
- Test both success and error cases

## Dependency Management

- Use `requirements.txt` for production dependencies
- Use `requirements-dev.txt` for development dependencies
- Pin dependency versions for stability

## Documentation

- Update the README.md file with any significant changes
- Document all public APIs with docstrings
- Keep the developer guide up to date

## Git Workflow

1. Create a feature branch from `main`:
```bash
git checkout -b feature/your-feature-name
```

2. Make your changes and commit them:
```bash
git add .
git commit -m "Description of your changes"
```

3. Push your branch to the remote repository:
```bash
git push origin feature/your-feature-name
```

4. Create a pull request on GitHub

5. After review and approval, merge the pull request

## Continuous Integration

The CI/CD pipeline runs the following checks:

- Linting with flake8
- Type checking with mypy
- Unit tests with pytest
- Code coverage with pytest-cov

Make sure all checks pass before merging your changes.

## Release Process

1. Update the version number in `setup.py`
2. Update the CHANGELOG.md file
3. Create a new release on GitHub
4. Tag the release with the version number
5. Publish the package to PyPI

## Troubleshooting

### Common Issues

- **Missing dependencies**: Make sure you have installed all required dependencies
- **Configuration issues**: Check the configuration files in `~/.exo/`
- **API key issues**: Verify that your API keys are correctly set
- **Port conflicts**: Make sure the ports used by the web server and WebSocket server are available

### Debugging

- Enable debug logging by setting the log level to DEBUG
- Use the `--debug` flag when running the application
- Check the logs in `~/.exo/logs/`
