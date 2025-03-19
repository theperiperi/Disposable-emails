import sys
import os
import argparse

# Add the src directory to Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from src.main import main as cli_main
from src.web.app import start_web

def main():
    parser = argparse.ArgumentParser(description='Disposable Email Client')
    parser.add_argument('--web', action='store_true', help='Start web interface')
    parser.add_argument('--port', type=int, default=5000, help='Port for web interface')
    args = parser.parse_args()

    try:
        if args.web:
            print(f"Starting web interface on http://localhost:{args.port}")
            print("Press Ctrl+C to exit")
            start_web()
        else:
            cli_main()
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)

if __name__ == "__main__":
    main() 