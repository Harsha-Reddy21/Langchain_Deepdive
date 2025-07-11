#!/usr/bin/env python3
"""
Smart Code Tutor Frontend Startup Script
"""

import subprocess
import sys
import os

def main():
    print("🎨 Starting Smart Code Tutor Frontend...")
    print("📦 Installing dependencies...")
    
    # Check if node_modules exists
    if not os.path.exists("node_modules"):
        print("📥 Installing npm dependencies...")
        try:
            subprocess.run(["npm", "install"], check=True)
            print("✅ Dependencies installed successfully!")
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies")
            sys.exit(1)
        except FileNotFoundError:
            print("❌ Node.js/npm not found. Please install Node.js first.")
            sys.exit(1)
    
    print("🚀 Starting development server...")
    print("🌐 Frontend will be available at: http://localhost:3000")
    print("=" * 50)
    
    try:
        # Start the React development server
        subprocess.run(["npm", "start"], check=True)
    except subprocess.CalledProcessError:
        print("❌ Failed to start frontend server")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Frontend server stopped")

if __name__ == "__main__":
    main() 