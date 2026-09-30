#!/usr/bin/env python3
"""
PocketSmart AI alias entrypoint (redirects to main.py)
"""
from main import run, PORT
import sys

if __name__ == "__main__":
    target_port = PORT
    auto_open = True
    for arg in sys.argv[1:]:
        if arg.isdigit():
            target_port = int(arg)
        elif arg in ("--no-browser", "-n"):
            auto_open = False
    run(target_port, open_browser=auto_open)
