#!/usr/bin/env python3
"""
Environment Configuration Diagnostic Tool
Checks if .env is being loaded correctly
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

print("=" * 70)
print("SENTRIX BACKEND - ENVIRONMENT DIAGNOSTIC")
print("=" * 70)

# 1. Check current working directory
print(f"\n1. Current working directory: {os.getcwd()}")

# 2. Check for .env files
project_root = Path(__file__).parent.parent
env_file = project_root / ".env"
env_example = project_root / ".env.example"

print(f"\n2. Environment files:")
print(f"   - Project root: {project_root}")
print(f"   - .env file: {env_file}")
print(f"   - .env exists: {'[OK] YES' if env_file.exists() else '[X] NO'}")
print(f"   - .env.example exists: {'[OK] YES' if env_example.exists() else '[X] NO'}")

# 3. Load .env file
print(f"\n3. Loading .env file...")
loaded = load_dotenv(env_file)
print(f"   - Loaded successfully: {'[OK] YES' if loaded else '[X] NO'}")

# 4. Check critical environment variables
print(f"\n4. Critical environment variables:")
critical_vars = [
    "ENVIRONMENT",
    "DEBUG",
    "SECRET_KEY",
    "JWT_SECRET_KEY",
    "DATABASE_URL",
    "BACKEND_PORT",
    "YOLO_SERVICE_URL",
    "REDIS_URL",
]

for var in critical_vars:
    value = os.getenv(var)
    if value:
        # Mask secrets
        if "SECRET" in var or "PASSWORD" in var:
            display_value = f"{value[:8]}...{value[-4:]}" if len(value) > 12 else "***"
        else:
            display_value = value
        print(f"   [OK] {var} = {display_value}")
    else:
        print(f"   [X] {var} = NOT SET")

# 5. Try to import and load config
print(f"\n5. Testing configuration import:")
try:
    sys.path.insert(0, str(project_root / "backend"))
    from src.config import get_settings, PROJECT_ROOT, ENV_FILE

    print(f"   [OK] Config module imported successfully")
    print(f"   - Config PROJECT_ROOT: {PROJECT_ROOT}")
    print(f"   - Config ENV_FILE: {ENV_FILE}")
    print(f"   - Config ENV_FILE exists: {'[OK] YES' if ENV_FILE.exists() else '[X] NO'}")

    settings = get_settings()
    print(f"   [OK] Settings loaded successfully")
    print(f"   - Environment: {settings.environment}")
    print(f"   - Debug: {settings.debug}")
    print(f"   - Backend port: {settings.backend_port}")
    print(f"   - Database: {settings.database_url}")

except Exception as e:
    print(f"   [X] Error loading config: {e}")
    import traceback
    traceback.print_exc()

# 6. Test app import
print(f"\n6. Testing app import:")
try:
    os.chdir(project_root / "backend")
    import app
    print(f"   [OK] App module imported successfully")
except Exception as e:
    print(f"   [X] Error importing app: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("DIAGNOSTIC COMPLETE")
print("=" * 70)
print("\nIf all checks passed, the backend should start normally with:")
print("  cd backend && python app.py")
print("\nOr using uvicorn directly:")
print("  cd backend && uvicorn app:app --reload --host 0.0.0.0 --port 8000")
print("=" * 70)
