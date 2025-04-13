"""
Filesystem MCP Server for file system access and operations.
"""

import argparse
import json
import logging
import os
import sys
from typing import Dict, List, Any, Optional
from flask import Flask, request, jsonify

logger = logging.getLogger(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

app = Flask(__name__)

@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "ok"})

@app.route("/list", methods=["POST"])
def list_files():
    """List files in a directory."""
    data = request.json
    path = data.get("path", ".")
    
    try:
        # Expand user directory if needed
        if path.startswith("~"):
            path = os.path.expanduser(path)
        
        # Get absolute path
        path = os.path.abspath(path)
        
        # Check if path exists
        if not os.path.exists(path):
            return jsonify({"error": f"Path does not exist: {path}"}), 404
        
        # Check if path is a directory
        if not os.path.isdir(path):
            return jsonify({"error": f"Path is not a directory: {path}"}), 400
        
        # List files and directories
        items = []
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            item_type = "directory" if os.path.isdir(item_path) else "file"
            items.append({
                "name": item,
                "type": item_type,
                "size": os.path.getsize(item_path) if os.path.isfile(item_path) else None,
                "modified": os.path.getmtime(item_path)
            })
        
        return jsonify({
            "path": path,
            "items": items
        })
    except Exception as e:
        logger.error(f"Error listing files: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/read", methods=["POST"])
def read_file():
    """Read a file."""
    data = request.json
    path = data.get("path")
    
    if not path:
        return jsonify({"error": "Path is required"}), 400
    
    try:
        # Expand user directory if needed
        if path.startswith("~"):
            path = os.path.expanduser(path)
        
        # Get absolute path
        path = os.path.abspath(path)
        
        # Check if path exists
        if not os.path.exists(path):
            return jsonify({"error": f"File does not exist: {path}"}), 404
        
        # Check if path is a file
        if not os.path.isfile(path):
            return jsonify({"error": f"Path is not a file: {path}"}), 400
        
        # Read file
        with open(path, "r") as f:
            content = f.read()
        
        return jsonify({
            "path": path,
            "content": content
        })
    except Exception as e:
        logger.error(f"Error reading file: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/write", methods=["POST"])
def write_file():
    """Write to a file."""
    data = request.json
    path = data.get("path")
    content = data.get("content")
    
    if not path:
        return jsonify({"error": "Path is required"}), 400
    
    if content is None:
        return jsonify({"error": "Content is required"}), 400
    
    try:
        # Expand user directory if needed
        if path.startswith("~"):
            path = os.path.expanduser(path)
        
        # Get absolute path
        path = os.path.abspath(path)
        
        # Create directory if it doesn't exist
        directory = os.path.dirname(path)
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        # Write file
        with open(path, "w") as f:
            f.write(content)
        
        return jsonify({
            "path": path,
            "success": True
        })
    except Exception as e:
        logger.error(f"Error writing file: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/delete", methods=["POST"])
def delete_file():
    """Delete a file or directory."""
    data = request.json
    path = data.get("path")
    recursive = data.get("recursive", False)
    
    if not path:
        return jsonify({"error": "Path is required"}), 400
    
    try:
        # Expand user directory if needed
        if path.startswith("~"):
            path = os.path.expanduser(path)
        
        # Get absolute path
        path = os.path.abspath(path)
        
        # Check if path exists
        if not os.path.exists(path):
            return jsonify({"error": f"Path does not exist: {path}"}), 404
        
        # Delete file or directory
        if os.path.isfile(path):
            os.remove(path)
        elif os.path.isdir(path):
            if recursive:
                import shutil
                shutil.rmtree(path)
            else:
                os.rmdir(path)
        
        return jsonify({
            "path": path,
            "success": True
        })
    except Exception as e:
        logger.error(f"Error deleting file: {e}")
        return jsonify({"error": str(e)}), 500

def main():
    """Main entry point for the filesystem MCP server."""
    parser = argparse.ArgumentParser(description="Filesystem MCP Server")
    parser.add_argument("--host", default="localhost", help="Host to bind the server to")
    parser.add_argument("--port", type=int, default=8090, help="Port for the server")
    args = parser.parse_args()
    
    logger.info(f"Starting Filesystem MCP Server on {args.host}:{args.port}")
    app.run(host=args.host, port=args.port)

if __name__ == "__main__":
    main()
