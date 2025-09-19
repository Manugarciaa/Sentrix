#!/usr/bin/env python3
"""
Script to run the FastAPI development server for Sentrix backend
"""

import uvicorn
import os
import sys
from pathlib import Path

def main():
    """Run the FastAPI development server"""

    # Ensure we're in the correct directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)

    print("Iniciando Sentrix FastAPI Backend")
    print(f"Working directory: {backend_dir}")
    print("Server will be available at: http://localhost:8000")
    print("API docs will be available at: http://localhost:8000/docs")
    print("API redoc will be available at: http://localhost:8000/redoc")
    print("\n" + "="*50)

    try:
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            reload_dirs=["app"],
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"\nServer failed to start: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()