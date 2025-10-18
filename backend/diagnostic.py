#!/usr/bin/env python3
"""
Backend Service System Diagnostic
Diagnóstico del Sistema Backend

Proporciona información sobre conexiones, servicios y estado del backend.
"""

import os
import sys
import asyncio
import psutil
import platform
from datetime import datetime


try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    from src.database.connection import test_connection, get_database_info
    DATABASE_MODULE_AVAILABLE = True
except ImportError:
    DATABASE_MODULE_AVAILABLE = False


def print_header(title):
    """Print section header"""
    print(f"\n{'='*50}")
    print(f" {title}")
    print('='*50)


def get_system_info():
    """Get basic system information"""
    return {
        'platform': platform.system(),
        'python_version': platform.python_version(),
        'cpu_count': psutil.cpu_count(),
        'memory_gb': round(psutil.virtual_memory().total / (1024**3), 2),
        'memory_available_gb': round(psutil.virtual_memory().available / (1024**3), 2),
        'disk_free_gb': round(psutil.disk_usage('.').free / (1024**3), 2),
        'load_average': psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None
    }


def check_environment_variables():
    """Check important environment variables"""
    important_vars = [
        'DATABASE_URL',
        'SUPABASE_URL',
        'SUPABASE_KEY',
        'BACKEND_PORT',
        'YOLO_SERVICE_URL',
        'LOG_LEVEL'
    ]

    env_status = {}
    for var in important_vars:
        value = os.getenv(var)
        env_status[var] = {
            'set': value is not None,
            'value': value[:20] + '...' if value and len(value) > 20 else value
        }

    return env_status


def check_database_connection():
    """Check database connectivity"""
    if not DATABASE_MODULE_AVAILABLE:
        return {
            'available': False,
            'error': 'Database module not available'
        }

    try:
        connected = test_connection()
        if connected:
            db_info = get_database_info()
            return {
                'available': True,
                'connected': True,
                'info': db_info
            }
        else:
            return {
                'available': True,
                'connected': False,
                'error': 'Connection failed'
            }
    except Exception as e:
        return {
            'available': True,
            'connected': False,
            'error': str(e)
        }


def check_yolo_service():
    """Check YOLO service connectivity"""
    if not REQUESTS_AVAILABLE:
        return {'available': False, 'error': 'Requests module not available'}

    yolo_url = os.getenv('YOLO_SERVICE_URL', 'http://localhost:8001')
    try:
        response = requests.get(f"{yolo_url}/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            return {
                'available': True,
                'connected': True,
                'url': yolo_url,
                'health_data': health_data
            }
        else:
            return {
                'available': True,
                'connected': False,
                'url': yolo_url,
                'error': f'HTTP {response.status_code}'
            }
    except requests.exceptions.RequestException as e:
        return {
            'available': True,
            'connected': False,
            'url': yolo_url,
            'error': str(e)
        }


def check_dependencies():
    """Check critical dependencies"""
    deps = {}

    # Core dependencies
    dependencies_to_check = [
        'fastapi',
        'uvicorn',
        'sqlalchemy',
        'pydantic',
        'psycopg2',
        'alembic',
        'python-dotenv',
        'requests',
        'pillow'
    ]

    for dep in dependencies_to_check:
        try:
            module = __import__(dep.replace('-', '_'))
            version = getattr(module, '__version__', 'Unknown')
            deps[dep] = {'available': True, 'version': version}
        except ImportError:
            deps[dep] = {'available': False, 'version': None}

    return deps


def get_port_status():
    """Check if common ports are in use"""
    ports_to_check = [8000, 8001, 3000, 5432]
    port_status = {}

    for port in ports_to_check:
        try:
            connections = [conn for conn in psutil.net_connections()
                         if conn.laddr.port == port and conn.status == 'LISTEN']
            port_status[port] = {
                'in_use': len(connections) > 0,
                'connections': len(connections)
            }
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            port_status[port] = {
                'in_use': 'Unknown',
                'connections': 'Access denied'
            }

    return port_status


def check_file_structure():
    """Check important directories and files"""
    important_paths = [
        'src/',
        'src/api/',
        'src/database/',
        'src/schemas/',
        'src/services/',
        'app.py',
        'main.py',
        'requirements.txt',
        '.env'
    ]

    file_status = {}
    for path in important_paths:
        full_path = os.path.join(os.getcwd(), path)
        file_status[path] = {
            'exists': os.path.exists(full_path),
            'is_dir': os.path.isdir(full_path),
            'size_kb': round(os.path.getsize(full_path) / 1024, 1) if os.path.exists(full_path) and os.path.isfile(full_path) else None
        }

    return file_status


