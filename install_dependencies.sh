#!/bin/bash
# Script to install all required dependencies for the exo Multi-Agent Framework

# Default values
INSTALL_VOICE=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --voice)
            INSTALL_VOICE=true
            shift
            ;;
        --help)
            echo "Usage: $0 [options]"
            echo "Options:"
            echo "  --voice    Install voice assistant dependencies"
            echo "  --help     Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Function to detect the Linux distribution
detect_distro() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        DISTRO=$ID
    elif [ -f /etc/lsb-release ]; then
        . /etc/lsb-release
        DISTRO=$DISTRIB_ID
    elif [ -f /etc/debian_version ]; then
        DISTRO="debian"
    elif [ -f /etc/fedora-release ]; then
        DISTRO="fedora"
    elif [ -f /etc/centos-release ]; then
        DISTRO="centos"
    elif [ -f /etc/arch-release ]; then
        DISTRO="arch"
    else
        DISTRO="unknown"
    fi
    echo $DISTRO
}

# Function to install dependencies based on the distribution
install_dependencies() {
    DISTRO=$(detect_distro)
    echo "Detected Linux distribution: $DISTRO"

    case "$DISTRO" in
        "ubuntu"|"debian"|"linuxmint"|"pop"|"elementary")
            echo "Installing dependencies for Debian-based distribution..."
            sudo apt-get update
            sudo apt-get install -y libdbus-1-3 libgtk-3-0 libgbm1 libnss3 libxss1 libatk1.0-0 libatk-bridge2.0-0 libatspi2.0-0 libdrm2 libx11-xcb1 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libxtst6 libcups2 libasound2 libpulse0 libpangocairo-1.0-0 libpango-1.0-0 libcairo2 libfontconfig1 libglib2.0-0 libexpat1 libfreetype6 libpixman-1-0 libpng16-16 libxcb-shm0 libxcb-render0 libxrender1 libx11-6 libxext6 libxi6 libgcc-s1 libc6 libstdc++6 libgdk-pixbuf-2.0-0 libgdk-pixbuf-xlib-2.0-0 libgl1-mesa-glx libgl1 dbus-x11
            ;;
        "fedora"|"rhel"|"centos"|"rocky"|"alma")
            echo "Installing dependencies for Fedora/RHEL-based distribution..."
            sudo dnf install -y dbus-libs gtk3 mesa-libgbm nss libXScrnSaver atk at-spi2-atk at-spi2-core libdrm libX11-xcb libXcomposite libXdamage libXfixes libXrandr libXtst cups-libs alsa-lib pulseaudio-libs pango cairo fontconfig glib2 expat freetype pixman libpng libxcb libXrender libX11 libXext libXi libgcc glibc libstdc++ gdk-pixbuf2 mesa-libGL dbus-x11
            ;;
        "arch"|"manjaro"|"endeavouros")
            echo "Installing dependencies for Arch-based distribution..."
            sudo pacman -S --needed --noconfirm libdbus gtk3 mesa nss libxss atk at-spi2-atk at-spi2-core libdrm libx11 libxcomposite libxdamage libxfixes libxrandr libxtst libcups alsa-lib pulseaudio pango cairo fontconfig glib2 expat freetype2 pixman libpng libxcb libxrender libxext libxi gcc glibc libstdc++ gdk-pixbuf2 mesa-libgl dbus
            ;;
        *)
            echo "Unsupported distribution: $DISTRO"
            echo "Please install the required dependencies manually:"
            echo "- libdbus-1.so.3 (libdbus-1-3)"
            echo "- libgtk-3.so.0 (libgtk-3-0)"
            echo "- libgbm.so.1 (libgbm1)"
            echo "- libnss3.so (libnss3)"
            echo "- libxss.so.1 (libxss1)"
            echo "- libatk-1.0.so.0 (libatk1.0-0)"
            echo "- libatk-bridge-2.0.so.0 (libatk-bridge2.0-0)"
            echo "- libatspi.so.0 (libatspi2.0-0)"
            echo "- libdrm.so.2 (libdrm2)"
            echo "- libx11-xcb.so.1 (libx11-xcb1)"
            echo "- libxcomposite.so.1 (libxcomposite1)"
            echo "- libxdamage.so.1 (libxdamage1)"
            echo "- libxfixes.so.3 (libxfixes3)"
            echo "- libxrandr.so.2 (libxrandr2)"
            echo "- libxtst.so.6 (libxtst6)"
            echo "- libcups.so.2 (libcups2)"
            echo "- libasound.so.2 (libasound2)"
            echo "- libpulse.so.0 (libpulse0)"
            echo "- libpangocairo-1.0.so.0 (libpangocairo-1.0-0)"
            echo "- libpango-1.0.so.0 (libpango-1.0-0)"
            echo "- libcairo.so.2 (libcairo2)"
            echo "- libfontconfig.so.1 (libfontconfig1)"
            echo "- libglib-2.0.so.0 (libglib2.0-0)"
            echo "- libexpat.so.1 (libexpat1)"
            echo "- libfreetype.so.6 (libfreetype6)"
            echo "- libpixman-1.so.0 (libpixman-1-0)"
            echo "- libpng16.so.16 (libpng16-16)"
            echo "- libxcb-shm.so.0 (libxcb-shm0)"
            echo "- libxcb-render.so.0 (libxcb-render0)"
            echo "- libxrender.so.1 (libxrender1)"
            echo "- libx11.so.6 (libx11-6)"
            echo "- libxext.so.6 (libxext6)"
            echo "- libxi.so.6 (libxi6)"
            echo "- libgcc_s.so.1 (libgcc-s1)"
            echo "- libc.so.6 (libc6)"
            echo "- libstdc++.so.6 (libstdc++6)"
            echo "- libgdk_pixbuf-2.0.so.0 (libgdk-pixbuf-2.0-0)"
            echo "- libgdk_pixbuf_xlib-2.0.so.0 (libgdk-pixbuf-xlib-2.0-0)"
            echo "- libGL.so.1 (libgl1-mesa-glx or libgl1)"
            echo "- dbus-daemon (dbus-x11)"
            ;;
    esac
}

