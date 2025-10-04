#!/usr/bin/env python3
"""Script to run the refactored Online Bookstore application."""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app_refactored import app
from config import ConfigManager

if __name__ == "__main__":
    config = ConfigManager.load_config()
    
    print("🚀 Starting Refactored Online Bookstore Application")
    print("=" * 50)
    print(f"📱 Host: {config.host}")
    print(f"🔌 Port: {config.port}")
    print(f"🐛 Debug: {config.debug}")
    print(f"🔐 Secret Key: {'*' * len(config.security.secret_key)}")
    print("=" * 50)
    print("🌐 Application will be available at:")
    print(f"   http://{config.host}:{config.port}")
    print("=" * 50)
    print("📚 Demo Account:")
    print("   Email: demo@bookstore.com")
    print("   Password: demo123")
    print("=" * 50)
    print("🛑 Press Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        app.run(
            debug=config.debug,
            host=config.host,
            port=config.port
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        sys.exit(1)
