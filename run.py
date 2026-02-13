#!/usr/bin/env python3
"""Standalone entry point for OpenClaw Skills Hub."""

import sys
import os

# Add the package to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from openclaw_skills_hub.cli.main import main

if __name__ == "__main__":
    sys.exit(main())
