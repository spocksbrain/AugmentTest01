# exo Electron UI

This is the Electron-based desktop UI for the exo Multi-Agent Framework. It provides a native desktop application experience for interacting with the exo backend running in a container.

## Features

- Native desktop application experience
- Automatic container detection and connection
- Seamless integration with the exo backend
- Cross-platform support (Windows, macOS, Linux)
- Dependency management and auto-installation

## Development

### Prerequisites

- Node.js 14+
- npm 6+
- Electron 25+

### Installation

```bash
# Install dependencies
npm install
```

### Running in Development Mode

```bash
# Start the Electron app in development mode
npm start
```

### Building for Production

```bash
# Build for all platforms
npm run build

# Build for specific platforms
npm run build:win
npm run build:mac
npm run build:linux
```

## Container Integration

The Electron UI is designed to connect to the exo backend running in a Docker container. It automatically detects running containers and allows the user to select which one to connect to.

### How it Works

1. The Electron app starts and checks for Docker installation
2. It lists all running Docker containers
3. The user selects a container to connect to
4. The app connects to the WebSocket server running in the container
5. All communication happens over WebSockets

### Configuration

The app stores connection settings in the user's application data directory:

- Windows: `%APPDATA%\exo\container-config.json`
- macOS: `~/Library/Application Support/exo/container-config.json`
- Linux: `~/.config/exo/container-config.json`

## Architecture

The Electron UI follows a simple architecture:

- `main.js`: Main process code
- `preload.js`: Preload script for secure renderer process communication
- `index.html`: UI layout and renderer process code
- `scripts/`: Helper scripts for dependency management and container integration

## Dependency Management

The app includes a robust dependency management system that:

1. Checks for required system dependencies
2. Prompts the user to install missing dependencies
3. Handles installation automatically when possible
4. Provides clear instructions when manual installation is required

## Building Installers

The app uses electron-builder to create installers for different platforms:

- Windows: NSIS installer (.exe)
- macOS: DMG installer (.dmg)
- Linux: AppImage, DEB, and RPM packages

The installers handle all dependency requirements and create appropriate shortcuts and file associations.

## License

MIT