def run_diagnostic():
    """Run complete diagnostic"""
    print_header("BACKEND SERVICE DIAGNOSTIC")

    # System Information
    print_header("System Information")
    sys_info = get_system_info()
    print(f"Platform: {sys_info['platform']}")
    print(f"Python: {sys_info['python_version']}")
    print(f"CPU Cores: {sys_info['cpu_count']}")
    print(f"Memory: {sys_info['memory_available_gb']:.1f} GB available / {sys_info['memory_gb']:.1f} GB total")
    print(f"Free Disk: {sys_info['disk_free_gb']:.1f} GB")
    if sys_info['load_average']:
        print(f"Load Average: {sys_info['load_average']}")

    # Environment Variables
    print_header("Environment Variables")
    env_vars = check_environment_variables()
    for var, status in env_vars.items():
        status_text = "SET" if status['set'] else "NOT SET"
        value_text = f" ({status['value']})" if status['set'] and status['value'] else ""
        print(f"{var}: {status_text}{value_text}")

    # Database Connection
    print_header("Database Connection")
    db_status = check_database_connection()
    if db_status['available']:
        if db_status['connected']:
            print("Database: Connected")
            if 'info' in db_status:
                info = db_status['info']
                print(f"Database URL: {info.get('database_url', 'Unknown')}")
                print(f"Version: {info.get('version', 'Unknown')}")
                print(f"PostGIS: {'Available' if info.get('postgis_available') else 'Not available'}")
        else:
            print(f"Database: Connection failed - {db_status.get('error', 'Unknown error')}")
    else:
        print(f"Database: Module not available - {db_status.get('error', 'Unknown error')}")

    # YOLO Service Connection
    print_header("YOLO Service Connection")
    yolo_status = check_yolo_service()
    if yolo_status['available']:
        if yolo_status['connected']:
            print(f"YOLO Service: Connected ({yolo_status['url']})")
            if 'health_data' in yolo_status:
                health = yolo_status['health_data']
                print(f"Service: {health.get('service', 'Unknown')}")
                print(f"Version: {health.get('version', 'Unknown')}")
                print(f"Model Available: {health.get('model_available', 'Unknown')}")
        else:
            print(f"YOLO Service: Not reachable ({yolo_status['url']})")
            print(f"Error: {yolo_status.get('error', 'Unknown error')}")
    else:
        print(f"YOLO Service: Cannot check - {yolo_status.get('error', 'Unknown error')}")

    # Port Status
    print_header("Port Status")
    ports = get_port_status()
    port_names = {8000: 'Backend', 8001: 'YOLO Service', 3000: 'Frontend', 5432: 'PostgreSQL'}
    for port, status in ports.items():
        name = port_names.get(port, 'Unknown')
        if isinstance(status['in_use'], bool):
            status_text = "In use" if status['in_use'] else "Available"
            print(f"Port {port} ({name}): {status_text}")
        else:
            print(f"Port {port} ({name}): {status['in_use']}")

    # Dependencies
    print_header("Dependencies")
    deps = check_dependencies()
    for dep, info in deps.items():
        status = "OK" if info['available'] else "MISSING"
        version = f" (v{info['version']})" if info['available'] and info['version'] != 'Unknown' else ""
        print(f"{dep}: {status}{version}")

    # File Structure
    print_header("File Structure")
    files = check_file_structure()
    for path, info in files.items():
        status = "EXISTS" if info['exists'] else "MISSING"
        type_info = " (directory)" if info['is_dir'] else f" ({info['size_kb']} KB)" if info['size_kb'] else ""
        print(f"{path}: {status}{type_info}")

    # Summary
    print_header("Summary")

    # Overall health assessment
    critical_issues = []

    if not db_status.get('connected', False):
        critical_issues.append("Database connection")

    if not yolo_status.get('connected', False):
        critical_issues.append("YOLO Service connection")

    core_deps = ['fastapi', 'uvicorn', 'sqlalchemy']
    missing_deps = [dep for dep in core_deps if not deps.get(dep, {}).get('available', False)]
    if missing_deps:
        critical_issues.append(f"Missing dependencies: {', '.join(missing_deps)}")

    if critical_issues:
        print(f"Status: Issues detected")
        print("Critical issues:")
        for issue in critical_issues:
            print(f"  - {issue}")
    else:
        print("Status: All systems operational")

    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    try:
        run_diagnostic()
    except KeyboardInterrupt:
        print("\nDiagnostic interrupted")
    except Exception as e:
        print(f"\nError during diagnostic: {e}")