# Install Node.js and npm if not already installed
install_nodejs() {
    if ! command -v node &> /dev/null; then
        echo "Node.js is not installed. Installing..."

        DISTRO=$(detect_distro)
        case "$DISTRO" in
            "ubuntu"|"debian"|"linuxmint"|"pop"|"elementary")
                curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
                sudo apt-get install -y nodejs
                ;;
            "fedora"|"rhel"|"centos"|"rocky"|"alma")
                curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
                sudo dnf install -y nodejs
                ;;
            "arch"|"manjaro"|"endeavouros")
                sudo pacman -S --needed --noconfirm nodejs npm
                ;;
            *)
                echo "Please install Node.js manually from https://nodejs.org/"
                ;;
        esac
    else
        echo "Node.js is already installed."
    fi
}

# Install Electron globally if not already installed
install_electron() {
    if ! command -v electron &> /dev/null; then
        echo "Electron is not installed. Installing..."
        sudo npm install -g electron
    else
        echo "Electron is already installed."
    fi
}

# Install Python dependencies
install_python_dependencies() {
    echo "Installing Python dependencies..."

    # Check if pip is installed
    if ! command -v pip &> /dev/null; then
        echo "pip is not installed. Installing..."
        if [ "$DISTRO" = "debian" ] || [ "$DISTRO" = "ubuntu" ]; then
            sudo apt-get install -y python3-pip
        elif [ "$DISTRO" = "fedora" ] || [ "$DISTRO" = "centos" ] || [ "$DISTRO" = "rhel" ]; then
            sudo dnf install -y python3-pip
        elif [ "$DISTRO" = "arch" ]; then
            sudo pacman -S --noconfirm python-pip
        else
            echo "Could not install pip. Please install it manually."
            return 1
        fi
    fi

    # Install required Python packages
    echo "Installing required Python packages..."
    pip install flask flask-socketio websockets
}

# Install voice assistant dependencies
install_voice_dependencies() {
    echo "Installing voice assistant dependencies..."

    # Install system dependencies for PyAudio
    if [ "$DISTRO" = "debian" ] || [ "$DISTRO" = "ubuntu" ]; then
        sudo apt-get install -y portaudio19-dev python3-pyaudio
    elif [ "$DISTRO" = "fedora" ] || [ "$DISTRO" = "centos" ] || [ "$DISTRO" = "rhel" ]; then
        sudo dnf install -y portaudio-devel
    elif [ "$DISTRO" = "arch" ]; then
        sudo pacman -S --noconfirm portaudio
    else
        echo "Could not install system dependencies for PyAudio. Please install them manually."
    fi

    # Install Python packages for voice assistant
    echo "Installing Python packages for voice assistant..."
    pip install SpeechRecognition pyttsx3 pyaudio gTTS pygame

    echo "Voice assistant dependencies installed."
}

# Check if running in a container
is_running_in_container() {
    # Check for container-specific files
    if [ -f /.dockerenv ] || [ -f /run/.containerenv ]; then
        return 0
    fi

    # Check cgroup
    if grep -q 'docker\|lxc\|kubepods' /proc/1/cgroup 2>/dev/null; then
        return 0
    fi

    return 1
}

# Main function
main() {
    echo "Installing dependencies for exo Multi-Agent Framework..."

    # Check if running in a container
    if is_running_in_container; then
        echo ""
        echo "Detected container environment."
        echo "Note: The UI may not work correctly in a container environment."
        echo "The system will automatically run in backend-only mode unless --force-ui is specified."
        echo ""
    fi

    # Install system dependencies
    install_dependencies

    # Install Node.js and npm
    install_nodejs

    # Install Electron (for backward compatibility)
    install_electron

    # Install Python dependencies
    install_python_dependencies

    # Install voice assistant dependencies if requested
    if [ "$INSTALL_VOICE" = "true" ]; then
        install_voice_dependencies
    fi

    echo "All dependencies installed successfully!"
    echo "You can now run the exo Multi-Agent Framework with: python run_exo.py"

    if is_running_in_container; then
        echo ""
        echo "Since you are in a container environment, use the following command to run in backend-only mode:"
        echo "python run_exo.py --no-ui"
        echo ""
        echo "If you want to force the UI (not recommended in containers), use:"
        echo "python run_exo.py --force-ui"
    fi
}

# Run the main function
main
