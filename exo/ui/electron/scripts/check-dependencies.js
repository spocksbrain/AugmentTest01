const { execSync } = require('child_process');
const os = require('os');
const fs = require('fs');
const path = require('path');
const readline = require('readline');

// Define required dependencies for each platform
const dependencies = {
  linux: {
    debian: [
      { name: 'libasound2', package: 'libasound2' },
      { name: 'libgtk-3-0', package: 'libgtk-3-0' },
      { name: 'libnotify4', package: 'libnotify4' },
      { name: 'libnss3', package: 'libnss3' },
      { name: 'libxss1', package: 'libxss1' },
      { name: 'libxtst6', package: 'libxtst6' },
      { name: 'xdg-utils', package: 'xdg-utils' },
      { name: 'libatspi2.0-0', package: 'libatspi2.0-0' },
      { name: 'libdrm2', package: 'libdrm2' },
      { name: 'libgbm1', package: 'libgbm1' },
      { name: 'libxcb-dri3-0', package: 'libxcb-dri3-0' }
    ],
    fedora: [
      { name: 'libasound.so.2', package: 'alsa-lib' },
      { name: 'libgtk-3.so.0', package: 'gtk3' },
      { name: 'libnotify.so.4', package: 'libnotify' },
      { name: 'libnss3.so', package: 'nss' },
      { name: 'libXss.so.1', package: 'libXScrnSaver' },
      { name: 'libXtst.so.6', package: 'libXtst' },
      { name: 'xdg-utils', package: 'xdg-utils' },
      { name: 'libatspi.so.0', package: 'at-spi2-atk' },
      { name: 'libdrm.so.2', package: 'libdrm' },
      { name: 'libgbm.so.1', package: 'mesa-libgbm' },
      { name: 'libxcb-dri3.so.0', package: 'libxcb' }
    ],
    arch: [
      { name: 'libasound.so.2', package: 'alsa-lib' },
      { name: 'libgtk-3.so.0', package: 'gtk3' },
      { name: 'libnotify.so.4', package: 'libnotify' },
      { name: 'libnss3.so', package: 'nss' },
      { name: 'libXss.so.1', package: 'libxss' },
      { name: 'libXtst.so.6', package: 'libxtst' },
      { name: 'xdg-utils', package: 'xdg-utils' },
      { name: 'libatspi.so.0', package: 'at-spi2-atk' },
      { name: 'libdrm.so.2', package: 'libdrm' },
      { name: 'libgbm.so.1', package: 'mesa' },
      { name: 'libxcb-dri3.so.0', package: 'libxcb' }
    ]
  },
  win: [
    { name: 'Visual C++ Redistributable', check: checkVCRedist }
  ],
  mac: [
    // macOS typically has all required dependencies
  ]
};

// Create readline interface for user input
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

// Main function
async function main() {
  console.log('Checking system dependencies for exo...');
  
  const platform = os.platform();
  
  if (platform === 'linux') {
    await checkLinuxDependencies();
  } else if (platform === 'win32') {
    await checkWindowsDependencies();
  } else if (platform === 'darwin') {
    await checkMacDependencies();
  } else {
    console.log(`Unsupported platform: ${platform}`);
    console.log('Please ensure you have the necessary dependencies installed manually.');
  }
  
  rl.close();
}

// Check Linux dependencies
async function checkLinuxDependencies() {
  try {
    // Detect Linux distribution
    const distro = await detectLinuxDistro();
    console.log(`Detected Linux distribution: ${distro}`);
    
    let distroType = 'debian';
    if (distro === 'fedora' || distro === 'rhel' || distro === 'centos') {
      distroType = 'fedora';
    } else if (distro === 'arch' || distro === 'manjaro') {
      distroType = 'arch';
    }
    
    // Get list of dependencies for this distribution
    const deps = dependencies.linux[distroType] || dependencies.linux.debian;
    
    // Check each dependency
    const missing = [];
    for (const dep of deps) {
      const isInstalled = await checkLinuxDependency(dep.name, distroType);
      if (!isInstalled) {
        missing.push(dep);
      }
    }
    
    // Handle missing dependencies
    if (missing.length > 0) {
      console.log('The following dependencies are missing:');
      missing.forEach(dep => console.log(`- ${dep.name} (${dep.package})`));
      
      const answer = await askQuestion('Would you like to install these dependencies now? (y/n) ');
      if (answer.toLowerCase() === 'y') {
        await installLinuxDependencies(missing, distroType);
      } else {
        console.log('Please install the missing dependencies manually before running exo.');
      }
    } else {
      console.log('All required dependencies are installed.');
    }
  } catch (error) {
    console.error('Error checking Linux dependencies:', error.message);
    console.log('Please ensure you have the necessary dependencies installed manually.');
  }
}

