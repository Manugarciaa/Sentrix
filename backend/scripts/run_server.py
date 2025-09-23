#!/usr/bin/env python3
"""
Script to run the FastAPI development server for Sentrix backend
"""

import uvicorn
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    """Run the FastAPI development server"""

    # Get configuration from environment variables
    host = os.getenv("BACKEND_HOST", "0.0.0.0")
    port = int(os.getenv("BACKEND_PORT", "8000"))
    debug = os.getenv("DEBUG", "true").lower() == "true"
    reload = os.getenv("RELOAD_ON_CHANGE", "true").lower() == "true"
    log_level = os.getenv("LOG_LEVEL", "info").lower()

    # Ensure we're in the correct directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)

    print("Iniciando Sentrix FastAPI Backend")
    print(f"Working directory: {backend_dir}")
    print(f"Configuration - Host: {host}, Port: {port}, Debug: {debug}")
    print(f"Server will be available at: http://localhost:{port}")
    print(f"API docs will be available at: http://localhost:{port}/docs")
    print(f"API redoc will be available at: http://localhost:{port}/redoc")
    print("\n" + "="*50)

    try:
        uvicorn.run(
            "app.main:app",
            host=host,
            port=port,
            reload=reload,
            reload_dirs=["app"],
            log_level=log_level
        )
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"\nServer failed to start: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()