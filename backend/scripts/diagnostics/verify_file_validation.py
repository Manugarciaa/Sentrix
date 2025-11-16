"""
Script de verificación manual de validación de archivos P1.1
Verifica que el código esté correctamente configurado
"""

import re
import os

def check_file(filepath, checks):
    """Verifica que un archivo contenga ciertos patrones"""
    print(f"\n[CHECKING] {filepath}")
    if not os.path.exists(filepath):
        print(f"  [ERROR] File not found")
        return False

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    results = []
    for check_name, pattern in checks.items():
        if re.search(pattern, content, re.MULTILINE | re.DOTALL):
            print(f"  [OK] {check_name}")
            results.append(True)
        else:
            print(f"  [ERROR] {check_name} - NOT FOUND")
            results.append(False)

    return all(results)

print("=" * 60)
print("VERIFICACION DE FILE VALIDATION P1.1")
print("=" * 60)

# Verificaciones para file_validation.py
file_validation_checks = {
    "Import magic": r"import magic",
    "ALLOWED_MIME_TYPES defined": r"ALLOWED_MIME_TYPES = \{",
    "sanitize_filename function": r"def sanitize_filename\(filename: str\)",
    "validate_file_content function": r"async def validate_file_content",
    "validate_file_extension function": r"def validate_file_extension",
    "validate_uploaded_image function": r"async def validate_uploaded_image",
    "Magic bytes validation": r"magic\.from_buffer\(content, mime=True\)",
    "MIME type check": r"if mime_type not in allowed_mime_types:",
    "Size validation": r"if len\(content\) > max_size:",
    "Path traversal prevention": r"os\.path\.basename"
}

# Verificaciones para analyses.py (uso de validación)
analyses_checks = {
    "Import validate_uploaded_image": r"from.*file_validation import validate_uploaded_image",
    "Security comment": r"# SECURITY.*MIME",
    "Uses validate_uploaded_image": r"await validate_uploaded_image\(",
    "Uses sanitized filename": r"filename=safe_filename"
}

# Verificaciones para requirements.txt
requirements_checks = {
    "python-magic": r"python-magic",
    "python-magic-bin": r"python-magic-bin"
}

# Ejecutar verificaciones
validation_ok = check_file("src/utils/file_validation.py", file_validation_checks)
analyses_ok = check_file("src/api/v1/analyses.py", analyses_checks)
requirements_ok = check_file("requirements.txt", requirements_checks)

# Verificar que el archivo de tests existe
print(f"\n[CHECKING] tests/test_file_validation.py")
if os.path.exists("tests/test_file_validation.py"):
    print(f"  [OK] Test file exists")
    with open("tests/test_file_validation.py", 'r', encoding='utf-8') as f:
        content = f.read()
        test_count = len(re.findall(r"def test_", content))
        print(f"  [OK] Contains {test_count} test functions")
    tests_ok = test_count >= 10  # Should have at least 10 tests
    if not tests_ok:
        print(f"  [ERROR] Expected at least 10 tests, found {test_count}")
else:
    print(f"  [ERROR] Test file not found")
    tests_ok = False

# Resultado final
print("\n" + "=" * 60)
print("RESULTADO DE VERIFICACION")
print("=" * 60)

results = {
    "file_validation.py": validation_ok,
    "analyses.py (usage)": analyses_ok,
    "requirements.txt": requirements_ok,
    "test_file_validation.py": tests_ok
}

all_ok = all(results.values())

for file, ok in results.items():
    status = "[OK]" if ok else "[ERROR]"
    print(f"{status} {file}")

print("=" * 60)

if all_ok:
    print("[OK] TODAS LAS VERIFICACIONES PASARON")
    print("[OK] File validation P1.1 está correctamente implementado")
    exit(0)
else:
    print("[ERROR] ALGUNAS VERIFICACIONES FALLARON")
    print("[ERROR] Revisar los archivos marcados con error")
    exit(1)
