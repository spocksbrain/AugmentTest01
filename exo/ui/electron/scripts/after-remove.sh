#!/bin/bash

# After-remove script for exo on Linux
# This script runs after the application is uninstalled

# Clean up desktop integration
cleanup_desktop_integration() {
    echo "Cleaning up desktop integration..."
    
    # Remove desktop file
    DESKTOP_FILE="/usr/share/applications/exo.desktop"
    
    if [ -f "$DESKTOP_FILE" ] && [ -w "$(dirname "$DESKTOP_FILE")" ]; then
        rm -f "$DESKTOP_FILE"
        echo "Desktop file removed."
    else
        echo "WARNING: Cannot remove desktop file. Please run the following command manually with sudo:"
        echo "rm -f /usr/share/applications/exo.desktop"
    fi
}

# Main cleanup process
echo "Running post-uninstallation cleanup for exo..."

# Clean up desktop integration
cleanup_desktop_integration

echo "Post-uninstallation cleanup completed."
exit 0
