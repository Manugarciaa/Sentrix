#!/usr/bin/env python3
"""
Clean problematic Unicode characters from Python files
Limpiar caracteres Unicode problemáticos de archivos Python
"""

import os
import re
from pathlib import Path

def clean_unicode_chars(file_path):
    """Clean Unicode characters from a file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content

        # Replace problematic Unicode characters with text equivalents
        replacements = {
            'ERROR:': 'ERROR:',
            'OK:': 'OK:',
            'WARNING:': 'WARNING:',
            'FILE:': 'FILE:',
            'TOOL:': 'TOOL:',
            'ALERT:': 'ALERT:',
            'DATA:': 'DATA:',
            'TAG:': 'TAG:',
            'CHART:': 'CHART:',
            'LOCATION:': 'LOCATION:',
            'LINK:': 'LINK:',
            'TARGET:': 'TARGET:',
            'TOOLS:': 'TOOLS:',
            'FOLDER:': 'FOLDER:',
            'PACKAGE:': 'PACKAGE:',
            'LAUNCH:': 'LAUNCH:',
            'NOTES:': 'NOTES:',
            'BUILD:': 'BUILD:'
        }

        for unicode_char, replacement in replacements.items():
            content = content.replace(unicode_char, replacement)

        # Only write if content changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Cleaned: {file_path}")
            return True

        return False

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def clean_project():
    """Clean all Python files in the project"""
    backend_dir = Path(__file__).parent.parent
    python_files = list(backend_dir.rglob("*.py"))

    cleaned_count = 0

    for py_file in python_files:
        # Skip cache directories
        if '__pycache__' in str(py_file) or '.pytest_cache' in str(py_file):
            continue

        if clean_unicode_chars(py_file):
            cleaned_count += 1

    print(f"\nProcessed {len(python_files)} Python files")
    print(f"Cleaned {cleaned_count} files")
    print("All problematic Unicode characters have been replaced with ASCII equivalents")

if __name__ == "__main__":
    print("Cleaning Unicode characters from Python files...")
    clean_project()