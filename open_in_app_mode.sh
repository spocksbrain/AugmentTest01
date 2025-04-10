#!/bin/bash

# Script to open the exo UI in app mode
# Usage: ./open_in_app_mode.sh [host] [port]

HOST=${1:-localhost}
PORT=${2:-8080}
URL="http://${HOST}:${PORT}"

echo "Opening $URL in app mode..."

# Try different browsers based on what's available
if command -v google-chrome &> /dev/null; then
    google-chrome --app="$URL"
elif command -v chromium-browser &> /dev/null; then
    chromium-browser --app="$URL"
elif command -v chromium &> /dev/null; then
    chromium --app="$URL"
elif command -v microsoft-edge &> /dev/null; then
    microsoft-edge --app="$URL"
elif command -v brave-browser &> /dev/null; then
    brave-browser --app="$URL"
else
    echo "No compatible browser found for app mode."
    echo "Please install Google Chrome, Chromium, Microsoft Edge, or Brave."
    echo "Alternatively, you can manually open $URL in your browser."
    
    # Try to open in regular browser as fallback
    if command -v xdg-open &> /dev/null; then
        xdg-open "$URL"
    elif command -v open &> /dev/null; then
        open "$URL"
    elif command -v start &> /dev/null; then
        start "$URL"
    fi
fi
