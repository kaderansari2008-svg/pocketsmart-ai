#!/usr/bin/env python3
"""
PocketSmart AI: Primary VS Code Entrypoint & Demo Runner
Usage:
    python3 main.py              # Starts server & auto-opens browser
    python3 main.py 8080         # Runs on specific port
    python3 main.py --no-browser # Runs without opening browser
"""

import os
import sys

# Ensure backend directory is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(BASE_DIR, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from server import run, PORT

if __name__ == "__main__":
    target_port = PORT
    auto_open = True

    for arg in sys.argv[1:]:
        if arg.isdigit():
            target_port = int(arg)
        elif arg in ("--no-browser", "-n"):
            auto_open = False
        elif arg.startswith("--port="):
            target_port = int(arg.split("=")[1])

    run(target_port, open_browser=auto_open)
