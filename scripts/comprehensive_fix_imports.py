#!/usr/bin/env python3
"""
Script comprehensivo para corregir TODOS los errores de importación en el proyecto Sentrix
"""

import os
import re
from pathlib import Path

def fix_imports_comprehensive(root_dir):
    """Fix all import issues across the entire project"""
    fixes_applied = 0
    total_files = 0

    # Patterns to fix
    patterns = [
        # Backend src imports - convert absolute to relative
        (r'from src\.([^.\s]+)', r'from ..\1'),
        (r'import src\.([^.\s]+)', r'import ..\1'),

        # Backend app imports - most should be src imports now
        (r'from app\.main', r'from ..main'),
        (r'from app\.config', r'from ..config'),
        (r'from app\.database', r'from ..database'),
        (r'from app\.api\.([^.\s]+)', r'from ..api.\1'),
        (r'from app\.services\.([^.\s]+)', r'from ..services.\1'),
        (r'from app\.utils\.([^.\s]+)', r'from ..utils.\1'),
        (r'from app\.models\.([^.\s]+)', r'from ..models.\1'),
        (r'from app\.schemas\.([^.\s]+)', r'from ..schemas.\1'),
        (r'from app\.core\.([^.\s]+)', r'from ..core.\1'),

        # Fix malformed imports
        (r'from src\.\.', r'from ..'),
        (r'import src\.\.', r'import ..'),
    ]

    # Walk through all Python files
    for root, dirs, files in os.walk(root_dir):
        # Skip certain directories
        skip_dirs = ['.git', '__pycache__', '.pytest_cache', 'node_modules', '.vscode']
        dirs[:] = [d for d in dirs if d not in skip_dirs]

        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                total_files += 1

                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()

                    original_content = content

                    # Apply all patterns
                    for pattern, replacement in patterns:
                        content = re.sub(pattern, replacement, content)

                    # If content changed, write it back
                    if content != original_content:
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.write(content)
                        print(f"Fixed imports in: {filepath}")
                        fixes_applied += 1

                except Exception as e:
                    print(f"Error processing {filepath}: {e}")

    return fixes_applied, total_files

def fix_specific_files():
    """Fix specific problematic files"""

    # Fix backend app.py - these should be absolute imports since it's the entry point
    app_py_fixes = [
        (r'from src\.api\.v1 import health', r'from ..api.v1 import health'),
        (r'from src\.api\.v1 import analyses', r'from ..api.v1 import analyses'),
        (r'from src\.api\.v1 import auth', r'from ..api.v1 import auth'),
        (r'from src\.api\.v1 import reports', r'from ..api.v1 import reports'),
    ]

    # These are actually correct in app.py since it's the entry point
    print("Backend app.py imports are correct as absolute imports (entry point)")

    # Fix alembic env.py
    alembic_env = r"C:\Users\manolo\Documents\Sentrix\backend\alembic\env.py"
    if os.path.exists(alembic_env):
        try:
            with open(alembic_env, 'r', encoding='utf-8') as f:
                content = f.read()

            original = content
            # Fix alembic imports to use relative imports
            content = re.sub(r'from src\.database\.models\.base import Base',
                           r'import sys\nimport os\nsys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))\nfrom ..database.models.base import Base', content)
            content = re.sub(r'from src\.database\.models\.models import',
                           r'from ..database.models.models import', content)

            if content != original:
                with open(alembic_env, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"Fixed alembic env.py")
        except Exception as e:
            print(f"Error fixing alembic env.py: {e}")

def main():
    """Main function"""
    print("Iniciando correccion comprehensiva de importaciones...")

    # Fix the entire project
    project_root = r"C:\Users\manolo\Documents\Sentrix"
    fixes_applied, total_files = fix_imports_comprehensive(project_root)

    print(f"\nResumen:")
    print(f"   Archivos procesados: {total_files}")
    print(f"   Archivos corregidos: {fixes_applied}")

    # Fix specific files that need special treatment
    print("\nAplicando correcciones especificas...")
    fix_specific_files()

    print("\nCorreccion de importaciones completada!")

if __name__ == "__main__":
    main()