const { app, BrowserWindow, ipcMain, dialog, Menu } = require('electron');
const path = require('path');
const isDev = require('electron-is-dev');
const WebSocket = require('ws');
const { initialize, enable } = require('@electron/remote/main');
const containerIntegration = require('./scripts/container-integration');
const fs = require('fs');
const os = require('os');

// Initialize remote module
initialize();

// Keep a global reference of the window object to prevent garbage collection
let mainWindow;

// WebSocket client for communication with the Python backend
let wsClient;

// Container configuration
let containerConfig = containerIntegration.loadConfig();

// Connection status
let isConnected = false;
let reconnectAttempts = 0;
const MAX_RECONNECT_ATTEMPTS = 5;
const RECONNECT_INTERVAL = 2000; // 2 seconds

function createWindow() {
  // Create the browser window
  mainWindow = new BrowserWindow({
    width: 900,
    height: 700,
    minWidth: 600,
    minHeight: 400,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    },
    // Set window properties
    frame: true,
    titleBarStyle: 'hidden',
    backgroundColor: '#1e1e1e',
    icon: path.join(__dirname, 'assets/icons/png/64x64.png'),
    show: false // Don't show until ready-to-show
  });

  // Enable remote module for this window
  enable(mainWindow.webContents);

  // Load the app
  mainWindow.loadFile(path.join(__dirname, 'index.html'));

  // Show window when ready
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();

    // Check for Docker and container connection
    checkContainerConnection();
  });

  // Open DevTools in development mode
  if (isDev) {
    mainWindow.webContents.openDevTools({ mode: 'detach' });
  }

  // Handle window close
  mainWindow.on('closed', () => {
    disconnectFromContainer();
    mainWindow = null;
  });

  // Create application menu
  createAppMenu();
}

// Connect to the container's WebSocket server
function connectToContainerWebSocket(url) {
  // Disconnect existing connection if any
  disconnectFromContainer();

  console.log(`Connecting to WebSocket at ${url}...`);

  try {
    wsClient = new WebSocket(url);

    wsClient.on('open', () => {
      console.log('Connected to container WebSocket');
      isConnected = true;
      reconnectAttempts = 0;

      // Update UI
      if (mainWindow) {
        mainWindow.webContents.send('connection-status', { connected: true });
      }
    });

    wsClient.on('message', (message) => {
      try {
        const data = JSON.parse(message.toString());
        console.log('Received from backend:', data);

        // Forward the message to the renderer process
        if (mainWindow) {
          mainWindow.webContents.send('from-backend', data);
        }
      } catch (error) {
        console.error('Error parsing message:', error);
      }
    });

    wsClient.on('close', () => {
      console.log('WebSocket connection closed');
      isConnected = false;

      // Update UI
      if (mainWindow) {
        mainWindow.webContents.send('connection-status', { connected: false });
      }

      // Try to reconnect
      if (reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
        reconnectAttempts++;
        console.log(`Reconnecting (attempt ${reconnectAttempts}/${MAX_RECONNECT_ATTEMPTS})...`);
        setTimeout(() => connectToContainerWebSocket(url), RECONNECT_INTERVAL);
      } else {
        console.log('Max reconnect attempts reached');
        showConnectionError();
      }
    });

    wsClient.on('error', (error) => {
      console.error('WebSocket error:', error.message);
    });

    return true;
  } catch (error) {
    console.error('Error connecting to WebSocket:', error.message);
    return false;
  }
}

// Disconnect from the container
function disconnectFromContainer() {
  if (wsClient) {
    if (wsClient.readyState === WebSocket.OPEN) {
      wsClient.close();
    }
    wsClient = null;
  }
  isConnected = false;
}

// Check container connection
async function checkContainerConnection() {
  // Check if Docker is installed
  const dockerInstalled = containerIntegration.checkDocker();
  if (!dockerInstalled) {
    showDockerNotInstalledError();
    return;
  }

  // If auto-connect is enabled and we have a last container, try to connect to it
  if (containerConfig.autoConnect && containerConfig.lastContainer) {
    try {
      const containers = containerIntegration.listContainers();
      const containerExists = containers.some(container => container.id === containerConfig.lastContainer);

      if (containerExists) {
        const connectionInfo = await containerIntegration.connectToContainer(containerConfig.lastContainer, containerConfig);
        connectToContainerWebSocket(connectionInfo.websocketUrl);
        return;
      }
    } catch (error) {
      console.error('Error auto-connecting to container:', error.message);
    }
  }

  // Show container selection dialog
  showContainerSelectionDialog();
}

