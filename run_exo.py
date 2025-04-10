#!/usr/bin/env python3
"""
Simple script to run the exo Multi-Agent Framework
"""

import os
import sys
import subprocess
import argparse

def is_running_in_container():
    """Check if we're running inside a container."""
    # Check for container-specific files
    container_indicators = [
        "/.dockerenv",
        "/run/.containerenv",
    ]
    for indicator in container_indicators:
        if os.path.exists(indicator):
            return True

    # Check cgroup
    try:
        with open("/proc/1/cgroup", "r") as f:
            content = f.read()
            if "docker" in content or "lxc" in content or "kubepods" in content:
                return True
    except (IOError, FileNotFoundError):
        pass

    return False

def main():
    """Main entry point for the run script."""
    parser = argparse.ArgumentParser(description="Run the exo Multi-Agent Framework")
    parser.add_argument("--no-ui", action="store_true", help="Run without UI")
    parser.add_argument("--no-browser", action="store_true", help="Don't open browser automatically")
    parser.add_argument("--auto-install", action="store_true", help="Automatically install missing dependencies without asking")
    parser.add_argument("--host", default="localhost", help="Host to bind the web server to")
    parser.add_argument("--port", type=int, default=8080, help="Port for the web server")
    parser.add_argument("--websocket-port", type=int, default=8765, help="Port for the WebSocket server")
    parser.add_argument("--skip-onboarding", action="store_true", help="Skip the onboarding process")
    parser.add_argument("--add-mcp-server", action="store_true", help="Add a new MCP server")
    parser.add_argument("--add-local-mcp", action="store_true", help="Install and add a local MCP server")
    parser.add_argument("--onboard", action="store_true", help="Run the onboarding process")
    parser.add_argument("--voice", action="store_true", help="Enable voice assistant")
    parser.add_argument("--wake-word", default="exo", help="Wake word for voice assistant")
    parser.add_argument("--app-mode", action="store_true", help="Launch browser in app mode (standalone window)")
    parser.add_argument("--simulate-voice", action="store_true", help="Use simulated voice commands (for testing)")
    parser.add_argument("--direct-mic", action="store_true", help="Use direct microphone access instead of web-based voice input")
    parser.add_argument("--electron", action="store_true", help="Use Electron UI instead of web UI")
    parser.add_argument("--no-electron", action="store_true", help="Disable Electron UI even if available")
    args = parser.parse_args()

    # If running in a container, use 0.0.0.0 as the host to allow external connections
    if is_running_in_container() and args.host == "localhost":
        print("\nDetected container environment. Binding to all interfaces (0.0.0.0).")
        args.host = "0.0.0.0"

    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Start the Python backend
    print("Starting exo Multi-Agent Framework...")
    backend_cmd = [sys.executable, "-m", "exo.main"]

    # Add command line arguments
    if args.no_ui:
        backend_cmd.append("--no-ui")
    if args.no_browser:
        backend_cmd.append("--no-browser")
    if args.host != "localhost":
        backend_cmd.extend(["--host", args.host])
    if args.port != 8080:
        backend_cmd.extend(["--port", str(args.port)])
    if args.websocket_port != 8765:
        backend_cmd.extend(["--websocket-port", str(args.websocket_port)])
    if args.skip_onboarding:
        backend_cmd.append("--skip-onboarding")
    if args.add_mcp_server:
        backend_cmd.append("--add-mcp-server")
    if args.add_local_mcp:
        backend_cmd.append("--add-local-mcp")
    if args.onboard:
        backend_cmd.append("--onboard")
    if args.voice:
        backend_cmd.append("--voice")
        if args.wake_word != "exo":
            backend_cmd.extend(["--wake-word", args.wake_word])
        if args.simulate_voice:
            backend_cmd.append("--simulate-voice")
        if args.direct_mic:
            backend_cmd.append("--direct-mic")

    if args.app_mode:
        backend_cmd.append("--app-mode")

    if args.electron:
        backend_cmd.append("--electron")

    if args.no_electron:
        backend_cmd.append("--no-electron")

    # Start the backend process
    backend_process = subprocess.Popen(
        backend_cmd,
        cwd=current_dir
    )

    # If running in a container, print the access URL
    if is_running_in_container() and not args.no_ui:
        print(f"\nWeb UI will be available at: http://<container-host>:{args.port}")
        print(f"If you're using port forwarding, access the UI at: http://localhost:{args.port}")
        print("\nNote: The browser will not automatically open in container environments.")
        print("You'll need to manually open the URL in your browser.\n")

    try:
        # Wait for the process to complete
        if backend_process:
            backend_process.wait()
    except KeyboardInterrupt:
        print("Shutting down exo...")
        if backend_process:
            backend_process.terminate()

    print("exo shutdown complete")

if __name__ == "__main__":
    main()
