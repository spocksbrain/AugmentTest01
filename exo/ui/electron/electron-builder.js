const builder = require('electron-builder');
const path = require('path');
const fs = require('fs');

// Define platform-specific dependencies
const linuxDependencies = [
  'libasound2',
  'libgtk-3-0',
  'libnotify4',
  'libnss3',
  'libxss1',
  'libxtst6',
  'xdg-utils',
  'libatspi2.0-0',
  'libdrm2',
  'libgbm1',
  'libxcb-dri3-0'
];

// Build configuration
const config = {
  appId: 'com.augmentcode.exo',
  productName: 'exo',
  copyright: 'Copyright © 2025 Augment Code',
  
  // Directories
  directories: {
    output: path.join(__dirname, 'dist'),
    app: __dirname
  },
  
  // Files to include
  files: [
    'main.js',
    'preload.js',
    'index.html',
    'node_modules/**/*',
    'assets/**/*',
    {
      from: path.join(__dirname, 'scripts'),
      to: 'scripts',
      filter: ['**/*']
    }
  ],
  
  // Extra resources
  extraResources: [
    {
      from: path.join(__dirname, 'resources'),
      to: 'resources',
      filter: ['**/*']
    }
  ],
  
  // Mac configuration
  mac: {
    category: 'public.app-category.productivity',
    target: ['dmg', 'zip'],
    icon: path.join(__dirname, 'assets/icons/mac/icon.icns'),
    darkModeSupport: true,
    hardenedRuntime: true,
    gatekeeperAssess: false,
    entitlements: path.join(__dirname, 'entitlements.plist'),
    entitlementsInherit: path.join(__dirname, 'entitlements.plist')
  },
  
  // Windows configuration
  win: {
    target: ['nsis'],
    icon: path.join(__dirname, 'assets/icons/win/icon.ico'),
    publisherName: 'Augment Code'
  },
  
  // Linux configuration
  linux: {
    target: ['AppImage', 'deb', 'rpm'],
    icon: path.join(__dirname, 'assets/icons/png'),
    category: 'Utility',
    desktop: {
      StartupNotify: 'true',
      StartupWMClass: 'exo'
    },
    // Specify dependencies
    depends: linuxDependencies
  },
  
  // NSIS configuration for Windows installer
  nsis: {
    oneClick: false,
    allowToChangeInstallationDirectory: true,
    createDesktopShortcut: true,
    createStartMenuShortcut: true,
    shortcutName: 'exo',
    include: path.join(__dirname, 'installer.nsh'),
    installerIcon: path.join(__dirname, 'assets/icons/win/installer.ico'),
    uninstallerIcon: path.join(__dirname, 'assets/icons/win/uninstaller.ico')
  },
  
  // DMG configuration for Mac
  dmg: {
    background: path.join(__dirname, 'assets/dmg-background.png'),
    icon: path.join(__dirname, 'assets/icons/mac/icon.icns'),
    iconSize: 128,
    contents: [
      {
        x: 130,
        y: 150,
        type: 'file'
      },
      {
        x: 410,
        y: 150,
        type: 'link',
        path: '/Applications'
      }
    ],
    window: {
      width: 540,
      height: 380
    }
  },
  
  // AppImage configuration for Linux
  appImage: {
    systemIntegration: 'ask',
    license: path.join(__dirname, 'LICENSE')
  },
  
  // DEB configuration for Linux
  deb: {
    afterInstall: path.join(__dirname, 'scripts/after-install.sh'),
    afterRemove: path.join(__dirname, 'scripts/after-remove.sh'),
    fpm: ['--deb-no-default-config-files']
  },
  
  // RPM configuration for Linux
  rpm: {
    afterInstall: path.join(__dirname, 'scripts/after-install.sh'),
    afterRemove: path.join(__dirname, 'scripts/after-remove.sh')
  },
  
  // Publish configuration (for auto-updates)
  publish: {
    provider: 'github',
    owner: 'augmentcode',
    repo: 'exo'
  }
};

// Build for current platform
async function build() {
  try {
    await builder.build({
      config: config
    });
    console.log('Build completed successfully!');
  } catch (error) {
    console.error('Build failed:', error);
    process.exit(1);
  }
}

build();
