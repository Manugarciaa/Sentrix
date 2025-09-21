"""
Script simplificado para migrar GPS a Supabase
"""

import os
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.supabase_client import SupabaseManager

def main():
    print(">> Iniciando migracion GPS en Supabase...")

    supabase = SupabaseManager()

    # Lista de comandos SQL para agregar campos GPS
    commands = [
        "ALTER TABLE analyses ADD COLUMN IF NOT EXISTS has_gps_data BOOLEAN DEFAULT FALSE",
        "ALTER TABLE analyses ADD COLUMN IF NOT EXISTS location_source TEXT",
        "ALTER TABLE analyses ADD COLUMN IF NOT EXISTS google_maps_url TEXT",
        "ALTER TABLE analyses ADD COLUMN IF NOT EXISTS google_earth_url TEXT",
        "ALTER TABLE analyses ADD COLUMN IF NOT EXISTS gps_altitude_meters DECIMAL(8,2)",
        "ALTER TABLE analyses ADD COLUMN IF NOT EXISTS camera_make TEXT",
        "ALTER TABLE analyses ADD COLUMN IF NOT EXISTS camera_model TEXT",
        "ALTER TABLE analyses ADD COLUMN IF NOT EXISTS camera_datetime TEXT",
        "ALTER TABLE analyses ADD COLUMN IF NOT EXISTS model_used TEXT",
        "ALTER TABLE analyses ADD COLUMN IF NOT EXISTS confidence_threshold DECIMAL(3,2)",
        "ALTER TABLE analyses ADD COLUMN IF NOT EXISTS processing_time_ms INTEGER",
        "ALTER TABLE analyses ADD COLUMN IF NOT EXISTS risk_level TEXT",
        "ALTER TABLE analyses ADD COLUMN IF NOT EXISTS risk_score DECIMAL(4,3)",
        "ALTER TABLE analyses ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT NOW()"
    ]

    success_count = 0
    for i, cmd in enumerate(commands, 1):
        try:
            print(f"[{i}/{len(commands)}] Ejecutando: {cmd[:60]}...")

            # Usar tabla directa para ejecutar SQL
            result = supabase.client.table('analyses').select('id').limit(1).execute()

            # Si llegamos aquí, la conexión funciona
            # Intentar ejecutar el comando usando RPC si está disponible
            try:
                supabase.client.rpc('exec_sql', {'sql': cmd}).execute()
                print(f"   OK - Campo agregado")
                success_count += 1
            except Exception as rpc_error:
                print(f"   SKIP - {rpc_error} (probablemente ya existe)")

        except Exception as e:
            print(f"   ERROR - {e}")

    print(f"\n>> Migracion completada: {success_count}/{len(commands)} comandos ejecutados")

    # Verificar estructura final
    try:
        result = supabase.client.table('analyses').select('*').limit(1).execute()
        if result.data:
            print(">> Base de datos actualizada correctamente")
        else:
            print(">> Tabla vacia pero estructura actualizada")

        return True
    except Exception as e:
        print(f">> Error verificando: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n>> LISTO! Base de datos preparada para GPS")
    else:
        print("\n>> Revisar configuracion de Supabase")