"""
Script de verificación manual de rate limiting
Verifica que el código esté correctamente configurado
"""

import re

def check_file(filepath, checks):
    """Verifica que un archivo contenga ciertos patrones"""
    print(f"\n[CHECKING] {filepath}")
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

# Verificaciones para analyses.py
analyses_checks = {
    "Import limiter": r"from.*middleware\.rate_limit import limiter",
    "Limiter always enabled": r"# SECURITY: Rate limiting always enabled",
    "Authenticated endpoint rate limit": r"@limiter\.limit\(['\"]10/minute['\"]\)",
    "Public endpoint rate limit": r"@limiter\.limit\(['\"]3/minute['\"]\)",
    "Request parameter in authenticated": r"async def create_analysis\(\s*request: Request",
    "Request parameter in public": r"async def create_public_analysis\(\s*request: Request",
    "File validation in authenticated": r"await validate_uploaded_image",
    "File validation in public": r"await validate_uploaded_image",
    "No RATE_LIMITING_ENABLED conditional": r"if RATE_LIMITING_ENABLED:" # Should NOT exist
}

# Verificaciones para app.py
app_checks = {
    "Rate limiting setup": r"from src\.middleware\.rate_limit import setup_rate_limiting",
    "Limiter configured": r"limiter = setup_rate_limiting\(app\)",
    "Success message": r"\[OK\] Rate limiting configured"
}

# Verificaciones para rate_limit.py
middleware_checks = {
    "Limiter import": r"from slowapi import Limiter",
    "Get remote address": r"from slowapi\.util import get_remote_address",
    "Limiter instance": r"limiter = Limiter\(key_func=get_remote_address\)",
    "Setup function": r"def setup_rate_limiting\(app\)"
}

print("=" * 60)
print("VERIFICACION DE RATE LIMITING P1.2")
print("=" * 60)

# Verificar analyses.py
analyses_ok = check_file(
    "src/api/v1/analyses.py",
    {k: v for k, v in analyses_checks.items() if k != "No RATE_LIMITING_ENABLED conditional"}
)

# Verificar que NO existe el código condicional
with open("src/api/v1/analyses.py", 'r', encoding='utf-8') as f:
    content = f.read()
    if "if RATE_LIMITING_ENABLED:" in content:
        print("  [ERROR] Código condicional todavía existe (debería haberse eliminado)")
        analyses_ok = False
    elif "RATE_LIMITING_ENABLED" in content:
        print("  [ERROR] Variable RATE_LIMITING_ENABLED todavía existe")
        analyses_ok = False
    else:
        print("  [OK] Código condicional eliminado correctamente")

# Verificar app.py
app_ok = check_file("app.py", app_checks)

# Verificar middleware
middleware_ok = check_file("src/middleware/rate_limit.py", middleware_checks)

# Resultado final
print("\n" + "=" * 60)
print("RESULTADO DE VERIFICACION")
print("=" * 60)

results = {
    "analyses.py": analyses_ok,
    "app.py": app_ok,
    "rate_limit.py": middleware_ok
}

all_ok = all(results.values())

for file, ok in results.items():
    status = "[OK]" if ok else "[ERROR]"
    print(f"{status} {file}")

print("=" * 60)

if all_ok:
    print("[OK] TODAS LAS VERIFICACIONES PASARON")
    print("[OK] Rate limiting está correctamente configurado")
    exit(0)
else:
    print("[ERROR] ALGUNAS VERIFICACIONES FALLARON")
    print("[ERROR] Revisar los archivos marcados con error")
    exit(1)
