"""
Entry point for the Vision-HID-Bridge Control Node.

This script initializes the MCP server and starts the main event loop.
It delegates the actual server implementation to `server.py`.

Usage:
    python -m control_node.src.main
"""

try:
    from .server import run
except ImportError:
    from server import run

if __name__ == "__main__":
    run()
