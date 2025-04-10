const { contextBridge, ipcRenderer } = require('electron');
const { BrowserWindow } = require('@electron/remote');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
  // Send a message to the backend
  sendMessage: (data) => {
    ipcRenderer.send('to-backend', data);
  },

  // Receive a message from the backend
  onMessage: (callback) => {
    ipcRenderer.on('from-backend', (event, data) => callback(data));
  },

  // Connection status
  onConnectionStatus: (callback) => {
    ipcRenderer.on('connection-status', (event, status) => callback(status));
  },

  // Container connection
  connectToContainer: () => {
    ipcRenderer.send('connect-to-container');
  },

  // Update container settings
  updateContainerSettings: (settings) => {
    ipcRenderer.send('container-settings', settings);
  },

  // Window control functions
  minimizeWindow: () => {
    const currentWindow = BrowserWindow.getFocusedWindow();
    if (currentWindow) currentWindow.minimize();
  },

  maximizeWindow: () => {
    const currentWindow = BrowserWindow.getFocusedWindow();
    if (currentWindow) {
      if (currentWindow.isMaximized()) {
        currentWindow.unmaximize();
      } else {
        currentWindow.maximize();
      }
    }
  },

  closeWindow: () => {
    const currentWindow = BrowserWindow.getFocusedWindow();
    if (currentWindow) currentWindow.close();
  },

  // Get app version
  getVersion: () => require('@electron/remote').app.getVersion()
});
