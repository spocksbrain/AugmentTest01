# exo Multi-Agent Framework

"exo" is an advanced multi-agent AI system designed to provide seamless interaction with users through a minimalist yet powerful interface. The system consists of a hierarchical arrangement of specialized AI agents working in concert to handle complex tasks across multiple domains.

## Core Architecture

The system is built around three main components:

1. **Primary Interface & Management Agent (PIA)**: The user's primary point of contact
2. **Command & Control Agent (CNC)**: Coordinates complex multi-domain tasks
3. **Domain Agents**: Specialized agents for specific tasks

## Getting Started

### Prerequisites

- Python 3.10 or higher
- Node.js and npm (for UI components)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/exo.git
cd exo

# Install Python dependencies
pip install -e .

# Install UI dependencies
cd ui
npm install
```

## Usage

```python
from exo.core import ExoSystem

# Initialize the exo system
exo_system = ExoSystem()

# Start the system
exo_system.start()
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
