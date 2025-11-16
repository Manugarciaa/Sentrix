#!/usr/bin/env python3
"""
Sentrix Environment Setup Script
Configures environment variables and validates system configuration
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path


def print_header(title):
    print(f"\n{'='*60}")
    print(f" {title}")
    print('='*60)


def print_success(message):
    print(f"✓ {message}")


def print_warning(message):
    print(f"[WARN] {message}")


def print_error(message):
    print(f"X {message}")


def copy_env_file():
    """Copy .env.example to .env if it doesn't exist"""
    print_header("Environment Configuration")

    root_dir = Path(__file__).parent.parent
    env_example = root_dir / ".env.example"
    env_file = root_dir / ".env"

    if env_file.exists():
        print_warning(f".env file already exists at {env_file}")
        return True

    if not env_example.exists():
        print_error(f".env.example file not found at {env_example}")
        return False

    try:
        shutil.copy2(env_example, env_file)
        print_success(f"Created .env file from template at {env_file}")
        print("[NOTE] Please edit .env file with your specific configuration values")
        return True
    except Exception as e:
        print_error(f"Failed to copy .env file: {e}")
        return False


def validate_environment():
    """Validate critical environment variables"""
    print_header("Environment Validation")

    # Load .env file
    from dotenv import load_dotenv
    load_dotenv()

    required_vars = [
        ("DATABASE_URL", "Database connection string"),
        ("SECRET_KEY", "Application secret key"),
        ("JWT_SECRET_KEY", "JWT secret key"),
    ]

    optional_vars = [
        ("SUPABASE_URL", "Supabase project URL"),
        ("SUPABASE_KEY", "Supabase anonymous key"),
        ("GOOGLE_MAPS_API_KEY", "Google Maps API key"),
    ]

    all_valid = True

    print("Required Variables:")
    for var_name, description in required_vars:
        value = os.getenv(var_name)
        if value and value != f"your_{var_name.lower()}":
            print_success(f"{var_name}: {description}")
        else:
            print_error(f"{var_name}: {description} - NOT SET")
            all_valid = False

    print("\nOptional Variables:")
    for var_name, description in optional_vars:
        value = os.getenv(var_name)
        if value and not value.startswith("your_"):
            print_success(f"{var_name}: {description}")
        else:
            print_warning(f"{var_name}: {description} - not configured")

    return all_valid


def check_ports():
    """Check if configured ports are available"""
    print_header("Port Availability Check")

    from dotenv import load_dotenv
    load_dotenv()

    ports_to_check = [
        (int(os.getenv("BACKEND_PORT", "8000")), "Backend API"),
        (int(os.getenv("YOLO_SERVICE_PORT", "8001")), "YOLO Service"),
        (int(os.getenv("FRONTEND_PORT", "3000")), "Frontend"),
    ]

    all_available = True

    for port, service in ports_to_check:
        if is_port_available(port):
            print_success(f"Port {port} available for {service}")
        else:
            print_warning(f"Port {port} already in use - {service} may conflict")
            all_available = False

    return all_available


def is_port_available(port):
    """Check if a port is available"""
    import socket

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        result = sock.connect_ex(('localhost', port))
        return result != 0


def check_dependencies():
    """Check if required Python packages are installed"""
    print_header("Dependency Check")

    required_packages = [
        "fastapi",
        "uvicorn",
        "sqlalchemy",
        "alembic",
        "pydantic",
        "python-dotenv",
        "ultralytics",
        "pillow",
        "numpy",
    ]

    missing_packages = []

    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print_success(f"{package}")
        except ImportError:
            print_error(f"{package} - NOT INSTALLED")
            missing_packages.append(package)

    if missing_packages:
        print(f"\n[PACKAGE] Install missing packages with:")
        print(f"pip install {' '.join(missing_packages)}")
        return False

    return True


def create_directories():
    """Create necessary directories"""
    print_header("Directory Setup")

    from dotenv import load_dotenv
    load_dotenv()

    directories = [
        os.getenv("UPLOAD_DIRECTORY", "./uploads"),
        os.getenv("TEMP_DIRECTORY", "./temp"),
        "./logs",
        "./backend/logs",
        "./yolo-service/logs",
        "./shared/logs",
    ]

    for directory in directories:
        dir_path = Path(directory)
        try:
            dir_path.mkdir(parents=True, exist_ok=True)
            print_success(f"Directory: {directory}")
        except Exception as e:
            print_error(f"Failed to create {directory}: {e}")
            return False

    return True


def generate_secrets():
    """Generate secure secrets if defaults are being used"""
    print_header("Security Setup")

    env_file = Path(".env")
    if not env_file.exists():
        print_error(".env file not found. Run copy_env_file() first.")
        return False

    import secrets

    # Read current .env content
    with open(env_file, 'r') as f:
        content = f.read()

    # Generate new secrets if defaults are detected
    if "your-super-secret-key" in content:
        new_secret = secrets.token_urlsafe(32)
        content = content.replace("your-super-secret-key-change-in-production", new_secret)
        print_success("Generated new SECRET_KEY")

    if "your-jwt-secret-key" in content:
        new_jwt_secret = secrets.token_urlsafe(32)
        content = content.replace("your-jwt-secret-key-change-in-production", new_jwt_secret)
        print_success("Generated new JWT_SECRET_KEY")

    # Write updated content back
    with open(env_file, 'w') as f:
        f.write(content)

    print_success("Security configuration updated")
    return True


def main():
    """Main setup function"""
    print_header("Sentrix Environment Setup")
    print("This script will configure your Sentrix development environment")

    steps = [
        ("Copy environment template", copy_env_file),
        ("Generate security secrets", generate_secrets),
        ("Create directories", create_directories),
        ("Check dependencies", check_dependencies),
        ("Validate environment", validate_environment),
        ("Check port availability", check_ports),
    ]

    success_count = 0

    for step_name, step_function in steps:
        print(f"\n[PROCESSING] {step_name}...")
        try:
            if step_function():
                success_count += 1
            else:
                print_warning(f"{step_name} completed with warnings")
        except Exception as e:
            print_error(f"{step_name} failed: {e}")

    print_header("Setup Summary")
    print(f"✓ {success_count}/{len(steps)} steps completed successfully")

    if success_count == len(steps):
        print_success("[SUCCESS] Environment setup complete!")
        print("\n[INFO] Next steps:")
        print("1. Edit .env file with your specific configuration")
        print("2. Start the backend: cd backend && python scripts/run_server.py")
        print("3. Start YOLO service: cd yolo-service && python server.py")
        print("4. Access API documentation at http://localhost:8000/docs")
    else:
        print_warning("[WARN] Setup completed with some issues. Check the output above.")
        print("[TIP] You may need to manually configure some settings.")


if __name__ == "__main__":
    main()