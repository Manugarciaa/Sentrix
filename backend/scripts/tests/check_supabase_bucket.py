"""
Script para verificar y configurar el bucket de Supabase Storage
"""
import os
import sys
from pathlib import Path

# Cargar variables de entorno desde .env en la raíz del proyecto
from dotenv import load_dotenv

# Buscar .env en la raíz del proyecto (un nivel arriba de backend)
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

print(f"Cargando .env desde: {env_path}")
print(f"Archivo existe: {env_path.exists()}\n")

# Importar después de cargar .env
from supabase import create_client

# Obtener credenciales
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

print("=== CONFIGURACIÓN DE SUPABASE ===")
print(f"URL: {SUPABASE_URL}")
print(f"Service Key: {'***' + SUPABASE_SERVICE_KEY[-20:] if SUPABASE_SERVICE_KEY else 'NO CONFIGURADO'}")
print()

if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    print("ERROR: SUPABASE_URL o SUPABASE_SERVICE_ROLE_KEY no están configurados")
    sys.exit(1)

try:
    # Crear cliente de Supabase
    supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    print("OK - Cliente de Supabase creado correctamente")

    # Listar buckets
    print("\n=== BUCKETS DE STORAGE ===")
    buckets = supabase.storage.list_buckets()

    if not buckets:
        print("No se encontraron buckets")
    else:
        for bucket in buckets:
            print(f"\nBucket: {bucket.name}")
            print(f"  - ID: {bucket.id}")
            print(f"  - Publico: {bucket.public}")
            print(f"  - Creado: {bucket.created_at}")

    # Verificar bucket 'images' específicamente
    print("\n=== VERIFICACIÓN BUCKET 'images' ===")
    images_bucket = next((b for b in buckets if b.name == 'images'), None)

    if images_bucket:
        print("OK - Bucket 'images' existe")
        is_public = images_bucket.public
        print(f"  - Es público: {is_public}")

        if not is_public:
            print("\n  ADVERTENCIA: El bucket NO es público")
            print("  Las imágenes no serán accesibles públicamente")
            print("  Debes configurarlo como público en Supabase Dashboard")
            print("  O ejecutar: supabase.storage.update_bucket('images', {'public': True})")

        # Intentar listar archivos en el bucket
        try:
            files = supabase.storage.from_('images').list()
            print(f"  - Archivos en bucket: {len(files)}")
            if len(files) > 0:
                print(f"  - Primeros 3 archivos:")
                for file in files[:3]:
                    print(f"    * {file.get('name') if isinstance(file, dict) else file.name}")
        except Exception as e:
            print(f"  ERROR listando archivos: {str(e)}")

    else:
        print("ERROR - Bucket 'images' NO existe")
        print("\nDebes crear el bucket 'images' en Supabase Dashboard:")
        print("1. Ve a Storage en Supabase")
        print("2. Crea un nuevo bucket llamado 'images'")
        print("3. Marca la opción 'Public bucket'")

    # Test de upload
    print("\n=== TEST DE UPLOAD ===")
    if images_bucket:
        try:
            # Crear un archivo de test pequeño
            test_data = b"Test image data"
            test_filename = "test_upload.txt"

            result = supabase.storage.from_('images').upload(
                test_filename,
                test_data,
                {"content-type": "text/plain"}
            )

            print(f"OK - Upload de prueba exitoso")

            # Obtener URL pública
            public_url = supabase.storage.from_('images').get_public_url(test_filename)
            print(f"URL publica: {public_url}")

            # Limpiar: borrar archivo de test
            try:
                supabase.storage.from_('images').remove([test_filename])
                print("OK - Archivo de prueba eliminado")
            except:
                pass

        except Exception as e:
            print(f"ERROR en upload: {str(e)}")
            print("\nPosibles causas:")
            print("- El bucket no tiene permisos de escritura")
            print("- La SERVICE_ROLE_KEY no es correcta")
            print("- Hay políticas RLS bloqueando el acceso")

    print("\n=== RESUMEN ===")
    print("1. Conexión a Supabase: OK")
    print(f"2. Bucket 'images' existe: {'SI' if images_bucket else 'NO'}")
    if images_bucket:
        print(f"3. Bucket es público: {'SI' if images_bucket.public else 'NO'}")
        print(f"4. Test de upload: Revisar arriba")

except Exception as e:
    print(f"\nERROR CRÍTICO: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
