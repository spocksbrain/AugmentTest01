#!/bin/bash

# After-install script for exo on Linux
# This script runs after the application is installed

# Detect the Linux distribution
if [ -f /etc/os-release ]; then
    . /etc/os-release
    DISTRO=$ID
elif [ -f /etc/lsb-release ]; then
    . /etc/lsb-release
    DISTRO=$DISTRIB_ID
else
    DISTRO=$(uname -s)
fi

# Function to install dependencies based on the distribution
install_dependencies() {
    echo "Installing dependencies for exo..."
    
    case $DISTRO in
        ubuntu|debian|linuxmint)
            # Check if we have sudo access
            if command -v sudo >/dev/null 2>&1; then
                echo "Installing dependencies using apt..."
                sudo apt-get update
                sudo apt-get install -y libasound2 libgtk-3-0 libnotify4 libnss3 libxss1 libxtst6 xdg-utils libatspi2.0-0 libdrm2 libgbm1 libxcb-dri3-0
            else
                echo "WARNING: sudo not available. Please install the following packages manually:"
                echo "libasound2 libgtk-3-0 libnotify4 libnss3 libxss1 libxtst6 xdg-utils libatspi2.0-0 libdrm2 libgbm1 libxcb-dri3-0"
            fi
            ;;
            
        fedora|rhel|centos)
            # Check if we have sudo access
            if command -v sudo >/dev/null 2>&1; then
                echo "Installing dependencies using dnf..."
                sudo dnf install -y alsa-lib gtk3 libnotify nss libXScrnSaver libXtst xdg-utils at-spi2-atk libdrm mesa-libgbm libxcb
            else
                echo "WARNING: sudo not available. Please install the following packages manually:"
                echo "alsa-lib gtk3 libnotify nss libXScrnSaver libXtst xdg-utils at-spi2-atk libdrm mesa-libgbm libxcb"
            fi
            ;;
            
        arch|manjaro)
            # Check if we have sudo access
            if command -v sudo >/dev/null 2>&1; then
                echo "Installing dependencies using pacman..."
                sudo pacman -Sy --noconfirm alsa-lib gtk3 libnotify nss libxss libxtst xdg-utils at-spi2-atk libdrm mesa libxcb
            else
                echo "WARNING: sudo not available. Please install the following packages manually:"
                echo "alsa-lib gtk3 libnotify nss libxss libxtst xdg-utils at-spi2-atk libdrm mesa libxcb"
            fi
            ;;
            
        *)
            echo "Unsupported distribution: $DISTRO"
            echo "Please install the following dependencies manually:"
            echo "- ALSA sound library (libasound2)"
            echo "- GTK3 library"
            echo "- libnotify"
            echo "- NSS (Network Security Services)"
            echo "- libXScrnSaver"
            echo "- libXtst"
            echo "- xdg-utils"
            echo "- AT-SPI2 ATK"
            echo "- libdrm"
            echo "- Mesa GBM"
            echo "- libxcb"
            ;;
    esac
}

# Install desktop integration
install_desktop_integration() {
    echo "Setting up desktop integration..."
    
    # Create desktop file
    DESKTOP_FILE="/usr/share/applications/exo.desktop"
    
    if [ -w "$(dirname "$DESKTOP_FILE")" ]; then
        cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Name=exo
Comment=Your personal AI assistant
Exec=/opt/exo/exo
Icon=/opt/exo/resources/icon.png
Terminal=false
Type=Application
Categories=Utility;
StartupNotify=true
EOF
        chmod +x "$DESKTOP_FILE"
        echo "Desktop integration completed."
    else
        echo "WARNING: Cannot create desktop file. Please run the following command manually with sudo:"
        echo "cat > /usr/share/applications/exo.desktop << EOF"
        echo "[Desktop Entry]"
        echo "Name=exo"
        echo "Comment=Your personal AI assistant"
        echo "Exec=/opt/exo/exo"
        echo "Icon=/opt/exo/resources/icon.png"
        echo "Terminal=false"
        echo "Type=Application"
        echo "Categories=Utility;"
        echo "StartupNotify=true"
        echo "EOF"
    fi
}

# Main installation process
echo "Running post-installation setup for exo..."

# Install dependencies
install_dependencies

# Set up desktop integration
install_desktop_integration

echo "Post-installation setup completed."
exit 0