// Check Windows dependencies
async function checkWindowsDependencies() {
  try {
    // Check each dependency
    const missing = [];
    for (const dep of dependencies.win) {
      const isInstalled = await dep.check();
      if (!isInstalled) {
        missing.push(dep);
      }
    }
    
    // Handle missing dependencies
    if (missing.length > 0) {
      console.log('The following dependencies are missing:');
      missing.forEach(dep => console.log(`- ${dep.name}`));
      
      const answer = await askQuestion('Would you like to install these dependencies now? (y/n) ');
      if (answer.toLowerCase() === 'y') {
        await installWindowsDependencies(missing);
      } else {
        console.log('Please install the missing dependencies manually before running exo.');
      }
    } else {
      console.log('All required dependencies are installed.');
    }
  } catch (error) {
    console.error('Error checking Windows dependencies:', error.message);
    console.log('Please ensure you have the necessary dependencies installed manually.');
  }
}

// Check macOS dependencies
async function checkMacDependencies() {
  // macOS typically has all required dependencies
  console.log('All required dependencies should be available on macOS.');
}

// Detect Linux distribution
async function detectLinuxDistro() {
  try {
    if (fs.existsSync('/etc/os-release')) {
      const osRelease = fs.readFileSync('/etc/os-release', 'utf8');
      const idMatch = osRelease.match(/^ID=(.*)$/m);
      if (idMatch && idMatch[1]) {
        return idMatch[1].replace(/"/g, '');
      }
    }
    
    if (fs.existsSync('/etc/lsb-release')) {
      const lsbRelease = fs.readFileSync('/etc/lsb-release', 'utf8');
      const idMatch = lsbRelease.match(/^DISTRIB_ID=(.*)$/m);
      if (idMatch && idMatch[1]) {
        return idMatch[1].replace(/"/g, '').toLowerCase();
      }
    }
    
    // Fallback to debian
    return 'debian';
  } catch (error) {
    console.error('Error detecting Linux distribution:', error.message);
    return 'debian';
  }
}

// Check if a Linux dependency is installed
async function checkLinuxDependency(name, distroType) {
  try {
    if (distroType === 'debian') {
      // For Debian-based distributions
      execSync(`dpkg -s ${name} 2>/dev/null`);
      return true;
    } else if (distroType === 'fedora') {
      // For Fedora-based distributions
      execSync(`rpm -q --whatprovides ${name} 2>/dev/null`);
      return true;
    } else if (distroType === 'arch') {
      // For Arch-based distributions
      execSync(`pacman -Q ${name} 2>/dev/null`);
      return true;
    }
    return false;
  } catch (error) {
    return false;
  }
}

// Install Linux dependencies
async function installLinuxDependencies(dependencies, distroType) {
  try {
    const packages = dependencies.map(dep => dep.package).join(' ');
    
    if (distroType === 'debian') {
      // For Debian-based distributions
      console.log(`Installing dependencies using apt: ${packages}`);
      execSync(`sudo apt-get update && sudo apt-get install -y ${packages}`, { stdio: 'inherit' });
    } else if (distroType === 'fedora') {
      // For Fedora-based distributions
      console.log(`Installing dependencies using dnf: ${packages}`);
      execSync(`sudo dnf install -y ${packages}`, { stdio: 'inherit' });
    } else if (distroType === 'arch') {
      // For Arch-based distributions
      console.log(`Installing dependencies using pacman: ${packages}`);
      execSync(`sudo pacman -Sy --noconfirm ${packages}`, { stdio: 'inherit' });
    } else {
      console.log(`Unsupported distribution type: ${distroType}`);
      console.log('Please install the dependencies manually.');
      return false;
    }
    
    console.log('Dependencies installed successfully.');
    return true;
  } catch (error) {
    console.error('Error installing dependencies:', error.message);
    console.log('Please install the dependencies manually.');
    return false;
  }
}

// Check if Visual C++ Redistributable is installed
function checkVCRedist() {
  try {
    const stdout = execSync('reg query "HKLM\\SOFTWARE\\Microsoft\\VisualStudio\\14.0\\VC\\Runtimes\\x64" /v Installed', { encoding: 'utf8' });
    return stdout.includes('0x1');
  } catch (error) {
    return false;
  }
}

// Install Windows dependencies
async function installWindowsDependencies(dependencies) {
  try {
    for (const dep of dependencies) {
      if (dep.name === 'Visual C++ Redistributable') {
        console.log('Downloading Visual C++ Redistributable...');
        const vcRedistPath = path.join(os.tmpdir(), 'vc_redist.x64.exe');
        execSync(`curl -L -o "${vcRedistPath}" https://aka.ms/vs/16/release/vc_redist.x64.exe`, { stdio: 'inherit' });
        
        console.log('Installing Visual C++ Redistributable...');
        execSync(`"${vcRedistPath}" /quiet /norestart`, { stdio: 'inherit' });
        
        console.log('Cleaning up...');
        fs.unlinkSync(vcRedistPath);
      }
    }
    
    console.log('Dependencies installed successfully.');
    return true;
  } catch (error) {
    console.error('Error installing dependencies:', error.message);
    console.log('Please install the dependencies manually.');
    return false;
  }
}

// Helper function to ask a question
function askQuestion(question) {
  return new Promise(resolve => {
    rl.question(question, answer => {
      resolve(answer);
    });
  });
}

// Run the main function
main().catch(error => {
  console.error('Error:', error.message);
  rl.close();
});
