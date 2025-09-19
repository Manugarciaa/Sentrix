#!/usr/bin/env python3
"""
Script de configuración para entorno de desarrollo
Automatiza la configuración inicial del backend Sentrix
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def imprimir_encabezado(titulo):
    """Imprime encabezado formateado"""
    print(f"\n{'='*60}")
    print(f" {titulo}")
    print('='*60)


def verificar_python():
    """Verifica que Python sea la versión correcta"""
    imprimir_encabezado("VERIFICACIÓN DE PYTHON")

    version = sys.version_info
    print(f"🐍 Python {version.major}.{version.minor}.{version.micro}")

    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print("❌ Se requiere Python 3.9 o superior")
        return False

    print("✅ Versión de Python compatible")
    return True


def verificar_dependencias_sistema():
    """Verifica dependencias del sistema"""
    imprimir_encabezado("VERIFICACIÓN DE DEPENDENCIAS DEL SISTEMA")

    dependencias = {
        "git": "git --version",
        "postgresql": "psql --version",
        "redis": "redis-cli --version"
    }

    todas_disponibles = True

    for nombre, comando in dependencias.items():
        try:
            resultado = subprocess.run(
                comando.split(),
                capture_output=True,
                text=True,
                timeout=10
            )
            if resultado.returncode == 0:
                version = resultado.stdout.strip().split('\n')[0]
                print(f"✅ {nombre}: {version}")
            else:
                print(f"❌ {nombre}: No disponible")
                todas_disponibles = False
        except (subprocess.TimeoutExpired, FileNotFoundError):
            print(f"❌ {nombre}: No encontrado")
            todas_disponibles = False

    if not todas_disponibles:
        print("\n⚠️  Algunas dependencias no están disponibles.")
        print("   PostgreSQL y Redis son opcionales para desarrollo local.")

    return True  # No bloquear por dependencias opcionales


def configurar_entorno_virtual():
    """Crea y configura entorno virtual"""
    imprimir_encabezado("CONFIGURACIÓN DE ENTORNO VIRTUAL")

    venv_path = Path("venv")

    if venv_path.exists():
        respuesta = input("🔄 El entorno virtual ya existe. ¿Recrear? (s/N): ")
        if respuesta.lower() == 's':
            print("🗑️  Eliminando entorno virtual existente...")
            shutil.rmtree(venv_path)
        else:
            print("✅ Usando entorno virtual existente")
            return True

    print("🔨 Creando entorno virtual...")
    try:
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("✅ Entorno virtual creado")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error creando entorno virtual: {e}")
        return False


def instalar_dependencias():
    """Instala dependencias de Python"""
    imprimir_encabezado("INSTALACIÓN DE DEPENDENCIAS")

    # Determinar comando pip según el sistema
    if sys.platform == "win32":
        pip_cmd = ["venv\\Scripts\\pip"]
    else:
        pip_cmd = ["venv/bin/pip"]

    # Actualizar pip
    print("📦 Actualizando pip...")
    try:
        subprocess.run(pip_cmd + ["install", "--upgrade", "pip"], check=True)
        print("✅ pip actualizado")
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Error actualizando pip: {e}")

    # Instalar dependencias principales
    print("📦 Instalando dependencias principales...")
    try:
        subprocess.run(pip_cmd + ["install", "-r", "requirements.txt"], check=True)
        print("✅ Dependencias principales instaladas")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error instalando dependencias: {e}")
        return False

    return True


def configurar_archivo_env():
    """Configura archivo .env"""
    imprimir_encabezado("CONFIGURACIÓN DE VARIABLES DE ENTORNO")

    env_path = Path(".env")
    env_example_path = Path(".env.example")

    if not env_example_path.exists():
        print("❌ Archivo .env.example no encontrado")
        return False

    if env_path.exists():
        respuesta = input("🔄 El archivo .env ya existe. ¿Sobrescribir? (s/N): ")
        if respuesta.lower() != 's':
            print("✅ Manteniendo archivo .env existente")
            return True

    print("📝 Creando archivo .env desde plantilla...")
    try:
        shutil.copy(env_example_path, env_path)
        print("✅ Archivo .env creado")

        print("\n⚠️  IMPORTANTE: Editar .env con valores reales:")
        print("   - DATABASE_URL: URL de PostgreSQL")
        print("   - YOLO_SERVICE_URL: URL del servicio YOLO")
        print("   - SUPABASE_URL y SUPABASE_KEY: Credenciales de Supabase")

        return True
    except Exception as e:
        print(f"❌ Error creando .env: {e}")
        return False


def configurar_base_datos():
    """Configura base de datos inicial"""
    imprimir_encabezado("CONFIGURACIÓN DE BASE DE DATOS")

    # Verificar si Alembic está disponible
    alembic_ini = Path("alembic.ini")
    if not alembic_ini.exists():
        print("❌ Configuración de Alembic no encontrada")
        return False

    respuesta = input("🗄️  ¿Ejecutar migraciones de base de datos? (s/N): ")
    if respuesta.lower() != 's':
        print("⏭️  Saltando configuración de base de datos")
        return True

    # Ejecutar migraciones
    if sys.platform == "win32":
        python_cmd = ["venv\\Scripts\\python"]
    else:
        python_cmd = ["venv/bin/python"]

    print("🔄 Ejecutando migraciones...")
    try:
        subprocess.run(python_cmd + ["run_migrations.py"], check=True)
        print("✅ Migraciones ejecutadas")
        return True
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Error en migraciones (posible si no hay DB): {e}")
        print("   Asegúrate de que PostgreSQL esté corriendo y configurado")
        return True  # No bloquear por esto


def ejecutar_tests():
    """Ejecuta tests para verificar instalación"""
    imprimir_encabezado("VERIFICACIÓN CON TESTS")

    respuesta = input("🧪 ¿Ejecutar tests de verificación? (s/N): ")
    if respuesta.lower() != 's':
        print("⏭️  Saltando tests de verificación")
        return True

    if sys.platform == "win32":
        python_cmd = ["venv\\Scripts\\python"]
    else:
        python_cmd = ["venv/bin/python"]

    print("🧪 Ejecutando tests básicos...")
    try:
        # Ejecutar solo tests que no requieren DB
        subprocess.run(
            python_cmd + ["-m", "pytest", "tests/test_yolo_integration.py", "-v"],
            check=True
        )
        print("✅ Tests básicos pasaron")
        return True
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Algunos tests fallaron: {e}")
        print("   Esto es normal si las dependencias externas no están configuradas")
        return True


def mostrar_instrucciones_finales():
    """Muestra instrucciones para usar el entorno"""
    imprimir_encabezado("¡CONFIGURACIÓN COMPLETADA!")

    print("🎉 El entorno de desarrollo está listo.")
    print("\n📋 Próximos pasos:")

    if sys.platform == "win32":
        print("1. Activar entorno virtual:")
        print("   venv\\Scripts\\activate")
    else:
        print("1. Activar entorno virtual:")
        print("   source venv/bin/activate")

    print("\n2. Editar archivo .env con valores reales")

    print("\n3. Verificar configuración:")
    print("   python scripts/test_yolo_integration.py")

    print("\n4. Iniciar servidor:")
    print("   python run_server.py")

    print("\n5. Abrir documentación API:")
    print("   http://localhost:8000/docs")

    print("\n📚 Comandos útiles:")
    print("   python run_tests.py          # Ejecutar tests")
    print("   python run_migrations.py     # Aplicar migraciones")
    print("   python scripts/database_maintenance.py  # Mantenimiento DB")


def main():
    """Función principal del script"""
    print("🚀 Script de Configuración de Desarrollo - Sentrix Backend")
    print("=" * 60)

    pasos = [
        ("Verificar Python", verificar_python),
        ("Verificar dependencias del sistema", verificar_dependencias_sistema),
        ("Configurar entorno virtual", configurar_entorno_virtual),
        ("Instalar dependencias", instalar_dependencias),
        ("Configurar variables de entorno", configurar_archivo_env),
        ("Configurar base de datos", configurar_base_datos),
        ("Ejecutar tests de verificación", ejecutar_tests)
    ]

    exitosos = 0
    total = len(pasos)

    for nombre, funcion in pasos:
        print(f"\n🔄 {nombre}...")
        try:
            if funcion():
                exitosos += 1
                print(f"✅ {nombre} completado")
            else:
                print(f"❌ {nombre} falló")
                respuesta = input("¿Continuar con el siguiente paso? (s/N): ")
                if respuesta.lower() != 's':
                    break
        except KeyboardInterrupt:
            print(f"\n\n👋 Configuración cancelada en: {nombre}")
            return False
        except Exception as e:
            print(f"❌ Error inesperado en {nombre}: {e}")
            respuesta = input("¿Continuar? (s/N): ")
            if respuesta.lower() != 's':
                break

    # Mostrar resultado final
    print(f"\n📊 Resultado: {exitosos}/{total} pasos completados")

    if exitosos >= total - 1:  # Permitir 1 fallo
        mostrar_instrucciones_finales()
        return True
    else:
        print("⚠️  La configuración no se completó correctamente.")
        print("   Revisar errores y ejecutar nuevamente.")
        return False


if __name__ == "__main__":
    try:
        resultado = main()
        sys.exit(0 if resultado else 1)
    except KeyboardInterrupt:
        print("\n\n👋 Configuración cancelada por el usuario")
        sys.exit(1)