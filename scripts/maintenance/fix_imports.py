#!/usr/bin/env python3
"""
Script para corregir imports problemáticos en el backend
"""

import os
import re

def fix_imports_in_file(filepath):
    """Fix problematic imports in a single file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content

        # Fix common import patterns
        # Replace relative src imports with proper relative imports
        content = re.sub(r'from src\.(\w+)', r'from ..\1', content)
        content = re.sub(r'from utils\.(\w+)', r'from ..utils.\1', content)
        content = re.sub(r'from core\.(\w+)', r'from ..core.\1', content)
        content = re.sub(r'from schemas\.(\w+)', r'from ..schemas.\1', content)
        content = re.sub(r'from services\.(\w+)', r'from ..services.\1', content)
        content = re.sub(r'from database\.(\w+)', r'from ..database.\1', content)

        # Fix specific problematic patterns
        content = re.sub(r'from config import', r'from ...config import', content)

        # If content changed, write it back
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Fixed imports in: {filepath}")
            return True
        return False

    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return False

def main():
    backend_src = r"C:\Users\manolo\Documents\Sentrix\backend\src"

    fixed_count = 0
    total_files = 0

    # Walk through all Python files
    for root, dirs, files in os.walk(backend_src):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                total_files += 1
                if fix_imports_in_file(filepath):
                    fixed_count += 1

    print(f"\nProcessed {total_files} files, fixed {fixed_count} files")

if __name__ == "__main__":
    main()