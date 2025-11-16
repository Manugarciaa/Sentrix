"""
Test para verificar que el backend puede leer las variables de entorno
"""
import os
import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

print("=== TEST DE CONFIGURACION DEL BACKEND ===\n")

# Cargar .env manualmente primero
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

print(f"1. Archivo .env existe: {env_path.exists()}")
print(f"2. Variables de entorno directas:")
print(f"   SUPABASE_URL: {os.getenv('SUPABASE_URL')}")
print(f"   SUPABASE_KEY existe: {'Si' if os.getenv('SUPABASE_KEY') else 'No'}")
print(f"   SUPABASE_SERVICE_ROLE_KEY existe: {'Si' if os.getenv('SUPABASE_SERVICE_ROLE_KEY') else 'No'}")
print(f"   SUPABASE_STORAGE_BUCKET: {os.getenv('SUPABASE_STORAGE_BUCKET', 'No configurado')}")
print(f"   SUPABASE_PROCESSED_BUCKET: {os.getenv('SUPABASE_PROCESSED_BUCKET', 'No configurado')}")

print("\n3. Intentando cargar Settings de Pydantic:")
try:
    from config import get_settings
    settings = get_settings()

    print(f"   Settings cargado: OK")
    print(f"   supabase_url: {settings.supabase_url}")
    print(f"   supabase_key existe: {'Si' if settings.supabase_key else 'No'}")
    print(f"   supabase_service_role_key existe: {'Si' if settings.supabase_service_role_key else 'No'}")
    print(f"   supabase_storage_bucket: {settings.supabase_storage_bucket}")
    print(f"   supabase_processed_bucket: {settings.supabase_processed_bucket}")

except Exception as e:
    print(f"   ERROR: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n4. Intentando crear SupabaseManager:")
try:
    from utils.supabase_client import SupabaseManager

    sm = SupabaseManager()
    print(f"   SupabaseManager creado: OK")
    print(f"   Bucket storage: {sm._settings.supabase_storage_bucket}")
    print(f"   Bucket processed: {sm._settings.supabase_processed_bucket}")

    # Test de upload simple
    print("\n5. Test de upload:")
    test_data = b"Test image content"
    result = sm.upload_image(test_data, "test_image.jpg")

    print(f"   Status: {result.get('status')}")
    if result.get('status') == 'success':
        print(f"   Public URL: {result.get('public_url')}")
        print(f"   File path: {result.get('file_path')}")

        # Limpiar
        try:
            sm.delete_image(result['file_path'])
            print(f"   Limpieza: OK")
        except:
            pass
    else:
        print(f"   Error: {result.get('message')}")

except Exception as e:
    print(f"   ERROR: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n=== FIN DEL TEST ===")