// Show container selection dialog
async function showContainerSelectionDialog() {
  try {
    const containerId = await containerIntegration.showContainerSelectionDialog(mainWindow);
    if (containerId) {
      const connectionInfo = await containerIntegration.connectToContainer(containerId, containerConfig);
      connectToContainerWebSocket(connectionInfo.websocketUrl);
    }
  } catch (error) {
    console.error('Error connecting to container:', error.message);
    showConnectionError(error.message);
  }
}

// Show Docker not installed error
function showDockerNotInstalledError() {
  dialog.showErrorBox(
    'Docker Not Installed',
    'Docker is required to run the exo backend in a container. Please install Docker and restart the application.'
  );
}

// Show connection error
function showConnectionError(message = '') {
  const errorMessage = message || 'Failed to connect to the container. Please check that the container is running and try again.';

  dialog.showErrorBox(
    'Connection Error',
    errorMessage
  );
}

// Create application menu
function createAppMenu() {
  const isMac = process.platform === 'darwin';

  const template = [
    // App menu (macOS only)
    ...(isMac ? [{
      label: app.name,
      submenu: [
        { role: 'about' },
        { type: 'separator' },
        { role: 'services' },
        { type: 'separator' },
        { role: 'hide' },
        { role: 'hideOthers' },
        { role: 'unhide' },
        { type: 'separator' },
        { role: 'quit' }
      ]
    }] : []),

    // File menu
    {
      label: 'File',
      submenu: [
        {
          label: 'Connect to Container',
          click: () => showContainerSelectionDialog()
        },
        { type: 'separator' },
        isMac ? { role: 'close' } : { role: 'quit' }
      ]
    },

    // Edit menu
    {
      label: 'Edit',
      submenu: [
        { role: 'undo' },
        { role: 'redo' },
        { type: 'separator' },
        { role: 'cut' },
        { role: 'copy' },
        { role: 'paste' },
        ...(isMac ? [
          { role: 'pasteAndMatchStyle' },
          { role: 'delete' },
          { role: 'selectAll' },
          { type: 'separator' },
          {
            label: 'Speech',
            submenu: [
              { role: 'startSpeaking' },
              { role: 'stopSpeaking' }
            ]
          }
        ] : [
          { role: 'delete' },
          { type: 'separator' },
          { role: 'selectAll' }
        ])
      ]
    },

    // View menu
    {
      label: 'View',
      submenu: [
        { role: 'reload' },
        { role: 'forceReload' },
        { role: 'toggleDevTools' },
        { type: 'separator' },
        { role: 'resetZoom' },
        { role: 'zoomIn' },
        { role: 'zoomOut' },
        { type: 'separator' },
        { role: 'togglefullscreen' }
      ]
    },

    // Window menu
    {
      label: 'Window',
      submenu: [
        { role: 'minimize' },
        { role: 'zoom' },
        ...(isMac ? [
          { type: 'separator' },
          { role: 'front' },
          { type: 'separator' },
          { role: 'window' }
        ] : [
          { role: 'close' }
        ])
      ]
    },

    // Help menu
    {
      role: 'help',
      submenu: [
        {
          label: 'Learn More',
          click: async () => {
            const { shell } = require('electron');
            await shell.openExternal('https://github.com/augmentcode/exo');
          }
        },
        {
          label: 'About exo',
          click: () => showAboutDialog()
        }
      ]
    }
  ];

  const menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);
}

// Show about dialog
function showAboutDialog() {
  dialog.showMessageBox(mainWindow, {
    title: 'About exo',
    message: 'exo Multi-Agent Framework',
    detail: `Version: ${app.getVersion()}\n\nA powerful AI assistant that helps you with your daily tasks.\n\nCopyright © 2025 Augment Code`,
    buttons: ['OK'],
    icon: path.join(__dirname, 'assets/icons/png/64x64.png')
  });
}

// Initialize the app
app.whenReady().then(() => {
  createWindow();

  // On macOS, recreate the window when the dock icon is clicked
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

// Quit the app when all windows are closed (except on macOS)
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// Handle messages from the renderer process
ipcMain.on('to-backend', (event, data) => {
  console.log('Sending to backend:', data);

  // Forward the message to the Python backend
  if (wsClient && wsClient.readyState === WebSocket.OPEN) {
    wsClient.send(JSON.stringify(data));
  } else {
    console.warn('Cannot send message: WebSocket not connected');

    // Show connection error if not already reconnecting
    if (reconnectAttempts === 0) {
      showConnectionError();
    }
  }
});

// Handle container connection request
ipcMain.on('connect-to-container', () => {
  showContainerSelectionDialog();
});

// Handle container settings request
ipcMain.on('container-settings', (event, settings) => {
  // Update container settings
  containerConfig = { ...containerConfig, ...settings };
  containerIntegration.saveConfig(containerConfig);
});

// Handle app quit
app.on('before-quit', () => {
  // Disconnect from the container
  disconnectFromContainer();
});
