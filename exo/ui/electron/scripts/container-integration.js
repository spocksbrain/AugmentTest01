const { app, dialog } = require('electron');
const fs = require('fs');
const path = require('path');
const os = require('os');
const { execSync, spawn } = require('child_process');

// Configuration
const CONFIG_FILE = path.join(app.getPath('userData'), 'container-config.json');
const DEFAULT_CONFIG = {
  containerHost: 'localhost',
  containerPort: 8080,
  websocketPort: 8765,
  autoConnect: true,
  lastContainer: null
};

// Load configuration
function loadConfig() {
  try {
    if (fs.existsSync(CONFIG_FILE)) {
      const config = JSON.parse(fs.readFileSync(CONFIG_FILE, 'utf8'));
      return { ...DEFAULT_CONFIG, ...config };
    }
  } catch (error) {
    console.error('Error loading configuration:', error);
  }
  return DEFAULT_CONFIG;
}

// Save configuration
function saveConfig(config) {
  try {
    fs.writeFileSync(CONFIG_FILE, JSON.stringify(config, null, 2));
  } catch (error) {
    console.error('Error saving configuration:', error);
  }
}

// Check if Docker is installed
function checkDocker() {
  try {
    execSync('docker --version', { stdio: 'ignore' });
    return true;
  } catch (error) {
    return false;
  }
}

// List running containers
function listContainers() {
  try {
    const output = execSync('docker ps --format "{{.ID}}|{{.Names}}|{{.Image}}|{{.Status}}"', { encoding: 'utf8' });
    return output.trim().split('\n').map(line => {
      const [id, name, image, status] = line.split('|');
      return { id, name, image, status };
    });
  } catch (error) {
    console.error('Error listing containers:', error);
    return [];
  }
}

// Get container IP address
function getContainerIP(containerId) {
  try {
    const output = execSync(`docker inspect --format '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' ${containerId}`, { encoding: 'utf8' });
    return output.trim();
  } catch (error) {
    console.error('Error getting container IP:', error);
    return null;
  }
}

// Check if a port is open on a host
function checkPort(host, port) {
  return new Promise(resolve => {
    const net = require('net');
    const socket = new net.Socket();
    
    const timeout = setTimeout(() => {
      socket.destroy();
      resolve(false);
    }, 1000);
    
    socket.connect(port, host, () => {
      clearTimeout(timeout);
      socket.destroy();
      resolve(true);
    });
    
    socket.on('error', () => {
      clearTimeout(timeout);
      socket.destroy();
      resolve(false);
    });
  });
}

// Connect to a container
async function connectToContainer(containerId, config) {
  // Get container IP
  const containerIP = getContainerIP(containerId);
  if (!containerIP) {
    throw new Error('Failed to get container IP address');
  }
  
  // Check if the web server port is open
  const webServerOpen = await checkPort(containerIP, config.containerPort);
  if (!webServerOpen) {
    throw new Error(`Web server port ${config.containerPort} is not open on the container`);
  }
  
  // Check if the WebSocket port is open
  const websocketOpen = await checkPort(containerIP, config.websocketPort);
  if (!websocketOpen) {
    throw new Error(`WebSocket port ${config.websocketPort} is not open on the container`);
  }
  
  // Update configuration
  config.containerHost = containerIP;
  config.lastContainer = containerId;
  saveConfig(config);
  
  return {
    webUrl: `http://${containerIP}:${config.containerPort}`,
    websocketUrl: `ws://${containerIP}:${config.websocketPort}`
  };
}

// Start a container
function startContainer(imageName) {
  try {
    // Check if the image exists
    const images = execSync(`docker images ${imageName} --format "{{.Repository}}:{{.Tag}}"`, { encoding: 'utf8' });
    if (!images.trim()) {
      throw new Error(`Image ${imageName} not found`);
    }
    
    // Start the container
    const containerId = execSync(`docker run -d -p 8080:8080 -p 8765:8765 ${imageName}`, { encoding: 'utf8' }).trim();
    return containerId;
  } catch (error) {
    console.error('Error starting container:', error);
    throw error;
  }
}

// Stop a container
function stopContainer(containerId) {
  try {
    execSync(`docker stop ${containerId}`, { stdio: 'ignore' });
    return true;
  } catch (error) {
    console.error('Error stopping container:', error);
    return false;
  }
}

// Show container selection dialog
async function showContainerSelectionDialog(browserWindow) {
  const containers = listContainers();
  
  if (containers.length === 0) {
    const result = await dialog.showMessageBox(browserWindow, {
      type: 'warning',
      title: 'No Containers Found',
      message: 'No running Docker containers were found.',
      detail: 'Would you like to start a new container with the exo image?',
      buttons: ['Start Container', 'Cancel'],
      defaultId: 0,
      cancelId: 1
    });
    
    if (result.response === 0) {
      try {
        const containerId = startContainer('exo:latest');
        return containerId;
      } catch (error) {
        await dialog.showErrorBox('Error', `Failed to start container: ${error.message}`);
        return null;
      }
    }
    
    return null;
  }
  
  const options = containers.map(container => ({
    label: `${container.name} (${container.image})`,
    value: container.id
  }));
  
  const result = await dialog.showMessageBox(browserWindow, {
    type: 'question',
    title: 'Select Container',
    message: 'Select a Docker container to connect to:',
    buttons: options.map(option => option.label).concat(['Cancel']),
    defaultId: 0,
    cancelId: options.length
  });
  
  if (result.response < options.length) {
    return options[result.response].value;
  }
  
  return null;
}

// Export functions
module.exports = {
  loadConfig,
  saveConfig,
  checkDocker,
  listContainers,
  getContainerIP,
  connectToContainer,
  startContainer,
  stopContainer,
  showContainerSelectionDialog
};
