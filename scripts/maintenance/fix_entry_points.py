#!/usr/bin/env python3
"""
Fix entry points that need absolute imports instead of relative imports
"""

import os
import re

def fix_entry_point_files():
    """Fix specific entry point files that should use absolute imports"""

    entry_points = [
        r"C:\Users\manolo\Documents\Sentrix\yolo-service\scripts\batch_detection.py",
        r"C:\Users\manolo\Documents\Sentrix\yolo-service\scripts\predict_new_images.py",
        r"C:\Users\manolo\Documents\Sentrix\yolo-service\scripts\train_dengue_model.py"
    ]

    # Pattern to convert relative imports back to absolute for entry points
    patterns = [
        (r'from \.\.core', r'from src.core'),
        (r'from \.\.reports', r'from src.reports'),
        (r'from \.\.utils', r'from src.utils'),
        (r'import \.\.core', r'import src.core'),
        (r'import \.\.reports', r'import src.reports'),
        (r'import \.\.utils', r'import src.utils'),
    ]

    fixes_applied = 0

    for filepath in entry_points:
        if not os.path.exists(filepath):
            print(f"File not found: {filepath}")
            continue

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
                print(f"Fixed entry point: {filepath}")
                fixes_applied += 1

        except Exception as e:
            print(f"Error processing {filepath}: {e}")

    return fixes_applied

if __name__ == "__main__":
    print("Fixing entry point files...")
    fixes = fix_entry_point_files()
    print(f"Applied {fixes} fixes")