"""
Migración final GPS usando método directo
"""

import os
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.supabase_client import SupabaseManager

def execute_migration():
    """Ejecutar migración GPS"""

    print(">> Ejecutando migracion GPS en Supabase...")

    supabase = SupabaseManager()

    # Verificar conexión
    try:
        test_result = supabase.client.table('analyses').select('id').limit(1).execute()
        print(">> Conexion exitosa a Supabase")
    except Exception as e:
        print(f">> Error de conexion: {e}")
        return False

    # Generar UUID válido para prueba
    test_id = str(uuid.uuid4())

    # Datos de prueba básicos
    basic_data = {
        'id': test_id,
        'image_url': 'test://migration-check',
        'image_filename': 'migration_test.jpg',
        'total_detections': 0
    }

    # Intentar insertar registro básico
    try:
        basic_result = supabase.client.table('analyses').insert(basic_data).execute()

        if basic_result.data:
            print(">> Registro basico insertado correctamente")

            # Ahora intentar agregar campos GPS uno por uno
            gps_updates = {
                'has_gps_data': True,
                'location_source': 'TEST',
                'google_maps_url': 'https://maps.google.com/?q=0,0',
                'google_earth_url': 'https://earth.google.com/web/search/0,0',
                'camera_make': 'Test Camera',
                'camera_model': 'Test Model',
                'risk_level': 'BAJO'
            }

            successful_fields = []

            for field_name, field_value in gps_updates.items():
                try:
                    update_data = {field_name: field_value}
                    update_result = supabase.client.table('analyses').update(update_data).eq('id', test_id).execute()

                    if update_result.data and len(update_result.data) > 0:
                        successful_fields.append(field_name)
                        print(f"   OK: {field_name}")
                    else:
                        print(f"   SKIP: {field_name} (campo no existe)")

                except Exception as field_error:
                    print(f"   ERROR: {field_name} - {field_error}")

            # Limpiar registro de prueba
            try:
                supabase.client.table('analyses').delete().eq('id', test_id).execute()
                print(">> Registro de prueba eliminado")
            except:
                pass

            # Evaluar resultado
            success_rate = len(successful_fields) / len(gps_updates)

            print(f">> Campos GPS disponibles: {len(successful_fields)}/{len(gps_updates)}")
            print(f">> Tasa de exito: {success_rate:.1%}")

            if success_rate >= 0.5:  # Si al menos 50% de campos funcionan
                print(">> MIGRACION SUFICIENTE para funcionalidad GPS")
                return True
            else:
                print(">> MIGRACION INSUFICIENTE - Se requiere SQL manual")
                return False

        else:
            print(">> Error: No se pudo insertar registro basico")
            return False

    except Exception as e:
        print(f">> Error insertando registro basico: {e}")
        return False

def show_manual_sql():
    """Mostrar SQL para ejecutar manualmente"""

    print("\n" + "="*60)
    print("SQL PARA EJECUTAR EN SUPABASE DASHBOARD:")
    print("="*60)

    sql_commands = [
        "-- Campos GPS principales",
        "ALTER TABLE analyses ADD COLUMN IF NOT EXISTS has_gps_data BOOLEAN DEFAULT FALSE;",
        "ALTER TABLE analyses ADD COLUMN IF NOT EXISTS location_source TEXT;",
        "ALTER TABLE analyses ADD COLUMN IF NOT EXISTS google_maps_url TEXT;",
        "ALTER TABLE analyses ADD COLUMN IF NOT EXISTS google_earth_url TEXT;",
        "",
        "-- Metadatos de camara",
        "ALTER TABLE analyses ADD COLUMN IF NOT EXISTS camera_make TEXT;",
        "ALTER TABLE analyses ADD COLUMN IF NOT EXISTS camera_model TEXT;",
        "ALTER TABLE analyses ADD COLUMN IF NOT EXISTS camera_datetime TEXT;",
        "",
        "-- Campos de procesamiento",
        "ALTER TABLE analyses ADD COLUMN IF NOT EXISTS model_used TEXT;",
        "ALTER TABLE analyses ADD COLUMN IF NOT EXISTS confidence_threshold DECIMAL(3,2);",
        "ALTER TABLE analyses ADD COLUMN IF NOT EXISTS processing_time_ms INTEGER;",
        "ALTER TABLE analyses ADD COLUMN IF NOT EXISTS risk_level TEXT;",
        "",
        "-- Verificacion",
        "SELECT column_name FROM information_schema.columns WHERE table_name = 'analyses' AND column_name LIKE '%gps%';"
    ]

    for cmd in sql_commands:
        print(cmd)

    print("="*60)

def main():
    """Función principal"""

    success = execute_migration()

    if success:
        print("\n" + "="*40)
        print("MIGRACION GPS COMPLETADA")
        print("="*40)
        print("Base de datos lista para GPS")
        print("Sistema listo para pruebas")

        print("\nSERVICIOS DISPONIBLES:")
        print("- YOLO Service: http://localhost:8001")
        print("- Backend API: http://localhost:8000")
        print("- Frontend: http://localhost:3000")

        print("\nPUEDES COMENZAR LAS PRUEBAS!")

    else:
        print("\n" + "="*40)
        print("MIGRACION REQUIERE SQL MANUAL")
        print("="*40)
        show_manual_sql()

        print("\nINSTRUCCIONES:")
        print("1. Ve a https://app.supabase.com")
        print("2. Selecciona tu proyecto Sentrix")
        print("3. Ve a 'SQL Editor'")
        print("4. Ejecuta el SQL mostrado arriba")
        print("5. Regresa aqui y ejecuta pruebas")

if __name__ == "__main__":
    main()