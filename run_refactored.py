#!/usr/bin/env python
"""
Run script for the refactored Online Bookstore Flask application.

This script starts the Flask web server with appropriate configuration
for development or production environments.
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import the Flask app
from app_refactored import app

if __name__ == "__main__":
    # Get configuration from environment
    host = os.environ.get("FLASK_HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_ENV", "production") != "production"
    
    print("=" * 80)
    print("  Online Bookstore - Flask Application")
    print("=" * 80)
    print(f"  Environment: {os.environ.get('FLASK_ENV', 'production')}")
    print(f"  Host: {host}")
    print(f"  Port: {port}")
    print(f"  Debug: {debug}")
    print("=" * 80)
    print()
    
    # Run the Flask app
    try:
        app.run(host=host, port=port, debug=debug)
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        sys.exit(1)

