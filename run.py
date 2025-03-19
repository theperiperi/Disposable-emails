#!/usr/bin/env python3
import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.launcher import main

if __name__ == "__main__":
    main() 